from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_response(prompt, model):
    print(prompt)

    if model == 'gpt':
        return "Hello GPT!"
    else:
        return "Hello GAN!"

@app.route('/chat', methods=['POST', 'GET'])
def chat():
    data = request.get_json()
    
    response = get_response(data['prompt'], data['model'])
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3080)
    # app.run(host='0.0.0.0', port=3080, ssl_context='adhoc')
