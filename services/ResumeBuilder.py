import json
import os
import httpx
from openai import OpenAI
from dotenv import load_dotenv
from utils.FileOperations import FileOperations
from utils.Prompts import Prompts

load_dotenv()

class ResumeBuilder:
    def __init__(self, llm_provider='deepseek'):
        """Initialize the Resume Builder with LLM client"""
        self.llm_provider = llm_provider
        self.client, self.model = self.create_client(llm_provider)
        self.prompts = Prompts()
        self.json_schema = FileOperations().load_schema_file("data/schema.json")

    @staticmethod
    def call_gemini_and_extract_json(prompt: str, model_name: str = None) -> dict:
        """
        Calls the Google Gemini API synchronously with the given prompt and extracts the JSON object from the response.
        Raises exceptions for HTTP errors or malformed responses.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set in environment variables.")
        model = model_name or os.getenv("GEMINI_MODEL_NAME", "gemma-3-27b-it")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        with httpx.Client() as client:
            resp = client.post(url, headers=headers, json=data)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API error: {resp.status_code} - {resp.text}")
            response = resp.json()

        try:
            candidates = response.get("candidates")
            if not candidates or not isinstance(candidates, list):
                raise ValueError("No candidates found in Gemini response.")
            content = candidates[0].get("content")
            if not content or "parts" not in content or not content["parts"]:
                raise ValueError("No content parts found in Gemini response.")
            text = content["parts"][0].get("text")
            if not text:
                raise ValueError("No text found in Gemini response part.")
            # Remove code block markers if present
            if text.startswith("```json"):
                text = text.removeprefix("```json").removesuffix("```").strip()
            elif text.startswith("```"):
                text = text.removeprefix("```").removesuffix("```").strip()
            return json.loads(text)
        except Exception as e:
            raise RuntimeError(f"Failed to extract JSON from Gemini response: {e}")

    def parse_file_to_json_gemini(self, text):
        prompts = Prompts()
        base_prompt = prompts.get_prompt("EXTRACT_TO_SCHEMA")
        schema_instruction = base_prompt.format(SCHEMA=json.dumps(self.json_schema, indent=2))
        # Concatenate system and user prompt for Gemini
        prompt = f"{schema_instruction}\n{text}"
        return self.call_gemini_and_extract_json(prompt)

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








