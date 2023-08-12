import {useRef, useState} from 'react';
import PromptInput from "../PromptInput/PromptInput";
import './App.css';
import { ResponseAreaRefPros } from '../ResponseArea/area-ref-interface';
import ResponseArea from '../ResponseArea/ResponseArea';

const App = () => {

  const responseAreaRef1 = useRef<ResponseAreaRefPros>(null);
  const responseAreaRef2 = useRef<ResponseAreaRefPros>(null);

  const callGetGPTResult = () => {
    responseAreaRef1.current?.getGPTResult()
    responseAreaRef2.current?.getGPTResult()
  }

  const [prompt, setPrompt] = useState<string>('');
  const [isLoading1, setIsLoading1] = useState(false);
  const [isLoading2, setIsLoading2] = useState(false);

  return (
    <div className="App">
      <div id='response-area'>
        <ResponseArea 
          ref={responseAreaRef1}
          modelValue='gpt'
          prompt={prompt}
          updatePrompt={(prompt) => setPrompt(prompt)}
          isLoading={isLoading1}
          updateIsLoading={(isLoading) => setIsLoading1(isLoading)}
        />
        <ResponseArea 
          ref={responseAreaRef2}
          modelValue='gan'
          prompt={prompt}
          updatePrompt={(prompt) => setPrompt(prompt)}
          isLoading={isLoading2}
          updateIsLoading={(isLoading) => setIsLoading2(isLoading)}
        />
      </div>
      
      <div id="input-container">
        <PromptInput
          prompt={prompt}
          onSubmit={() => callGetGPTResult()}
          key="prompt-input"
          updatePrompt={(prompt) => setPrompt(prompt)}
        />
        <button id="submit-button" className={(isLoading1 && isLoading2) ? 'loading' : ''} onClick={() => callGetGPTResult()}></button>
      </div>
    </div>
  );
}

export default App;
