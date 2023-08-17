from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_response(prompt, model):
    print(prompt)

    if model == 'gpt':
        return "Hello GPT"
    else:
        return "Hello GAN"

@app.route('/chat', methods=['POST', 'GET'])
def chat():
    data = request.get_json()
    
    response = get_response(data['prompt'], data['model'])
    return response

@app.route('/', methods=['POST', 'GET'])
def test():
    return "Hello World!"

if __name__ == '__main__':
    # from waitress import serve
    # serve(app, host='0.0.0.0', port=8080)
    app.run(host='0.0.0.0', port=8080, ssl_context='adhoc')
