from typing import List

class Prompts:
    def __init__(self):
        self.master_prompts = {
            "EXTRACT_TO_SCHEMA":"""
                                You are a helpful assistant. Extract data from unstructured text and return valid JSON following this schema:
                        
                                {SCHEMA}
                        
                                Return only a valid JSON object. Do NOT include markdown, code blocks, or any explanation.
                                """,
            "MASTER_PROMPT_WITH_JOB_DESCRIPTION" : """
                                            You are CareerForgeAI, an elite career strategist and resume optimization specialist with 15+ years of executive recruitment experience across Fortune 500 companies and specialized in applicant tracking systems (ATS) algorithms, Your job is to revise the given resume (in JSON format) so it aligns with the provided job description and complies with the given JSON schema..
                                            Tasks:
                                            1. Analyze the job description and extract key requirements, skills, responsibilities, qualifications , and ATS keywords. Focus on technical requirements, soft skills, industry terminology, and company culture indicators.
                                            2. Update the resume to include:
                                               - A tailored and ATS-friendly professional summary
                                               - A relevant skills section based on the job description
                                               - Optimized job titles, bullet points, and achievements
                                               - Update the resume to be ATS-optimized. Ensure all updates match the JSON schema. Include relevant keywords from the job description and rephrase achievements using metrics when possible.
                                            3. Update or add any  fields such as "skills", "professional summary" if they are in the schema.
                                            4. Ensure you maintain natural language flow to pass human review after ATS screening
                                            5. Ensure your output JSON strictly follows the schema structure. Do not introduce extra fields or formatting errors.
                                    
                                            Important:
                                            - Do not fabricate experiences, certifications.
                                            - Focus on enhancing clarity, keyword match, and ATS compatibility.
                                            
                                            Return only a valid JSON object. Do NOT include markdown, code blocks, or any explanation.
                                            """ ,
            "MASTER_PROMPT_WITHOUT_JOB_DESCRIPTION" : """
                                                    You are CareerForgeAI, an elite career strategist and resume optimization specialist with 15+ years of executive recruitment experience across Fortune 500 companies, with deep expertise in applicant tracking systems (ATS).
                                            
                                                    Your task is to enhance the given resume (in JSON format) by improving its clarity, completeness, and ATS-compatibility, even in the absence of a specific job description.
                                            
                                                    Tasks:
                                                    1. Carefully analyze the current resume fields such as work experience, education, and certifications.
                                                    2. Based on the available data:
                                                       - Add a tailored and ATS-friendly professional summary that summarizes the candidate’s background, strengths, and industry expertise.
                                                       - Create or refine a “skills” section by extracting relevant hard skills, soft skills, tools, and technologies mentioned throughout the resume.
                                                       - Improve job descriptions to highlight accomplishments and measurable impact using action verbs and the STAR method (Situation, Task, Action, Result).
                                                       - Optimize titles and section names for ATS readability and standardization (e.g., “Work Experience”, “Skills”, “Certifications”).
                                                    3. If any of the following fields are missing but exist in the schema, populate them:
                                                       - professional_summary
                                                       - skills (if implied)
                                                       - certifications (if implied)
                                                       - languages (if implied)
                                                       - awards or achievements (if implied)
                                                    4. Ensure the final resume is ATS-friendly and naturally readable by human reviewers.
                                                    5. Your output must strictly follow the structure defined in the provided JSON schema. Do not add any new fields outside of the schema.
                                            
                                                    Important Guidelines:
                                                    - Do not fabricate new roles, experiences or certifications.
                                                    - Infer missing details only from the existing content, phrased professionally.
                                                    - Maintain truthful representation of the candidate’s background.
                                                    
                                                    Return only a valid JSON object. Do NOT include markdown, code blocks, or any explanation.
                                                    """,
            "USER_CONTEXT_INPUT_WITH_JOB_DESCRIPTION" : """
                                                        **INPUTS:**
                                                            1. Job Description: {job_description}
                                                            2. Current Resume Json: {current_resume_json}
                                                            3. Target Json Schema: {target_json_schema}    
                                                        """,
            "USER_CONTEXT_INPUT_WITHOUT_JOB_DESCRIPTION" : """ 
                                                        **INPUTS:**
                                                            1. Current Resume Json: {current_resume_json}
                                                            2. Target Json Schema: {target_json_schema}
                                                        """,

            "PROMPT_TECH_RESUME": """
                                Given a software developer's resume (in JSON format), a job description, and a schema:
                                - Align the resume to highlight tech stacks, project impact, and team contributions
                                - Add a professional summary that is focused on engineering accomplishments and strengths
                                - Include skills relevant to the job (programming languages, frameworks, tools)
                                - Return a valid JSON output as per the schema

                                Make sure the resume is ATS-friendly and well-aligned to the job description.
                                """,
            "PROMPT_SCHEMA_OPTIMIZER": """
                                    You are a JSON resume optimizer. Your job is to:
                                    - Tailor the resume based on the job description
                                    - Add ATS-friendly fields such as professional summary, skills, and accomplishments
                                    - Make sure your JSON output strictly follows the provided schema
                                    - Use concise, impactful language
                                    - Incorporate relevant keywords from the job description naturally

                                    The resume must be truthful and aligned with the candidate’s current experience.
                                    """,
            "PROMPT_LIGHT_EDIT": """
                                You are an AI resume editor. Given a resume in JSON format and a job description, make the following updates:
                                - Add a professional summary that reflects the candidate’s alignment with the job
                                - Add a skills section with relevant keywords
                                - Slightly tweak experience bullet points for clarity and ATS readability

                                Do not modify content that is not related to the job description. Return the resume as valid JSON per the given schema.
                                """,
            "PROMPT_ENHANCE_FIELDS": """
                                    Given a JSON resume, a job description, and a JSON schema, enhance the resume by:
                                    - Adding a professional summary tailored to the job
                                    - Adding a skills list extracted from the job description
                                    - Filling any missing fields present in the schema with best estimates based on existing resume content
                                    - Ensuring it is ATS-compatible with clear, standard formatting

                                    Output must strictly follow the provided JSON schema.
                                    """,
        }

        self.user_prompts = {}

    def add_user_prompt(self, prompt_name: str, prompt_text: str,
                        integration_point: str = "append"):
        """
        Add user-defined custom prompts

        Args:
            prompt_name: Unique identifier for the custom prompt
            prompt_text: The custom prompt text
            integration_point: How to integrate ('append', 'prepend', 'replace')
        """
        self.user_prompts[prompt_name] = {
            "text": prompt_text,
            "integration": integration_point
        }

    def combine_user_prompts(self, master_prompt_key: str, user_prompt_names: List[str] = None) -> str:
        """Combine master prompts with user custom prompts"""
        base_prompt = self.master_prompts.get(master_prompt_key, "")

        if not user_prompt_names:
            return base_prompt

        combined_prompt = base_prompt

        for prompt_name in user_prompt_names:
            if prompt_name in self.user_prompts:
                user_prompt = self.user_prompts[prompt_name]

                if user_prompt["integration"] == "prepend":
                    combined_prompt = f"{user_prompt['text']}\n\n{combined_prompt}"
                elif user_prompt["integration"] == "append":
                    combined_prompt = f"{combined_prompt}\n\n{user_prompt['text']}"
                elif user_prompt["integration"] == "replace":
                    combined_prompt = user_prompt["text"]

        return combined_prompt

    def add_prompt(self, name, prompt):
        self.master_prompts[name] = prompt

    def get_prompt(self, name):
        return self.master_prompts.get(name, "Prompt not found.")

    def list_prompts(self):
        return list(self.master_prompts.keys())