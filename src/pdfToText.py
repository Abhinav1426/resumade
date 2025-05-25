import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path):
    atext = ""
    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            # Add plain visible text
            atext += page.get_text().strip() + "\n"

            # Add hyperlinks
            links = page.get_links()
            for link in links:
                if 'uri' in link:
                    uri = link['uri']
                    atext += f"[Link found on Page {page_num}]: {uri}\n"

    return atext.strip()


def clean_text(text):
    return '\n'.join([line.strip() for line in text.splitlines() if line.strip()])

def pdfToText(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    text = clean_text(text)
    return text
