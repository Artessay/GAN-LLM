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

unwanted_prefix = '_orig_mod.'

checkpoint_gpt = torch.load('/home/featurize/work/gpts/mymodel/squad_ckpt.pt')
model_gpt = gptconf = GPTConfig(**checkpoint_gpt['model_args'])
model_gpt = GPT(model_gpt)
state_dict_gpt = checkpoint_gpt['model']
for k,v in list(state_dict_gpt.items()):
    if k.startswith(unwanted_prefix):
        state_dict_gpt[k[len(unwanted_prefix):]] = state_dict_gpt.pop(k)
model_gpt.load_state_dict(state_dict_gpt)
model_gpt.eval()
model_gpt.to('cuda:0')
if compile:
    model_gpt = torch.compile(model_gpt) # requires PyTorch 2.0 (optional)

print(f'gpt2-xl loaded')

checkpoint_finetune = torch.load('/home/featurize/work/gpts/mymodel/squad_gan_ckpt.pt') # !! checked: model's path
model_finetune = GPTConfig(**checkpoint_finetune['model_args'])
model_finetune = GPT(model_finetune)
state_dict_finetune = checkpoint_finetune['model']
for k,v in list(state_dict_finetune.items()):
    if k.startswith(unwanted_prefix):
        state_dict_finetune[k[len(unwanted_prefix):]] = state_dict_finetune.pop(k)
model_finetune.load_state_dict(state_dict_finetune)
        
model_finetune.eval()
model_finetune.to('cuda:1')
if compile:
    model_finetune = torch.compile(model_finetune) # requires PyTorch 2.0 (optional)
print(f'gpt2-finetuned loaded')

enc = tiktoken.get_encoding("gpt2")
encode = lambda s: enc.encode(s, allowed_special={"<|endoftext|>"})
decode = lambda l: enc.decode(l)

def get_response(prompt, model):
    print(prompt)

    if model == 'gpt':
        # run generation
        with torch.no_grad():
            with ctx:
                start_ids = encode(prompt)
                x = (torch.tensor(start_ids, dtype=torch.long, device='cuda:0')[None, ...])
                for k in range(num_samples):
                    y = model_gpt.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
        print(f'gpt Ans:')
        return decode(y[0].tolist())
    else:
        with torch.no_grad():
            with ctx:
                start_ids = encode(prompt)
                x = (torch.tensor(start_ids, dtype=torch.long, device='cuda:1')[None, ...])
                for k in range(num_samples):
                    y = model_finetune.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
        print(f'finetune Ans:')
        return decode(y[0].tolist())

@app.route('/chat', methods=['POST', 'GET'])
def chat():
    data = request.get_json()
    
    response = get_response(data['prompt'], data['model'])
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3080, ssl_context='adhoc')
