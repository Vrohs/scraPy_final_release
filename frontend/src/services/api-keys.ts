import { api } from '@/lib/api';

export interface ApiKey {
    id: string;
    name: string;
    key_prefix: string;
    created_at: string;
    key?: string; // Only present on creation
}

export const apiKeyService = {
    listKeys: async (token: string) => {
        const response = await api.get<ApiKey[]>('/api_keys/', {
            headers: { Authorization: `Bearer ${token}` }
        });
        return response.data;
    },

    createKey: async (name: string, token: string) => {
        const response = await api.post<ApiKey>('/api_keys/', { name }, {
            headers: { Authorization: `Bearer ${token}` }
        });
        return response.data;
    },

    revokeKey: async (id: string, token: string) => {
        await api.delete(`/api_keys/${id}`, {
            headers: { Authorization: `Bearer ${token}` }
        });
    }
};
