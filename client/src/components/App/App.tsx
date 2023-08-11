import {useRef, useState} from 'react';
import PromptInput from "../PromptInput/PromptInput";
import './App.css';
import { ResponseAreaRefPros } from '../ResponseArea/area-ref-interface';
import ResponseArea from '../ResponseArea/ResponseArea';

const App = () => {

  const responseAreaRef = useRef<ResponseAreaRefPros>(null);

  const callGetGPTResult = () => {
    responseAreaRef.current?.getGPTResult()
  }

  const [prompt, setPrompt] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="App">
      <div id='response-area'>
        <ResponseArea 
          ref={responseAreaRef}
          modelValue='gpt'
          prompt={prompt}
          updatePrompt={(prompt) => setPrompt(prompt)}
          isLoading={isLoading}
          updateIsLoading={(isLoading) => setIsLoading(isLoading)}
        />
      </div>
      
      <div id="input-container">
        <PromptInput
          prompt={prompt}
          onSubmit={() => callGetGPTResult()}
          key="prompt-input"
          updatePrompt={(prompt) => setPrompt(prompt)}
        />
        <button id="submit-button" className={isLoading ? 'loading' : ''} onClick={() => callGetGPTResult()}></button>
      </div>
    </div>
  );
}

export default App;
