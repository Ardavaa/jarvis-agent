'use client';

import { useEffect, useRef } from 'react';
import Message from './Message';
import type { Message as MessageType } from '@/types';

interface MessageListProps {
    messages: MessageType[];
    isLoading: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white dark:bg-gray-900">
            {messages.length === 0 && !isLoading && (
                <div className="flex items-center justify-center h-full">
                    <div className="text-center text-gray-500 dark:text-gray-400">
                        <h2 className="text-2xl font-semibold mb-2">Welcome to JARVIS</h2>
                        <p>Your multimodal AI assistant</p>
                        <p className="text-sm mt-2">Start a conversation by typing a message below</p>
                    </div>
                </div>
            )}

            {messages.map((message) => (
                <Message key={message.id} message={message} />
            ))}

            {isLoading && (
                <div className="flex items-center space-x-2 text-gray-500">
                    <div className="animate-pulse">●</div>
                    <div className="animate-pulse" style={{ animationDelay: '0.2s' }}>●</div>
                    <div className="animate-pulse" style={{ animationDelay: '0.4s' }}>●</div>
                </div>
            )}

            <div ref={messagesEndRef} />
        </div>
    );
}
