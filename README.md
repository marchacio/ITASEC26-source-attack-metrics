# ITASEC26 - Source-level attack metrics (research assets)

This repository contains data, tools and example artifacts used for research into source-level attacks, obfuscation and detection. The goal is to provide reproducible datasets and lightweight analyzers so defenders and researchers can study how malicious payloads and suspicious patterns appear across package versions.

## Contents (high level)
- `analyzers/` — analysis scripts that download npm packages, extract versions, analyze source files and export per-file time-series CSV metrics (see `BST_analyzer.py` and `HUT_analyzer.py`).
- `datasets/` — dataset snapshot of analyzed packages in our research.
- `resources/` — example payloads and other small artifacts preserved for reproducible study (includes `ratatouille_payload`).

## Why this repo
This project is the base for [our paper](https://github.com/marchacio/ITASEC26-source-attack-metrics/blob/main/itasec26_source_attack_metrics_paper.pdf) and  supports experiments into how attackers may hide malicious code in source distributions (obfuscation, homoglyphs, invisible characters, monolithic minified payloads) and provides simple detection-ready metrics (blank-space ratios, max line lengths, homoglyph/invisible counts) across historical versions of packages.


## Safety and responsible use
- Some example artifacts in `resources/` are real payloads preserved for research. These files may contain code used by attackers; do NOT execute them on production systems or online environments. See `resources/ratatouille_payload/README.md` for a clear disclaimer and safe-handling instructions.
- The scripts download many packages from the public npm registry. Respect rate limits and use the built-in `PAUSE_*` configuration constants to avoid overloading public services. Run experiments in isolated environments and with consent where required.

## Notes on reproducibility
- The dataset snapshot records the packages used for a run on a given date. To reproduce results, use the same snapshot file and the same versions of the scripts and dependencies.
- The scripts mark processed packages in `processed*.log` so runs can be resumed without repeating work.

## Contributing and citation
If you reuse these datasets or scripts in research, please cite the project and include the snapshot date (for example, the dataset file name). Contributions (issues or pull requests) are welcome — open an issue to discuss changes before large edits.

## Contact
For questions about running the analyses or reproducing experiments, open an issue in this repository.

# References
G. Benedetti, L. Caviglione, G. Lagorio, M. Zoratti, "Software Evolution Metrics for the Detection of Trojan Code in npm Packages", ITASEC - SERICS Joint National Conference on CyberSecurity, Cagliari, Italy, February 2026.

# Acknowledgments
This work was partially supported by Project SERICS (PE00000014) under the NRRP MUR
program funded by the EU - NGEU.
