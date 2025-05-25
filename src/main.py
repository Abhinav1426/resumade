from src.FileOperations import save_json_to_file, extract_text_from_pdf
from src.llm_invoker import parse_pdf_to_json

if __name__ == '__main__':
    pdfPath="C:\\Users\\Abhinav\\Downloads\\resume (6).pdf"
    pdfText = extract_text_from_pdf(pdfPath)
    structured_data = parse_pdf_to_json(pdfText)
    print(structured_data)
    save_json_to_file(structured_data)



