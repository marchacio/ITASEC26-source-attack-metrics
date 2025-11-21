# Dataset

This folder contains package lists and small example datasets used by the analyzers in this repository. It includes the original popularity snapshot used to drive large-scale runs, plus a small, local test dataset with both unobfuscated and obfuscated variants for fast experiments.

## Overview of contents
- `most_popular_packs_22_10_25.json` — a snapshot (2025-10-22) of popular npm packages sourced from the `npm-rank` project (https://github.com/tristan-f-r/npm-rank). Use this file for larger, real-world runs.
- `mini_manipulated_bst_dataset/` — a compact dataset intended for testing and demonstrations. It contains two variants:
	- `not_obfuscated_payload/` — a set of packages manipulated using the non-obfuscated RATatouille payload.
	- `obfuscated_payload/` — the same set of examples but with the real-obfuscated RATatouille payload.
- `npm_most_popular/` — dataset of analyzed packages using the `most_popular_packs_22_10_25.json` snapshot.
	- `most_popular_packs_22_10_25.json`
	- `BST/` and `HUT/` — output directories produced by the `BST_analyzer.py` and `HUT_analyzer.py` scripts respectively.

## Usage guidance
- Quick local test: point the analyzer scripts to `mini_manipulated_dataset/not_obfuscated_payload` or `mini_manipulated_dataset/obfuscated_payload` (or modify the scripts to read a short package list) to run fast, offline checks without hitting the npm registry.
- Full runs: use `most_popular_packs_22_10_25.json` as `PACKAGE_FILE` in `scripts/*.py` to run large-scale collection and analysis.

## Format notes
- The snapshot `most_popular_packs_22_10_25.json` is a JSON array (or list of objects) with package names and package metadata. The analyzer scripts use a streaming parser (`ijson`) and expect each item to be either a string (package name) or an object containing a `name` field.
- The `mini_manipulated_dataset` directories are structured to mimic the layout that the analysis scripts expect after downloading and extracting package tarballs (package/version/... files). This makes it simple to run the scripts against local test data.

## Safety and reproducibility
- The `obfuscated_payload` examples are intended for research; do not execute unknown payloads on production systems. Prefer static analysis and isolated environments.
- When reproducing experiments, record the snapshot filename and date. The `scripts` write `processed*.log` files so runs can be resumed.

## Attribution
This dataset includes data derived from `npm-rank` and small locally-built manipulated examples created for testing. If you reuse these materials in research, please cite the dataset snapshot date and the source repository.

## Issues or help
If you need help using the datasets or want to contribute improved test cases, open an issue in the parent repository.