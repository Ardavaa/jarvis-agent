import axios from 'axios';
import type { Message, Conversation, ChatResponse, VoiceTranscription } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Chat API
export const chatAPI = {
    sendMessage: async (content: string, conversationId?: string): Promise<ChatResponse> => {
        const response = await api.post('/api/chat', {
            message: content,
            conversation_id: conversationId,
            user_id: 'default_user',
        });
        return response.data;
    },

    getConversations: async (): Promise<Conversation[]> => {
        const response = await api.get('/api/conversations');
        return response.data.conversations || [];
    },

    getMessages: async (conversationId: string): Promise<Message[]> => {
        const response = await api.get(`/api/conversations/${conversationId}/messages`);
        return response.data.messages || [];
    },

    deleteConversation: async (conversationId: string): Promise<void> => {
        await api.delete(`/api/conversations/${conversationId}`);
    },
};

// Voice API
export const voiceAPI = {
    transcribe: async (audioBlob: Blob): Promise<VoiceTranscription> => {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        const response = await api.post('/api/voice/transcribe', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    synthesize: async (text: string): Promise<Blob> => {
        const response = await api.post('/api/voice/synthesize',
            { text },
            { responseType: 'blob' }
        );
        return response.data;
    },
};

export default api;
