import ollama
from transformers import AutoTokenizer
import re

def read_markdown(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return ""
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def split_into_chunks(text, max_chars=3000):
    chunks = []
    current_chunk = ""
    for line in text.splitlines():
        if len(current_chunk) + len(line) + 1 > max_chars:
            chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

def ask_ollama(prompt, chunk, model="deepseek-r1", max_response_chars=4000):
    full_prompt = f"{prompt}\n\n{chunk}"

    try:
        response = ollama.generate(
            model=model,
            prompt=full_prompt,
            stream=False
        )
        return response["response"][:max_response_chars]
    except Exception as e:
        print(f"Error with Ollama: {e}")
        return ""

def main():
    base = "Do a simple reseponse without any extra information, just the answer to the question and dont speak about your way of thinking and all the 'User ask information about this person' type \n."
    prompt = input("Enter your prompt: ").strip()
    prompt = base + prompt

    if not prompt:
        print("Prompt required.")
        return

    md_file = "filtered_output.md"

    text = read_markdown(md_file)
    if not text:
        print("No content to process. Check if filtered_output.md exists and is not empty.")
        return

    chunks = split_into_chunks(text, max_chars=3000)
    total_response = ""
    total_chars = 0
    max_total_chars = 4000
    model = "deepseek:1.5-7b"

    for i, chunk in enumerate(chunks):
        if total_chars >= max_total_chars:
            print("Reached 4000 character limit. Stopping further processing.")
            break
        print(f"\nProcessing chunk {i + 1}/{len(chunks)}...")
        response = ask_ollama(prompt, chunk, model=model)
        if response:
            response_chars = len(response)
            if total_chars + response_chars > max_total_chars:
                remaining_chars = max_total_chars - total_chars
                total_response += response[:remaining_chars]
                total_chars = max_total_chars
                print("Response truncated to stay within 4000 character limit.")
            else:
                total_response += response + "\n\n"
                total_chars += response_chars + 2
            print(f"Chunk response:\n{response}")
    with open("ollama_response.md", "w", encoding="utf-8") as f:
        f.write(total_response)

if __name__ == "__main__":
    main()
