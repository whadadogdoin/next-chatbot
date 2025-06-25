import { useState, useEffect,useRef } from 'react'
import './App.css'
import { Send, Bot, User, Loader2 } from "lucide-react"
import { Input } from "@/components/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/card"
import { ScrollArea } from "@/components/scroll-area"
import { Avatar, AvatarFallback } from "@/components/avatar"
import { Button } from './components/button'
// import axios from "axios"
//@ts-ignore
import ReactMarkdown from 'react-markdown'


function App() {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string; id: string }[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    const query = input.trim()
    if (!query) return

    const userId = crypto.randomUUID()
    const assistantId = crypto.randomUUID()

    setMessages(prev => [...prev, { id: userId, role: 'user', content: query }])
    setInput('')
    setIsLoading(true)

    try {
      setMessages(prev => [...prev, {id: assistantId, role: "assistant", content: ''}])
      const response = await fetch(`http://localhost:8000/chat/${encodeURIComponent(query)}`)
      if (!response.body) throw new Error('No streaming body')
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let partial = ''
      while(true){
        const {done,value} = await reader.read()
        if (done)
          break
        partial += decoder.decode(value,{stream: true})
        setMessages(prev => prev.map(m => m.id === assistantId ? {...m, content: partial} : m))
      }
    } catch (error) {
      console.error(error)
      setMessages(prev => [...prev, { id: (Date.now() + 1).toString(), role: 'assistant', content: 'Oops, something went wrong. Please try again.' }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">AI Assistant</h1>
          <p className="text-gray-600">Ask me anything and I'll help you out!</p>
        </div>

        <Card className="h-[90vh] flex flex-col shadow-xl border-0 overflow-hidden">
          <CardHeader className="bg-white border-b border-gray-100 rounded-t-lg z-10">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Bot className="w-5 h-5 text-blue-600" />
              Chat Assistant
            </CardTitle>
          </CardHeader>

          <CardContent className="flex-1 p-0 overflow-hidden">
            <ScrollArea className="h-full p-4">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <Bot className="w-16 h-16 text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-500 mb-2">Start a conversation</h3>
                  <p className="text-gray-400 max-w-md">
                    Type a message below to begin chatting with your AI assistant.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map(message => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      {message.role === 'assistant' && message.content!= '' && (
                        <Avatar className="w-8 h-8 bg-blue-100 flex-shrink-0">
                          <AvatarFallback>
                            <Bot className="w-4 h-4 text-blue-600" />
                          </AvatarFallback>
                        </Avatar>
                      )}

                      <div
                        className={`max-w-[70%] break-words overflow-hidden rounded-2xl px-4 py-2 ${
                          message.role === 'user'
                            ? 'bg-blue-600 text-white ml-auto'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {message.role === 'assistant' ? (
                          <div className='prose prose-sm whitespace-pre-wrap text-left break-word overflow-x-auto'>
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                          </div>
                        ) : (
                          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                        )}
                      </div>

                      {message.role === 'user' && (
                        <Avatar className="w-8 h-8 bg-blue-600 flex-shrink-0">
                          <AvatarFallback>
                            <User className="w-4 h-4 text-white" />
                          </AvatarFallback>
                        </Avatar>
                      )}
                    </div>
                  ))}

                  {isLoading && (
                    <div className="flex gap-3 justify-start">
                      <Avatar className="w-8 h-8 bg-blue-100 flex-shrink-0">
                        <AvatarFallback>
                          <Bot className="w-4 h-4 text-blue-600" />
                        </AvatarFallback>
                      </Avatar>
                      <div className="bg-gray-100 rounded-2xl px-4 py-2 max-w-[70%]">
                        <div className="flex items-center gap-2 break-words">
                          <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
                          <span className="text-sm text-gray-500">Thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>
              )}
            </ScrollArea>
          </CardContent>

          <div className="border-t border-gray-100 p-4 bg-white rounded-b-lg z-10">
            <form onSubmit={handleSend} className="flex gap-2">
              <Input
                value={input}
                onChange={handleInputChange}
                placeholder="Type your message here..."
                disabled={isLoading}
                className="flex-1 border-gray-200 focus:border-blue-500 focus:ring-blue-500"
              />
              <Button type="submit" disabled={isLoading || !input.trim()} className="bg-blue-600 hover:bg-blue-700 text-white px-4">
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </Button>
            </form>
            <p className="text-xs text-gray-500 mt-2 text-center">Messages will be cleared when you refresh the page</p>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default App
