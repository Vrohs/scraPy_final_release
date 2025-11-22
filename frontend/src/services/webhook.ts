import { api } from '@/lib/api';

export interface Webhook {
    id: string;
    url: string;
    events: string[];
    secret: string;
    created_at: string;
}

export const webhookService = {
    listWebhooks: async (token: string) => {
        const response = await api.get<Webhook[]>('/webhooks/', {
            headers: { Authorization: `Bearer ${token}` }
        });
        return response.data;
    },

    createWebhook: async (url: string, token: string) => {
        const response = await api.post<Webhook>('/webhooks/', { url, events: ["job.completed"] }, {
            headers: { Authorization: `Bearer ${token}` }
        });
        return response.data;
    },

    deleteWebhook: async (id: string, token: string) => {
        await api.delete(`/webhooks/${id}`, {
            headers: { Authorization: `Bearer ${token}` }
        });
    }
};
