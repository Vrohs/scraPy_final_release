import { api } from '@/lib/api';
import { ScrapeFormData } from '@/lib/validators';

export interface ScrapeJob {
    job_id: string;
    id?: string; // For history items from DB
    status: 'pending' | 'processing' | 'completed' | 'failed' | 'saved';
    url: string;
    mode: 'guided' | 'smart';
    created_at: string;
    data?: any;
    error?: string;
}

export const scrapeService = {
    createJob: async (data: ScrapeFormData, token?: string) => {
        // Transform form data to API expected format
        const payload = {
            url: data.url,
            mode: data.mode,
            selectors: data.mode === 'guided'
                ? data.selectors?.reduce((acc, curr) => ({ ...acc, [curr.key]: curr.selector }), {})
                : undefined,
            instruction: data.mode === 'smart' ? data.instruction : undefined,
            options: data.options
        };

        const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
        const response = await api.post<{ job_id: string; status: string }>('/scrape/', payload, { headers });
        return response.data;
    },

    getJob: async (id: string, token?: string) => {
        const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
        const response = await api.get<ScrapeJob>(`/scrape/${id}`, { headers });
        return response.data;
    },

    saveJob: async (id: string, token?: string) => {
        const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
        const response = await api.post<{ job_id: string; status: string }>(`/scrape/${id}/save`, {}, { headers });
        return response.data;
    },

    getHistory: async (token?: string) => {
        const headers = token ? { Authorization: `Bearer ${token}` } : undefined;
        const response = await api.get<ScrapeJob[]>('/scrape/history/all', { headers });
        return response.data;
    },
};
