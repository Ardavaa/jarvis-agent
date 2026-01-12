'use client';

import { useState } from 'react';
import ChatContainer from '@/components/Chat/ChatContainer';
import Sidebar from '@/components/Sidebar/Sidebar';

export default function Home() {
  const [currentConversationId, setCurrentConversationId] = useState<string>();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'block' : 'hidden'} md:block`}>
        <Sidebar
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          currentConversationId={currentConversationId}
          onSelectConversation={setCurrentConversationId}
        />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <ChatContainer conversationId={currentConversationId} />
      </div>
    </div>
  );
}
