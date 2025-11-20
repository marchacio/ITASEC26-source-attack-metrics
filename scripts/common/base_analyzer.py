from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List
from pathlib import Path
import time
import multiprocessing as mp
import logging

# --- Data Classes (data structures) ---
@dataclass
class FileAnalysisResult:
    file_path: str
    metrics: Dict
    anomalies: List[str]
    confidence_score: float
    processing_time: float
    error: str | None = None

@dataclass
class TagAnalysisResult:
    tag_name: str
    files_analyzed: int
    processing_time: float
    file_results: List[FileAnalysisResult] = field(default_factory=list)

# --- Base Analyzer Class ---
class BaseAnalyzer(ABC):
    def __init__(self, max_processes: int = 1):
        self.max_processes = max_processes
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def analyze_file(self, file_path: Path) -> FileAnalysisResult:
        pass

    def analyze_package_versions(self, package_path: Path, extension: str) -> Dict[str, TagAnalysisResult]:
        versions = sorted([d for d in package_path.iterdir() if d.is_dir()])
        if not versions:
            self.logger.warning(f"No version folders found in '{package_path}'.")
            return {}

        results = {}
        self.logger.info(f"Analyzing {len(versions)} versions for '*.{extension}' in '{package_path.name}'.")

        for i, version_path in enumerate(versions):
            version_name = version_path.name
            self.logger.info(f"-> Analyzing version {version_name} ({i+1}/{len(versions)})...")
            results[version_name] = self._analyze_version(version_path, version_name, extension)
        
        return results

    def _analyze_version(self, version_path: Path, version_name: str, extension: str) -> TagAnalysisResult:
        start_time = time.time()
        files_to_analyze = list(version_path.rglob(f"*.{extension}"))
        
        if not files_to_analyze:
            return TagAnalysisResult(version_name, 0, time.time() - start_time, [])

        if self.max_processes > 1 and len(files_to_analyze) > 1:
            with mp.Pool(processes=self.max_processes) as pool:
                file_results = pool.map(self.analyze_file, files_to_analyze)
        else:
            file_results = [self.analyze_file(f) for f in files_to_analyze]

        valid_results = [r for r in file_results if r.error is None]
        
        return TagAnalysisResult(
            tag_name=version_name,
            files_analyzed=len(valid_results),
            processing_time=time.time() - start_time,
            file_results=valid_results
        )
    
    def export_results(self, results: Dict[str, TagAnalysisResult], output_dir: Path, package_name: str):
        output_dir.mkdir(parents=True, exist_ok=True)
        self._export_to_csv(results, output_dir, package_name)

    @abstractmethod
    def _export_to_csv(self, results: Dict[str, TagAnalysisResult], output_dir: Path, package_name: str):
        pass