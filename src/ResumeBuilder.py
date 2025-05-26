import json
import os
from openai import OpenAI
from dotenv import load_dotenv

from src.FileOperations import FileOperations
from src.Prompts import Prompts

load_dotenv()

class ResumeBuilder:
    def __init__(self, llm_provider='deepseek'):
        """Initialize the Resume Builder with LLM client"""
        self.llm_provider = llm_provider
        self.client, self.model = self.create_client(llm_provider)
        self.prompts = Prompts()
        self.json_schema = FileOperations().load_schema_file("data/schema.json")

    @staticmethod
    def openAi_llm_caller(client,model,message):
        response = client.chat.completions.create(
            model=model,
            messages=message,
            stream=False
        )
        return response.choices[0].message

    def create_client(self,llm_provider='deepseek'):
        if llm_provider is None:
            client = OpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url=os.getenv('DEEPSEEK_URL'))
            model = "deepseek-chat"
            return client , model
        match llm_provider:
            case 'google':
                client = OpenAI(api_key=os.getenv('GEMINI_API_KEY'), base_url=os.getenv('GEMINI_URL'))
                model = "gemini-2.0-flash"
            case 'deepseek':
                client = OpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url=os.getenv('DEEPSEEK_URL'))
                model = "deepseek-chat"
            case 'openai':
                client = OpenAI(api_key=os.getenv('OPENAI_KEY'))
                model = "gpt-4.1-nano-2025-04-14"
            case _:
                client = OpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url=os.getenv('DEEPSEEK_URL'))
                model = "deepseek-chat"
        print(f'Providers : {llm_provider} \n model : {model}')
        self.client, self.model = client, model
        return client , model

    def response_to_json(self,content,llm_provider='deepseek'):
        if llm_provider is None:
            llm_provider = 'deepseek'
        match llm_provider:
            case 'google':
                if content.startswith("```json"):
                    content = content.removeprefix("```json").removesuffix("```").strip()
                elif content.startswith("```"):
                    content = content.removeprefix("```").removesuffix("```").strip()
                try:
                    parsed_json = json.loads(content)
                    return parsed_json
                except json.JSONDecodeError as e:
                    print("type of content:", type(content))
                    print("❌ Failed to parse JSON. Here's the raw content:\n", content)
                    raise e
            case 'deepseek':
                if content.startswith("```json"):
                    content = content.removeprefix("```json").removesuffix("```").strip()
                elif content.startswith("```"):
                    content = content.removeprefix("```").removesuffix("```").strip()
                try:
                    parsed_json = json.loads(content)
                    return parsed_json
                except json.JSONDecodeError as e:
                    print("type of content:", type(content))
                    print("❌ Failed to parse JSON. Here's the raw content:\n", content)
                    raise e
            case _:
                return json.loads(content)

    def parse_file_to_json(self,text):
        prompts = Prompts()
        base_prompt = prompts.get_prompt("EXTRACT_TO_SCHEMA")
        schema_instruction = base_prompt.format(SCHEMA=json.dumps(self.json_schema, indent=2))
        message = [
            {"role": "system", "content": schema_instruction},
            {"role": "user", "content": text}
        ]
        llm = 'google'
        client , model = self.create_client(llm)
        response = self.openAi_llm_caller(client, model, message)
        content = response.content
        return self.response_to_json(content, llm)

    def build_resume_json(self, current_resume_json , job_description = None , user_prompt = None):
        if job_description is None:
            system_instruction = self.prompts.get_prompt("MASTER_PROMPT_WITH_JOB_DESCRIPTION")
            prompt = self.prompts.get_prompt("USER_CONTEXT_INPUT_WITH_JOB_DESCRIPTION").format(
                job_description=json.dumps(job_description, indent=2),
                current_resume_json=json.dumps(current_resume_json, indent=2),
                target_json_schema= json.dumps(self.json_schema, indent=2)
            )
        else:
            system_instruction = self.prompts.get_prompt("MASTER_PROMPT_WITHOUT_JOB_DESCRIPTION")
            prompt = self.prompts.get_prompt("USER_CONTEXT_INPUT_WITHOUT_JOB_DESCRIPTION").format(
                current_resume_json=json.dumps(current_resume_json, indent=2),
                target_json_schema=json.dumps(self.json_schema, indent=2)
            )
        if user_prompt is not None:
            prompt = f"{prompt}\n\n{user_prompt}"
        message = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ]
        print(f"Message: {message}")
        client, model = self.create_client(self.llm_provider)
        response = self.openAi_llm_caller(client, model, message)
        content = response.content
        print(f"Response Content: {content}")
        return self.response_to_json(content, self.llm_provider)








