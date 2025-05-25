from src.FileOperations import save_json_to_file, resumefileToText
from src.llm_invoker import parse_file_to_json

if __name__ == '__main__':
    pdfPath="C:\\Users\\Abhinav\\Downloads\\resume (4).pdf"
    pdfText = resumefileToText(pdfPath)
    structured_data = parse_file_to_json(pdfText)
    print(structured_data)
    save_json_to_file(structured_data)



