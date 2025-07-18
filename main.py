# from utils.FileOperations import FileOperations
# from services.ResumeBuilder import ResumeBuilder
# from services.JsonToPDFBuilder import JsonToPDFBuilder
# from utils.WebScraper import WebScraper
import uvicorn
from app import app

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8001)
    # pdfPath="C:\\Users\\Abhinav\\Downloads\\resume (4).docx"
    # file_ops = FileOperations()
    # resume_builder = ResumeBuilder('google')
    # json_to_pdf_builder = JsonToPDFBuilder()
    # web_scraper = WebScraper()
    #
    # # Extract text from the document
    # resume_extracted_text = file_ops.resumefileToText(pdfPath)
    # print("Extracted Text:\n", resume_extracted_text)
    #
    # # Generate JSON from the extracted text
    # resume_json = resume_builder.parse_file_to_json(resume_extracted_text)
    # print("Generated JSON:\n", resume_json)
    #
    # # Save the JSON to a file
    # file_ops.save_json_to_file(resume_json, file_name='resume_data')
    #
    # # Get the job description from the LinkedIn URL
    # job_description = web_scraper.linkedin_scrape_job_details("https://www.linkedin.com/jobs/view/4194296041")
    # print("Job Description:\n", job_description)
    #
    # # Build the resume JSON with the job description
    # resume_json_with_job = resume_builder.build_resume_json(resume_json, job_description['description'])
    # print("Resume JSON with Job Description:\n", resume_json_with_job)
    #
    # # Save the updated JSON to a file
    # file_ops.save_json_to_file(resume_json_with_job, file_name='gen_ai_resume')
    #
    # # Convert the JSON to PDF
    # custom_order = [
    #     'personal_info',
    #     'summary',
    #     'education',
    #     'experiences',
    #     'skills',
    #     'projects',
    #     'languages',
    #     'extras',
    #     'awards',
    #     'certifications',
    # ]
    # resume_json_with_job = file_ops.load_schema_file(file_path='data/sample.json')
    # # bytes = json_to_pdf_builder.build(resume_json_with_job)
    # bytes = json_to_pdf_builder.build(resume_json_with_job, order=custom_order)
    # file_ops.save_pdf_to_file(bytes, file_name='gen_ai_resume')
    # print(f"PDF generated")









