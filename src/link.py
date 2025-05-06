import fitz
from transformers import AutoTokenizer
import ollama

def read_pdf(file_path):
    with fitz.open(file_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

def ask_ollama(prompt, model="phi3"):
    response = ollama.generate(
        model=model,
        prompt=prompt,
        stream=False
    )
    return response["response"]

prompt = str(input("Enter your prompt: "))

text = read_pdf("files/final_output.pdf")

tokenizer = AutoTokenizer.from_pretrained("gpt2")

chunks = []
current_chunk = []
current_length = 0

for token in tokenizer.tokenize(text):
    current_chunk.append(token)
    current_length += 1
    if current_length >= 3000:
        chunks.append(tokenizer.convert_tokens_to_string(current_chunk))
        current_chunk = []
        current_length = 0
if current_chunk:
    chunks.append(tokenizer.convert_tokens_to_string(current_chunk))

for chunk in chunks:
    response = ask_ollama(prompt + "\n\n" + chunk)
    print(response)
