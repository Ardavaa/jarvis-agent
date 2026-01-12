'use client';

import { useState } from 'react';
import { Plus, Menu, X, MessageSquare } from 'lucide-react';

interface SidebarProps {
    isOpen: boolean;
    onToggle: () => void;
    currentConversationId?: string;
    onSelectConversation: (id: string) => void;
}

export default function Sidebar({
    isOpen,
    onToggle,
    currentConversationId,
    onSelectConversation,
}: SidebarProps) {
    const [conversations] = useState<any[]>([]);

    const handleNewChat = () => {
        onSelectConversation('');
    };

    return (
        <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col h-screen">
            {/* Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                        JARVIS
                    </h2>
                </div>
                <button
                    onClick={handleNewChat}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                >
                    <Plus className="w-4 h-4" />
                    New Chat
                </button>
            </div>

            {/* Conversation List */}
            <div className="flex-1 overflow-y-auto p-2">
                {conversations.length === 0 && (
                    <div className="text-center text-gray-500 dark:text-gray-400 mt-8">
                        <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">No conversations yet</p>
                    </div>
                )}
            </div>
        </div>
    );
}
