'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import { Send, Mic } from 'lucide-react';

interface InputAreaProps {
    onSendMessage: (content: string) => void;
    disabled?: boolean;
}

export default function InputArea({ onSendMessage, disabled }: InputAreaProps) {
    const [input, setInput] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSend = () => {
        if (input.trim() && !disabled) {
            onSendMessage(input.trim());
            setInput('');
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
            }
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800">
            <div className="flex items-end gap-2">
                <button
                    onClick={() => alert('Voice feature coming soon!')}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    title="Voice input (coming soon)"
                >
                    <Mic className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                </button>

                <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => {
                        setInput(e.target.value);
                        e.target.style.height = 'auto';
                        e.target.style.height = e.target.scrollHeight + 'px';
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder="Type a message..."
                    disabled={disabled}
                    className="flex-1 resize-none rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 max-h-32"
                    rows={1}
                />

                <button
                    onClick={handleSend}
                    disabled={disabled || !input.trim()}
                    className="p-2 rounded-lg bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                    title="Send message"
                >
                    <Send className="w-5 h-5 text-white" />
                </button>
            </div>
        </div>
    );
}
