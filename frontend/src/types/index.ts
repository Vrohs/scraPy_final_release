export type ScrapingJobStatus = 'queued' | 'processing' | 'completed' | 'failed';

export interface ScrapingJob {
    id: string;
    url: string;
    status: ScrapingJobStatus;
    created_at: string;
    completed_at?: string;
    data?: any;
    error?: string;
}

export interface ScrapeRequest {
    url: string;
    mode: 'guided' | 'smart';
    selectors?: Record<string, string>;
    instruction?: string;
}
