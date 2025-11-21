# Analyzers

This folder contains two analysis scripts used to download npm packages, inspect their JavaScript source across versions, and export per-file time-series metrics useful for research and detection experiments.

Overview
- `BST_analyzer.py` (blank-space-ratio analyzer)
	- Purpose: compute simple per-file metrics related to whitespace and formatting (blank space count/ratio and maximum line length) across package versions.
	- Output: for each package a pair of CSV files named `blank_space_ratio.csv` and `blank_space_max_line_length.csv` with rows = file paths and columns = package versions.
	- Use case: detect sudden large additions of long single-line payloads or unusual whitespace patterns that can indicate obfuscated or injected code.

- `HUT_analyzer.py` (homoglyph-unicode analysis)
	- Purpose: scan JS files for suspicious Unicode usage: invisible/control BiDi characters and homoglyph characters that can be used for typosquatting or source-level obfuscation.
	- Output: `homoglyph_count.csv`, `invisible_count.csv`, and `total_chars.csv` per package with the same rows/columns layout (file × version).
	- Use case: discover packages or versions that introduce homoglyphs or invisible characters which may indicate supply-chain manipulation or malicious obfuscation.

## How the scripts work
1. Read a package list JSON (`most_popular_packs_22_10_25.json`) using a streaming parser (`ijson`) to avoid loading the whole file in memory (it could be large).
2. For each package, fetch metadata from the npm registry and download all available version tarballs.
3. Extract each version into a temporary directory and recursively search for files with the configured extension (default: `.js`).
4. Analyze each file with a per-file analyzer class (`BlankSpaceAnalyzer` or `UnicodeAnalyzer`). The analyzer returns a small metrics object and optionally an error.
5. Aggregate per-version metrics into pandas DataFrames and export CSV reports under the configured `OUTPUT_DIR`.
6. Mark packages as processed in a log file so runs can be resumed.

### Configuration variables (edit at top of each script)
- `PACKAGE_FILE` — path to the JSON list of package names.
- `DOWNLOAD_DIR` — temporary download/extract folder used per package.
- `OUTPUT_DIR` — location where CSV results are saved (one folder per package).
- `LOG_FILE` — processed packages log to allow resuming runs.
- `ANALYSIS_EXTENSION` — file extension to analyze (default `js`).
- `MAX_PROCESSES` — number of parallel worker processes used to analyze files.
- `PAUSE_BETWEEN_PACKAGES` / `PAUSE_BETWEEN_VERSIONS` — polite delays to reduce pressure on the npm registry.

## Requirements
- Python 3.8+ recommended
- File `most_popular_packs_22_10_25.json` containing the list of package names to analyze (obv, you can change the name).
- Required Python packages (install with pip):
	- `requests`
	- `pandas`
	- `ijson`
	- `confusables` (only required for `HUT_analyzer.py`)

Suggest: use a virtual environment to avoid dependency conflicts and install packages with the requirements.txt file:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## How to run
- Run `BST_analyzer.py` (BlankSpace analysis):
```xonsh
cd ITASEC26-source-attack-metrics/scripts
python BST_analyzer.py
```

- Run `HUT_analyzer.py` (Unicode/HUT analysis):
```xonsh
cd ITASEC26-source-attack-metrics/scripts
python HUT_analyzer.py
```

## Notes on running safely and politely
- These scripts download many packages and versions from the public npm registry. Be mindful of bandwidth and rate limits. Use `PAUSE_BETWEEN_PACKAGES` and `PAUSE_BETWEEN_VERSIONS` to throttle activity.
- Use a workspace with sufficient disk space; downloads can be large if many packages/versions are processed.
- If you want to run a limited test, modify `most_popular_packs_22_10_25.json` to include a few package names or edit the script to stop after N packages.
- The scripts create per-package temporary directories under `DOWNLOAD_DIR`. These directories are removed after processing, but if a run is interrupted partial data may remain — check and clean manually if needed.

## Resuming and logs
- Each script writes a `processed*.log` file (configurable via `LOG_FILE`) with the names of packages already processed; this allows safe resumption across runs.
- Per-package logs are also written under each package's output directory (`log.log`) to aid debugging.

## Output structure
- `OUTPUT_DIR`/
	- `package_name_escaped`/
		- CSV reports (e.g. `blank_space_ratio.csv`)
		- `log.log` (per-package processing log)

## Extending or customizing
- To add new analyzers, implement a subclass of `BaseAnalyzer` with `analyze_file` and `_export_to_csv` methods.
- You can change `ANALYSIS_EXTENSION` to analyze other file types (e.g., `ts`) or adapt the file discovery patterns.

## Support and contributions
If you need help running the scripts or want to suggest improvements, open an issue in the parent repository or send a pull request with tests/examples.

