import os
import json
from ollama import Client


def ollama_request(prompt, model, model_class=None):
    host = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
    if not model:
        # model = "mistral-small3.1:latest" # this seem good but resource intensive
        # model = "deepseek-r1:1.5b" # not good
        # model = "gemma3:latest" # pretty good
        model = "qwen2.5:latest"  # good and fast
    format_schema = model_class.model_json_schema()
    client = Client(host=host)
    response = client.chat(
        model=model,
        format=format_schema,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    # print(f"\tOllama response: {response.message.content}")
    # myjson = format_schema.model_validate_json(response.message.content)
    try:
        return json.loads(response.message.content)
    except json.JSONDecodeError:
        print("\tWarning: Failed to parse Ollama response as JSON.")
        return None
