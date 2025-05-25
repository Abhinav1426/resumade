import json

from openai import OpenAI

from src.FileOperations import load_schema_file

client = OpenAI(api_key="lols",base_url="https://api.deepseek.com")

def parse_pdf_to_json(text):
    schema_file_path = "schema.json"
    schema_file_contents = load_schema_file(schema_file_path)

    schema_instruction = f"""
    You are a helpful assistant. Extract data from unstructured text and return valid JSON following this schema:

    {json.dumps(schema_file_contents, indent=2)}

    Return only a valid JSON object. Do NOT include markdown, code blocks, or any explanation.
    """
    messages = [
        {"role": "system", "content": schema_instruction},
        {"role": "user", "content": text}
    ]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )

    content = response.choices[0].message.content
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





