# Resources folder

- **Example Payloads**: `/example_payloads/` contains minimal example JavaScript payloads used for quick testing: `BST_payload.js` and `HUT_payload.js`.
- **Ratatouille Payload**: `/ratatouille_payload/` contains a full Ratatouille payload in both original and obfuscated form: `ratatouille_payload.js` & `ratatouille_payload_obfuscated.js`.

Read the related README files in each folder for more details.

## Notes

- **Obfuscated vs original**: The `ratatouille_payload_obfuscated.js` file is the original obfuscated payload used in real scenarios and `ratatouille_payload.js` is the original unobfuscated payload.
- **Where analyzers live**: Analyzer implementations and helpers are in `scripts/` and `common/` (for example, `scripts/BST_analyzer.py`, `scripts/HUT_analyzer.py`, and `common/base_analyzer.py`).
- **Dataset**: Larger collections of manipulated and obfuscated payloads are available under the `dataset/` folder used in experiments.

## Contact
For questions about these examples or their intended usage, open an issue or contact the repository owner.
