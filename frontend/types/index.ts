// TypeScript types for JARVIS frontend

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  conversationId?: string;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  voiceEnabled: boolean;
  autoPlayResponses: boolean;
}

export interface ChatResponse {
  message: Message;
  conversationId: string;
}

export interface VoiceTranscription {
  text: string;
  language: string;
  confidence: number;
}
