from flask import Flask, render_template, request, jsonify
from search import crawl_and_collect, filter_relevant
from llm_client import ask_ollama

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def query():
    data = request.get_json()
    url = data.get('base_url')
    prompt = data.get('query')
    if not url or not prompt:
        return jsonify(error="base_url and query required"), 400
    pages = crawl_and_collect(url, prompt, max_pages=5)
    filtered = filter_relevant(pages, prompt)
    if not filtered:
        return jsonify(error="No relevant information found"), 200

    context = "\n".join(filtered)
    response = ask_ollama(prompt, context)

    return jsonify({
        "filtered_context": context,
        "llm_response": response
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
