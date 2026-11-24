"""Build both deliverables (PDF and DOCX) into ../deliverables."""
import os
import shutil
import subprocess
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "deliverables"))
os.makedirs(OUT, exist_ok=True)

for script in ("make_figures.py", "build_pdf.py", "build_docx.py"):
    print("running", script)
    subprocess.run([sys.executable, os.path.join(HERE, script)], check=True)

pdf_src = os.path.join(HERE, "build", "TLS-1.3-Technical-Report.pdf")
docx_src = os.path.join(HERE, "build", "TLS-1.3-Technical-Report.docx")

doc = pymupdf.open(pdf_src)
doc.set_metadata({
    "title": "TLS 1.3 Client-Server Channel - Technical Report",
    "subject": "Design, implementation and security evaluation of a "
               "two-process secure messaging prototype",
    "author": "",
    "keywords": "TLS 1.3, Python ssl, handshake, AEAD, certificate, Wireshark",
    "creator": "",
    "producer": "",
})
doc.save(os.path.join(OUT, "TLS-1.3-Technical-Report.pdf"), garbage=4, deflate=True)
shutil.copyfile(docx_src, os.path.join(OUT, "TLS-1.3-Technical-Report.docx"))

check = pymupdf.open(os.path.join(OUT, "TLS-1.3-Technical-Report.pdf"))
print("pages:", check.page_count)
