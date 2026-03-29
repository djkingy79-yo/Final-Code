"""
Criminal Appeal AI - Document Helpers
Shared helpers for document context building and text extraction.
"""
import re
import logging
from typing import List

logger = logging.getLogger(__name__)

MENTION_PATTERN = re.compile(r"@([A-Za-z0-9._-]{2,64})")


def extract_mentions(text: str) -> List[str]:
    if not text:
        return []
    mentions = [m.strip().lower() for m in MENTION_PATTERN.findall(text)]
    return sorted(list(set([m for m in mentions if m])))


def build_document_context(
    documents: List[dict],
    *,
    per_doc_char_limit: int,
    total_char_budget: int,
    include_description: bool = True,
    content_heading: str = "CONTENT"
) -> dict:
    """Build a bounded document context block to keep AI calls responsive."""
    blocks = []
    consumed_chars = 0
    included_docs = 0

    for doc in documents:
        if consumed_chars >= total_char_budget:
            break

        remaining = total_char_budget - consumed_chars
        allowed_chars = min(per_doc_char_limit, remaining)
        content = (doc.get("content_text") or "").strip()
        snippet = content[:allowed_chars] if content else ""
        consumed_chars += len(snippet)
        included_docs += 1

        block = f"--- DOCUMENT: {doc.get('filename')} [{doc.get('category', 'other')}] ---\n"
        if include_description and doc.get("description"):
            block += f"Description: {doc.get('description')}\n"

        if snippet:
            block += f"{content_heading}:\n{snippet}\n"
            if len(content) > len(snippet):
                block += f"[... trimmed {len(content) - len(snippet)} characters for speed ...]\n"
        else:
            block += f"{content_heading}: [No text content extracted]\n"

        blocks.append(block)

    omitted_docs = max(0, len(documents) - included_docs)
    return {
        "text": "\n".join(blocks),
        "included_docs": included_docs,
        "omitted_docs": omitted_docs,
        "consumed_chars": consumed_chars,
    }


def extract_text_with_ocr(file_content: bytes, filename: str, file_type: str) -> tuple:
    """Extract text from images and scanned PDFs using OCR"""
    import io
    import pytesseract
    from PIL import Image

    filename_lower = filename.lower()
    extracted_text = ""
    ocr_used = False

    try:
        if any(filename_lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.webp']):
            image = Image.open(io.BytesIO(file_content))
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            extracted_text = pytesseract.image_to_string(image)
            ocr_used = True
            logger.info(f"OCR extracted {len(extracted_text)} chars from image {filename}")

        elif "pdf" in file_type or filename_lower.endswith('.pdf'):
            try:
                from pypdf import PdfReader
                pdf_reader = PdfReader(io.BytesIO(file_content))
                text_parts = []
                for page in pdf_reader.pages[:30]:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                extracted_text = "\n".join(text_parts)
            except Exception as e:
                logger.warning(f"Regular PDF extraction failed: {e}")

            if len(extracted_text.strip()) < 100:
                try:
                    from pdf2image import convert_from_bytes
                    images = convert_from_bytes(
                        file_content,
                        dpi=200,
                        first_page=1,
                        last_page=min(20, 20)
                    )
                    ocr_parts = []
                    for i, image in enumerate(images):
                        if image.mode in ('RGBA', 'P'):
                            image = image.convert('RGB')
                        page_text = pytesseract.image_to_string(image)
                        if page_text.strip():
                            ocr_parts.append(f"--- Page {i+1} ---\n{page_text}")
                    if ocr_parts:
                        extracted_text = "\n\n".join(ocr_parts)
                        ocr_used = True
                        logger.info(f"OCR extracted {len(extracted_text)} chars from scanned PDF {filename}")
                except Exception as e:
                    logger.warning(f"PDF OCR failed: {e}")

        elif filename_lower.endswith('.docx') or "word" in file_type:
            try:
                from docx import Document as DocxDocument
                docx_doc = DocxDocument(io.BytesIO(file_content))
                text_parts = []
                for para in docx_doc.paragraphs:
                    if para.text.strip():
                        text_parts.append(para.text)
                extracted_text = "\n".join(text_parts)
            except Exception as e:
                logger.warning(f"DOCX extraction failed: {e}")

        elif "text" in file_type or filename_lower.endswith('.txt'):
            extracted_text = file_content.decode('utf-8', errors='ignore')

    except Exception as e:
        logger.error(f"OCR/Text extraction error for {filename}: {e}")

    return extracted_text, ocr_used
