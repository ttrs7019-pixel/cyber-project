# Technical report build

Two formats of the same report are produced from one content model:

| File | Purpose |
| --- | --- |
| `../deliverables/TLS-1.3-Technical-Report.pdf` | print/submission copy, A4, 8 pages |
| `../deliverables/TLS-1.3-Technical-Report.docx` | editable copy, A4, Word page numbers |

## Rebuild

```bash
python3 -m venv .venv
.venv/bin/pip install reportlab python-docx pymupdf matplotlib fonttools pillow
.venv/bin/python build_all.py
```

`build_all.py` regenerates the figures, renders both documents and copies the
results into `../deliverables/`.

## Layout

- `content.py` – all text, tables and captions (single source of truth)
- `make_figures.py` – figures 1–3, written to `figures/`
- `build_pdf.py` – ReportLab renderer (fonts embedded from `assets/`)
- `build_docx.py` – python-docx renderer (Cambria/Calibri/Consolas)
- `preview_docx.py` – rough paginated preview used to keep the DOCX at 8 pages
- `data/handshake_ms.json` – the 30 handshake samples behind figure 3

The page numbers in the contents list refer to the printed page numbers of the
body (page 1 is the first page of Section 1). `report/build/` is ignored.
