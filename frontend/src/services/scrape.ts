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
    createJob: async (data: ScrapeFormData) => {
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

        const response = await api.post<{ job_id: string; status: string }>('/scrape/', payload);
        return response.data;
    },

    getJob: async (id: string) => {
        const response = await api.get<ScrapeJob>(`/scrape/${id}`);
        return response.data;
    },

    saveJob: async (id: string) => {
        const response = await api.post<{ job_id: string; status: string }>(`/scrape/${id}/save`);
        return response.data;
    },

    getHistory: async () => {
        const response = await api.get<ScrapeJob[]>('/scrape/history/all');
        return response.data;
    },
};
