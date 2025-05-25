import json
import os
from openai import OpenAI
from src.FileOperations import load_schema_file
from dotenv import load_dotenv, dotenv_values
load_dotenv()

def create_client(llm_provider):
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
        case _:
            client = OpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url=os.getenv('DEEPSEEK_URL'))
            model = "deepseek-chat"
    return client , model

def response_to_json(content,llm_provider):
    if llm_provider is None:
        llm_provider = 'deepseek'
    match llm_provider:
        case 'google':
            return json.loads(content)
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

def openAi_llm_caller(client,model,message):
    response = client.chat.completions.create(
        model=model,
        messages=message,
        stream=False
    )
    return response.choices[0].message

def parse_file_to_json(text):
    schema_file_contents = load_schema_file("schema.json")
    schema_instruction = f"""
    You are a helpful assistant. Extract data from unstructured text and return valid JSON following this schema:

    {json.dumps(schema_file_contents, indent=2)}

    Return only a valid JSON object. Do NOT include markdown, code blocks, or any explanation.
    """
    message = [
        {"role": "system", "content": schema_instruction},
        {"role": "user", "content": text}
    ]
    client , model = create_client()
    response = openAi_llm_caller(client,model,message)
    content = response.content
    return response_to_json(content)







