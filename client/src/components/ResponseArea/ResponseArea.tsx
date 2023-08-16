import {forwardRef, useImperativeHandle, useState} from 'react';
import axios from "axios";
import './ResponseArea.css';
import { ResponseAreaRefPros } from './area-ref-interface';
import {ResponseInterface} from "../PromptResponseList/response-interface";
import PromptResponseList from "../PromptResponseList/PromptResponseList";

interface ResponseAreaPros {
    modelValue: string;
    prompt: string;
    updatePrompt: (prompt: string) => void;
    isLoading: boolean;
    updateIsLoading: (isLoading: boolean) => void;
}

const ResponseArea = forwardRef<ResponseAreaRefPros, ResponseAreaPros>(
    ({ 
        modelValue,
        prompt, updatePrompt,
        isLoading, updateIsLoading
    }, responseAreaRef) => {

    const [responseList, setResponseList] = useState<ResponseInterface[]>([]);
    const [promptToRetry, setPromptToRetry] = useState<string | null>(null);
    const [uniqueIdToRetry, setUniqueIdToRetry] = useState<string | null>(null);
    let loadInterval: number | undefined;

    const generateUniqueId = () => {
        const timestamp = Date.now();
        const randomNumber = Math.random();
        const hexadecimalString = randomNumber.toString(16);

        return `id-${timestamp}-${hexadecimalString}`;
    }

    const htmlToText = (html: string) => {
        const temp = document.createElement('div');
        temp.innerHTML = html;
        return temp.textContent;
    }

    const delay = (ms: number) => {
        return new Promise( resolve => setTimeout(resolve, ms) );
    }

    const addLoader = (uid: string) => {
        const element = document.getElementById(uid) as HTMLElement;
        element.textContent = ''

        // @ts-ignore
        loadInterval = setInterval(() => {
        // Update the text content of the loading indicator
        element.textContent += '.';

        // If the loading indicator has reached three dots, reset it
        if (element.textContent === '....') {
            element.textContent = '';
        }
        }, 300);
    }


    const addResponse = (selfFlag: boolean, response?: string) => {
        const uid = generateUniqueId()
        setResponseList(prevResponses => [
        ...prevResponses,
        {
            id: uid,
            response,
            selfFlag
        },
        ]);
        return uid;
    }

    const updateResponse = (uid: string, updatedObject: Record<string, unknown>) => {
        const element = document.getElementById(uid) as HTMLElement;
        element.textContent = ''
        setResponseList(prevResponses => {
        const updatedList = [...prevResponses]
        const index = prevResponses.findIndex((response) => response.id === uid);
        if (index > -1) {
            updatedList[index] = {
            ...updatedList[index],
            ...updatedObject
            }
        }
        return updatedList;
        });
    }

    const regenerateResponse = async () => {
        await getGPTResult(promptToRetry, uniqueIdToRetry);
    }

    const getGPTResult = async (_promptToRetry?: string | null, _uniqueIdToRetry?: string | null) => {
        // Get the prompt input
        const _prompt = _promptToRetry ?? htmlToText(prompt);

        // If a response is already being generated or the prompt is empty, return
        if (isLoading || !_prompt) {
            return;
        }

        updateIsLoading(true);

        // Clear the prompt input
        updatePrompt('');

        let uniqueId: string;
        if (_uniqueIdToRetry) {
        uniqueId = _uniqueIdToRetry;
        } else {
        // Add the self prompt to the response list
        addResponse(true, _prompt);
        uniqueId = addResponse(false);
        await delay(50);
        addLoader(uniqueId);
        }

        try {
        // Send a POST request to the API with the prompt in the request body
        const response = await axios.post(
            'chat', 
            {
                prompt: _prompt,
                model: modelValue
            },
            {
                timeout: 60000    // 60,000 ms total 1 minute
            }
        );
        
        // console.log(response);
        updateResponse(uniqueId, {
            response: response.data,
        });
        
        setPromptToRetry(null);
        setUniqueIdToRetry(null);
        } catch (err) {
        setPromptToRetry(_prompt);
        setUniqueIdToRetry(uniqueId);
        updateResponse(uniqueId, {
            // @ts-ignore
            response: `Error: ${err.message}`,
            error: true
        });
        } finally {
        // Clear the loader interval
        clearInterval(loadInterval);
        updateIsLoading(false);
        }
    }

    useImperativeHandle(responseAreaRef, () => ({
        getGPTResult
    }));

    return (
        <div className="question-answer">
            {
                modelValue === "gpt" 
                ? <div className='model-title'>GPT</div>
                : <div className='model-title'>GAN</div>
            }
            <div id="response-list">
                <PromptResponseList responseList={responseList} key="response-list"/>
            </div>
            { uniqueIdToRetry &&
                (<div id="regenerate-button-container">
                <button id="regenerate-response-button" className={isLoading ? 'loading' : ''} onClick={() => regenerateResponse()}>
                    Regenerate Response
                </button>
                </div>
                )
            }
        </div>
    );
})

export default ResponseArea;
