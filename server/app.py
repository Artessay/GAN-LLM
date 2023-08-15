from flask import Flask, request
from flask_cors import CORS
import os
import pickle
from contextlib import nullcontext
import torch
import tiktoken
from model import GPTConfig, GPT

# -----------------------------------------------------------------------------
init_from = 'resume' # either 'resume' (from an out_dir) or a gpt2 variant (e.g. 'gpt2-xl')
out_dir = 'out' # ignored if init_from is not 'resume'
num_samples = 1 # number of samples to draw
max_new_tokens = 150 # number of tokens generated in each sample
temperature = 0.8 # 1.0 = no change, < 1.0 = less random, > 1.0 = more random, in predictions
top_k = 10 # retain only the top_k most likely tokens, clamp others to have 0 probability
seed = 1337
device = 'cuda' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.
dtype = 'float16' # 'float32' or 'bfloat16' or 'float16'
compile = False # use PyTorch 2.0 to compile the model to be faster
exec(open('configurator.py').read()) # overrides from command line or config file
# -----------------------------------------------------------------------------

torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.backends.cuda.matmul.allow_tf32 = True # allow tf32 on matmul
torch.backends.cudnn.allow_tf32 = True # allow tf32 on cudnn
device_type = 'cuda' if 'cuda' in device else 'cpu' # for later use in torch.autocast
ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
ctx = nullcontext() if device_type == 'cpu' else torch.amp.autocast(device_type=device_type, dtype=ptdtype)


app = Flask(__name__)
CORS(app)

def get_response(prompt, model):
    print(prompt)
    if model == 'gpt':
        checkpoint = torch.load('out-squad-new/ckpt.pt') # !! checked: model's path
        gptconf = GPTConfig(**checkpoint['model_args'])
        model = GPT(gptconf)
        state_dict = checkpoint['model']
        unwanted_prefix = '_orig_mod.'
        for k,v in list(state_dict.items()):
            if k.startswith(unwanted_prefix):
                state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
        model.load_state_dict(state_dict)
                
        model.eval()
        model.to(device)
        if compile:
            model = torch.compile(model) # requires PyTorch 2.0 (optional)
        enc = tiktoken.get_encoding("gpt2")
        encode = lambda s: enc.encode(s, allowed_special={"<|endoftext|>"})
        decode = lambda l: enc.decode(l)
        start_ids = encode(prompt)
        x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])

        # run generation
        with torch.no_grad():
            with ctx:
                for k in range(num_samples):
                    y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)

        return decode(y[0].tolist())
        # return "Hello GPT"

    else:
        checkpoint = torch.load('out-squad-GAN/ckpt.pt') # !! checked: model's path
        gptconf = GPTConfig(**checkpoint['model_args'])
        model = GPT(gptconf)
        state_dict = checkpoint['model']
        unwanted_prefix = '_orig_mod.'
        for k,v in list(state_dict.items()):
            if k.startswith(unwanted_prefix):
                state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
        model.load_state_dict(state_dict)
                
        model.eval()
        model.to(device)
        if compile:
            model = torch.compile(model) # requires PyTorch 2.0 (optional)
        enc = tiktoken.get_encoding("gpt2")
        encode = lambda s: enc.encode(s, allowed_special={"<|endoftext|>"})
        decode = lambda l: enc.decode(l)
        start_ids = encode(prompt)
        x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])

        # run generation
        with torch.no_grad():
            with ctx:
                for k in range(num_samples):
                    y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)

        return decode(y[0].tolist())

@app.route('/chat', methods=['POST', 'GET'])
def chat():
    data = request.get_json()
    
    response = get_response(data['prompt'], data['model'])
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    # print("gpt")
    # print(get_response('To whom was John B. Kroc married?', 'gpt'))

    # print("gan")
    # print(get_response('To whom was John B. Kroc married?', 'gan'))
