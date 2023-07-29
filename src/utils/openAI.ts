import { createParser } from 'eventsource-parser'
import type { ParsedEvent, ReconnectInterval } from 'eventsource-parser'
import type { ChatMessage } from '@/types'

export const model = import.meta.env.OPENAI_API_MODEL || 'gpt-3.5-turbo'

export const generatePayload = (apiKey: string, messages: ChatMessage[]): RequestInit & { dispatcher?: any } => ({
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${apiKey}`,
  },
  method: 'POST',
  body: JSON.stringify({
    model,
    messages,
    temperature: 0.6,
    stream: true,
  }),
})

export const parseOpenAIStream = (rawResponse: Response) => {
  const encoder = new TextEncoder()
  const decoder = new TextDecoder()
  console.log('rawResponse', rawResponse)
  if (!rawResponse.ok) {
    return new Response(rawResponse.body, {
      status: rawResponse.status,
      statusText: rawResponse.statusText,
    })
  }

  console.log('rawResponse.body', rawResponse.body)
  const stream = new ReadableStream({
    async start(controller) {
      console.log('start')
      const streamParser = (event: ParsedEvent | ReconnectInterval) => {
        console.log('event', event)
        if (event.type === 'event') {
          const data = event.data
          if (data === '[DONE]') {
            controller.close()
            return
          }
          try {
            // response = {
            //   id: 'chatcmpl-6pULPSegWhFgi0XQ1DtgA3zTa1WR6',
            //   object: 'chat.completion.chunk',
            //   created: 1677729391,
            //   model: 'gpt-3.5-turbo-0301',
            //   choices: [
            //     { delta: { content: '你' }, index: 0, finish_reason: null }
            //   ],
            // }
            const json = JSON.parse(data)
            const text = json.choices[0].delta?.content || ''
            console.log('text', text)
            const queue = encoder.encode(text)
            controller.enqueue(queue)
          } catch (e) {
            console.log('error', e)
            controller.error(e)
          }
        }
      }

      const parser = createParser(streamParser)
      console.log('parser', parser)
      for await (const chunk of rawResponse.body as any) {
        console.log('chunk', chunk)
        parser.feed(decoder.decode(chunk))
      }
    },
  })

  return new Response(stream)
}
