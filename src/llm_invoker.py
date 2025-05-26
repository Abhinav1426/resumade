import json
import os
from openai import OpenAI
from src.FileOperations import load_schema_file
from dotenv import load_dotenv, dotenv_values

from src.Prompts import Prompts

load_dotenv()

def openAi_llm_caller(client,model,message):
    response = client.chat.completions.create(
        model=model,
        messages=message,
        stream=False
    )
    return response.choices[0].message

def create_client(llm_provider='deepseek'):
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
    return client , model

def response_to_json(content,llm_provider='deepseek'):
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



def parse_file_to_json(text):
    schema_file_contents = load_schema_file("schema.json")
    prompts = Prompts()
    base_prompt = prompts.get_prompt("EXTRACT_TO_SCHEMA")
    schema_instruction = base_prompt.replace("{SCHEMA}", json.dumps(schema_file_contents, indent=2))
    message = [
        {"role": "system", "content": schema_instruction},
        {"role": "user", "content": text}
    ]
    llm = 'google'
    client , model = create_client(llm)
    response = openAi_llm_caller(client,model,message)
    content = response.content
    return response_to_json(content,llm)

def resume_builder_with_propmt(input_json,propmts=None):
    schema_file_contents = load_schema_file("schema.json")








