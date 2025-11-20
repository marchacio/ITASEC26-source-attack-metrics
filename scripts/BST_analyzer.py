import requests
import tarfile
import io
import os
import time
import shutil
import pandas as pd
import multiprocessing as mp
import logging
import ijson
from pathlib import Path
from typing import Dict, Optional, Generator

from common.base_analyzer import BaseAnalyzer, FileAnalysisResult, TagAnalysisResult

# --- CONFIGURATION ---
PACKAGE_FILE = Path("most_popular_packs_22_10_25.json") # Input JSON file from npm-rank
DOWNLOAD_DIR = Path("temp")                 # Temporary folder for the current package
OUTPUT_DIR = Path("npm_results")            # Final folder for CSV results
LOG_FILE = "processed.log"                  # File to resume the process
ANALYSIS_EXTENSION = "js"                   # File extension to analyze
MAX_PROCESSES = os.cpu_count() or 1         # Processes for analysis
PAUSE_BETWEEN_PACKAGES = 2                  # Pause in seconds between packages
PAUSE_BETWEEN_VERSIONS = 0.1                # Pause during version downloads

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NPM_Analyzer")

# --- Specific Analyzer Implementation ---
class BlankSpaceAnalyzer(BaseAnalyzer):
    def analyze_file(self, file_path: Path) -> FileAnalysisResult:
        start_time = time.time()
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            blank_spaces = content.count(' ') + content.count('\t') + content.count('\n') + content.count('\r')
            total_chars = len(content)
            lines = content.splitlines()
            max_line_length = max((len(line) for line in lines), default=0)
            ratio = float('inf') if total_chars == 0 else blank_spaces / total_chars
            
            metrics = {"blank_space_ratio": ratio, "max_line_length": max_line_length}
            return FileAnalysisResult(str(file_path), metrics, [], 1.0, time.time() - start_time)
        except Exception as e:
            self.logger.error(f"Error while analyzing file {file_path}: {e}")
            return FileAnalysisResult(str(file_path), {}, [], 0.0, time.time() - start_time, str(e))

    def _export_to_csv(self, results: Dict[str, TagAnalysisResult], output_dir: Path, package_name: str):
        self.logger.info(f"Exporting results for '{package_name}' to CSV...")
        
        ratio_data, max_line_length_data, all_files = {}, {}, set()

        for version_name, version_result in results.items():
            ratio_version_data, max_line_length_version_data = {}, {}
            
            for fr in version_result.file_results:
                # The relative path is computed abstractly, independent of the base folder
                # e.g. /temp/express/1.0.0/index.js -> index.js
                relative_path = os.path.join(*Path(fr.file_path).parts[3:])
                
                all_files.add(relative_path)
                ratio_version_data[relative_path] = fr.metrics.get("blank_space_ratio")
                max_line_length_version_data[relative_path] = fr.metrics.get("max_line_length")
            
            ratio_data[version_name] = ratio_version_data
            max_line_length_data[version_name] = max_line_length_version_data

        if not all_files:
            self.logger.warning("No files analyzed. CSV files will be empty.")
            return

        sorted_files = sorted(list(all_files))
        ratio_df = pd.DataFrame(index=sorted_files)
        max_line_length_df = pd.DataFrame(index=sorted_files)

        for version_name in sorted(results.keys()): 
            ratio_df[version_name] = pd.Series(ratio_data.get(version_name, {})).reindex(sorted_files)
            max_line_length_df[version_name] = pd.Series(max_line_length_data.get(version_name, {})).reindex(sorted_files)

        package_output_dir = output_dir / package_name.replace('/', '_')
        package_output_dir.mkdir(exist_ok=True)
        
        ratio_output_path = package_output_dir / "blank_space_ratio.csv"
        max_line_output_path = package_output_dir / "blank_space_max_line_length.csv"
        
        ratio_df.to_csv(ratio_output_path, na_rep='')
        max_line_length_df.to_csv(max_line_output_path, na_rep='')

        self.logger.info(f"Reports saved in: {package_output_dir.resolve()}")

def stream_packages_from_file(json_file_path: Path) -> Generator[str, None, None]:
    """
    Yields package names one by one from a large JSON list file.
    Uses 'ijson' for memory efficiency.
    """
    logger.info(f"Streaming package names from {json_file_path}...")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            # 'item' iterates over elements in the root-level array
            package_generator = ijson.items(f, 'item')
            for item in package_generator:
                pkg_name = None
                if isinstance(item, dict):
                    pkg_name = item.get("name")
                elif isinstance(item, str):
                    pkg_name = item
                if isinstance(pkg_name, str) and pkg_name.strip():
                    yield pkg_name
                else:
                    logger.debug(f"Skipping invalid package entry: {item}")
    except FileNotFoundError:
        logger.critical(f"FATAL: Package file not found: {json_file_path}")
        return
    except Exception as e:
        logger.critical(f"FATAL: Error reading package file {json_file_path}: {e}")
        return

def download_all_versions(package_name: str, package_dir: Path) -> bool:
    """Download and extract all versions of a package."""
    logger.info(f"Fetching metadata for '{package_name}'...")
    try:
        response = requests.get(f"https://registry.npmjs.org/{package_name}", timeout=20)
        response.raise_for_status()
        metadata = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Unable to fetch metadata for '{package_name}'. Skipping. Details: {e}")
        return False

    versions = metadata.get('versions', {})
    if not versions:
        logger.warning(f"No versions found for '{package_name}'. Skipping.")
        return True
    
    logger.info(f"Found {len(versions)} versions. Starting download into '{package_dir}'...")
    os.makedirs(package_dir, exist_ok=True)

    for version, data in versions.items():
        try:
            tarball_url = data.get('dist', {}).get('tarball')
            if not tarball_url: continue

            version_path = package_dir / version
            if version_path.exists(): continue 

            res = requests.get(tarball_url, timeout=30)
            res.raise_for_status()

            with tarfile.open(fileobj=io.BytesIO(res.content), mode="r:gz") as tar:
                for member in tar.getmembers(): # Extract removing the 'package/' folder
                    parts = Path(member.path).parts
                    if len(parts) > 1:
                        member.path = os.path.join(*parts[1:])
                        tar.extract(member, path=version_path)
            time.sleep(PAUSE_BETWEEN_VERSIONS)
        except Exception as e:
            logger.error(f"  Error on version {version}: {e}")
    return True

def load_processed_packages() -> set:
    if not os.path.exists(LOG_FILE): return set()
    with open(LOG_FILE, 'r') as f: return {line.strip() for line in f}

def mark_package_as_processed(package_name: str):
    with open(LOG_FILE, 'a') as f: f.write(f"{package_name}\n")

# --- MAIN FUNCTION ---
def main():
    """Main function that orchestrates download, analysis and cleanup."""
    processed_packages = load_processed_packages()
    logger.info(f"Found {len(processed_packages)} packages already processed in the log.")

    package_stream = stream_packages_from_file(PACKAGE_FILE)
    packages_processed_this_run = 0

    DOWNLOAD_DIR.mkdir(exist_ok=True)
    
    print(f"\n--- Starting analysis ---")
    print(f"Reading from: {PACKAGE_FILE.resolve()}")
    print(f"Temporary folder: {DOWNLOAD_DIR.resolve()}")
    print(f"Results folder: {OUTPUT_DIR.resolve()}")
    print(f"Processes used: {MAX_PROCESSES}\n")
    
    analyzer = BlankSpaceAnalyzer(max_processes=MAX_PROCESSES)

    for package_name in package_stream:
        
        if package_name in processed_packages:
            continue

        packages_processed_this_run += 1
        
        logger.info(f"\n{'='*50}\n"
                    f"[Package {packages_processed_this_run}] START PACKAGE: {package_name}"
                    f"\n{'='*50}")
        
        sanitized_name = package_name.replace('/', '_')
        package_path = DOWNLOAD_DIR / sanitized_name
        package_output_dir = OUTPUT_DIR / sanitized_name
        package_output_dir.mkdir(parents=True, exist_ok=True)

        file_handler: Optional[logging.Handler] = None
        try:
            log_file_path = package_output_dir / "log.log"
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler)
        except Exception as e:
            logger.error(f"Unable to create log file for '{package_name}': {e}")
        
        try:
            # 1. DOWNLOAD
            success = download_all_versions(package_name, package_path)
            if not success:
                continue 

            # 2. ANALYSIS
            results = analyzer.analyze_package_versions(package_path, ANALYSIS_EXTENSION)
            
            # 3. EXPORT
            if results:
                analyzer.export_results(results, OUTPUT_DIR, package_name)
            else:
                logger.warning(f"No results to export for {package_name}.")

            # 4. MARK AS PROCESSED
            mark_package_as_processed(package_name)

        except Exception as e:
            logger.critical(f"Fatal error while processing {package_name}: {e}", exc_info=True)
        
        finally:
            # 5. CLEANUP
            if package_path.exists():
                logger.info(f"Cleaning temporary folder '{package_path}'...")
                shutil.rmtree(package_path)
                logger.info("Cleanup completed.")
            
            if file_handler is not None:
                try:
                    logging.getLogger().removeHandler(file_handler)
                    file_handler.close()
                except Exception:
                    pass

            logger.info(f"Waiting {PAUSE_BETWEEN_PACKAGES} seconds...")
            time.sleep(PAUSE_BETWEEN_PACKAGES)

    logger.info("\n--- Process completed! ---")

if __name__ == "__main__":
    if os.name != 'posix': # Not a Unix-like system (e.g., Windows)
        mp.set_start_method('spawn', force=True)
    main()