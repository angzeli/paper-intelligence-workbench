# PDF Metadata

v0.7 does not parse PDF full text and does not treat PDF metadata as authoritative.

The local file scanner can detect `.pdf` files, compute SHA256 hashes, record size, and link a PDF path to a registry `paper_id`. It does not:

- download PDFs
- scrape publisher pages
- bypass paywalls
- OCR scanned documents
- extract or summarize full text
- replace user-entered registry metadata

PDF records currently use `extracted_metadata_status=not_extracted_optional_future_work`.

Future metadata extraction may add advisory fields such as title, author, creation date, and page count if a lightweight optional dependency is justified. Any extracted metadata should remain a warning or suggestion, not a source of truth.
