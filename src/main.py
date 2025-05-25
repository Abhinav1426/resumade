import json
from datetime import datetime
from src.llm_invoker import parse_pdf_to_json
from src.pdfToText import extract_text_from_pdf




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

if __name__ == '__main__':
    schema_file_path = "schema.json"
    pdfPath="C:\\Users\\Abhinav\\Downloads\\resume (6).pdf"

    schema_file_contents = load_schema_file(schema_file_path)

    schema_instruction = f"""
    You are a helpful assistant. Extract data from unstructured text and return valid JSON following this schema:

    {json.dumps(schema_file_contents, indent=2)}

    Return only a valid JSON object. Do NOT include markdown, code blocks, or any explanation.
    """
    pdfText = extract_text_from_pdf(pdfPath)
    structured_data = parse_pdf_to_json(pdfText,schema_instruction)
    print(structured_data)
    save_json_to_file(structured_data)



