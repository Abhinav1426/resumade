import json
from datetime import datetime

import fitz


def load_schema_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        schema_file_contents = json.load(f)
    return schema_file_contents

def save_json_to_file(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'Extracted_schema_from_pdf_{timestamp}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON saved to {filename}")


def extract_text_from_doc(path):
    atext = ""
    with fitz.open(path) as doc:
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

def resumefileToText(pdf_path):
    text = extract_text_from_doc(pdf_path)
    text = clean_text(text)
    return text