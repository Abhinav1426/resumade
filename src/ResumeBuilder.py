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
        self.schema_file_contents = FileOperations().load_schema_file("data/schema.json")

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
                    print("❌ Failed to parse JSON. Here's the raw content:\n", content)
                    raise e
            case _:
                return json.loads(content)

    def parse_file_to_json(self,text):
        prompts = Prompts()
        base_prompt = prompts.get_prompt("EXTRACT_TO_SCHEMA")
        schema_instruction = base_prompt.replace("{SCHEMA}", json.dumps(self.schema_file_contents, indent=2))
        message = [
            {"role": "system", "content": schema_instruction},
            {"role": "user", "content": text}
        ]
        llm = 'google'
        client , model = self.create_client(llm)
        response = self.openAi_llm_caller(client, model, message)
        content = response.content
        return self.response_to_json(content, llm)









