'use client';

import { useState, useEffect } from 'react';
import MessageList from './MessageList';
import InputArea from './InputArea';
import { chatAPI } from '@/lib/api';
import type { Message } from '@/types';

interface ChatContainerProps {
    conversationId?: string;
}

export default function ChatContainer({ conversationId }: ChatContainerProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (conversationId) {
            loadMessages();
        } else {
            setMessages([]);
        }
    }, [conversationId]);

    const loadMessages = async () => {
        if (!conversationId) return;
        try {
            const msgs = await chatAPI.getMessages(conversationId);
            setMessages(msgs);
        } catch (error) {
            console.error('Failed to load messages:', error);
        }
    };

    const handleSendMessage = async (content: string) => {
        // Add user message immediately
        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content,
            timestamp: new Date(),
        };
        setMessages(prev => [...prev, userMessage]);

        setIsLoading(true);
        try {
            const response = await chatAPI.sendMessage(content, conversationId);
            // Replace with actual response
            setMessages(prev => [...prev.slice(0, -1), userMessage, response.message]);
        } catch (error) {
            console.error('Failed to send message:', error);
            // Add error message
            const errorMessage: Message = {
                id: Date.now().toString(),
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please make sure the backend is running on http://localhost:8000',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="border-b border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800">
                <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                    JARVIS
                </h1>
            </div>

            {/* Messages */}
            <MessageList messages={messages} isLoading={isLoading} />

            {/* Input */}
            <InputArea onSendMessage={handleSendMessage} disabled={isLoading} />
        </div>
    );
}
