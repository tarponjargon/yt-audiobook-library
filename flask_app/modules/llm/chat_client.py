import os
import json
from ollama import Client


def ollama_request(prompt, model, model_class=None):
    # Check both env var names for compatibility
    host = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
    if not model:
        # model = "mistral-small3.1:latest" # this seem good but resource intensive
        # model = "deepseek-r1:1.5b" # not good
        # model = "gemma3:latest" # pretty good
        model = "qwen2.5:latest"  # good and fast

    print(f"[DEBUG] Ollama request - host: {host}, model: {model}")
    print(f"[DEBUG] Prompt length: {len(prompt)} chars")

    format_schema = model_class.model_json_schema()
    client = Client(host=host)

    try:
        print(f"[DEBUG] Sending request to Ollama...")
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
        print(f"[DEBUG] Ollama response received: {len(response.message.content)} chars")
        print(f"[DEBUG] Response content: {response.message.content[:200]}...")
    except Exception as e:
        print(f"[DEBUG] Ollama request FAILED: {type(e).__name__}: {e}")
        raise

    try:
        return json.loads(response.message.content)
    except json.JSONDecodeError:
        print(f"[DEBUG] Failed to parse JSON response: {response.message.content}")
        return None
