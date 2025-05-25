import json

from openai import OpenAI


client = OpenAI(api_key="sk-dd26dc9fa4094176bc06ee35bbcd1272",base_url="https://api.deepseek.com")

def parse_pdf_to_json(text, schema_instruction):
    messages = [
        {"role": "system", "content": schema_instruction},
        {"role": "user", "content": text}
    ]

    # response = client.chat.completions.create(
    #     model="deepseek-chat",
    #     messages=messages,
    #     stream=False
    # )
    #
    # content = response.choices[0].message.content
    content = '```json\n{\n  "resume_analysis": {\n    "structured_resume": {\n      "personal_information": {\n        "name": "Harsha Vardhan Yellela",\n        "email": "harsha.yellela@gmail.com",\n        "phone": "+1-248-497-9965",\n        "location": "Ferndale, Michigan - 48220",\n        "socials": [\n          {\n            "name": "LinkedIn",\n            "link": "N/A"\n          }\n        ]\n      },\n      "education": [\n        {\n          "institution": "Lawrence Technological University",\n          "degree": "Master\'s of Science in Computer Science",\n          "location": "Southfield, Michigan",\n          "start_date": "N/A",\n          "end_date": "January 2026",\n          "gpa": "3.6",\n          "gpa_out_off": "4"\n        }\n      ],\n      "skills": [\n        {\n          "name": "Technical Skills",\n          "data": [\n            "Languages: Python, C++, Java, JavaScript, SQL"\n          ]\n        }\n      ],\n      "extracurricular_achievements": [\n        {\n          "name": "Winners of Microsoft x MLH Hackathon (for creating chatbot) Project",\n          "type": "N/A",\n          "location": "N/A",\n          "date": "January 2022",\n          "description": "Built an emergency assistant chatbot using NLP and rule-based logic; demonstrated at MLH Hackathon, winning top project."\n        }\n      ]\n    },\n    "job_description_analysis": {\n      "job_title": "N/A",\n      "company": "N/A",\n      "location": "N/A",\n      "employment_type": "N/A",\n      "remote_status": "N/A",\n      "required_skills_and_tools": [],\n      "preferred_qualifications": [],\n      "responsibilities": [],\n      "experience_level": "N/A",\n      "education_requirements": [],\n      "benefits": [],\n      "how_to_apply": "N/A"\n    },\n    "match_analysis": {\n      "matching_skills": [],\n      "missing_skills": [],\n      "suggested_keywords": [],\n      "role_alignment_score": 0\n    },\n    "optimized_resume": "Harsha Vardhan Yellela\nFerndale, Michigan - 48220\nharsha.yellela@gmail.com | +1-248-497-9965\n\nEDUCATION\nMaster\'s of Science in Computer Science\nLawrence Technological University, Southfield, Michigan\nExpected Graduation: January 2026 | GPA: 3.6/4.0\n\nTECHNICAL SKILLS\nLanguages: Python, C++, Java, JavaScript, SQL\n\nACHIEVEMENTS\nWinners of Microsoft x MLH Hackathon (for creating chatbot) Project\nJanuary 2022\nBuilt an emergency assistant chatbot using NLP and rule-based logic; demonstrated at MLH Hackathon, winning top project."\n  }\n}\n```'
    if content.startswith("```json"):
        content = content.removeprefix("```json").removesuffix("```").strip()
    elif content.startswith("```"):
        content = content.removeprefix("```").removesuffix("```").strip()

    try:
        parsed_json = json.loads(content)
        return parsed_json
    except json.JSONDecodeError as e:
        print("❌ Failed to parse JSON. Here's the raw content:\n", content)
        raise e





