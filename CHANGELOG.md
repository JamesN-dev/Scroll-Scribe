## v0.4.0 (2025-06-24)

### Feat

- **discover**: implement CSV and JSON discover command outputs with rich CSV & JSON metadata for ML ingestion
- integrate URL display consistency and CLI validation
- output order list tests passing, update fast_discovery and cli

## v0.3.1 (2025-06-24)

### Fix

- move save_links_to_file from discovery.py to fast_discovery.py and update imports

### Refactor

- ran tests and fixed error handling - fixed hardcoded magic numbers and created constants.py - updated hardcoded ai model to only change in .env - removed duplicated url cleaning logic - created a consistent timeout value throughout - added input validation for url, file path model name and timeout validation - updated README.md

## v0.3.0 (2025-06-23)

### Feat

- add RichHelpFormatter and example usage to CLI help output
- **cli**: improve UX with persistent progress bar
- New script simple_link_extractor.py will scrape all links on a doc or index site and output into a .txt file, which scrollscribe is designed to then scrape those files. updated README.md. moved .py files into app/ and renamed main.py to scrollscribe.py
- Add sequential scrape delay and README for ScrollScribe

### Refactor

- refactor logging/ui, add features, improve robustness, simplify
