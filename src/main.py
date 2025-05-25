from src.FileOperations import save_json_to_file, resumefileToText , load_schema_file
from src.llm_invoker import parse_file_to_json
import os
if __name__ == '__main__':
    pdfPath="C:\\Users\\Abhinav\\Downloads\\resume (4).docx"
    pdfText = resumefileToText(pdfPath)
    structured_data = parse_file_to_json(pdfText)
    save_json_to_file(structured_data)
    print(structured_data)



