from typing import List

def pdf_to_images(pdf_bytes: bytes, dpi: int = 200) -> List[bytes]:
    """Render every page of a PDF to PNG bytes using PyMuPDF."""
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pages = []
    for page in doc:
        pix = page.get_pixmap(matrix=mat, alpha=False)
        pages.append(pix.tobytes("png"))
    doc.close()
    return pages
