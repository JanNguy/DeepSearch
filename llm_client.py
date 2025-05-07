# llm_client.py
import ollama

def ask_ollama(prompt, context, model="deepseek-r1", max_tokens=4000):
    full_prompt = f"{prompt}\n\n{context}"
    try:
        resp = ollama.generate(model=model, prompt=full_prompt, stream=False)
        return resp.get("response","")[:max_tokens]
    except Exception as e:
        return f"[LLM Error] {e}"
