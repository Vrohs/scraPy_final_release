'use client';

import { useParams } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import { scrapeService } from '@/services/scrape';
import ResultsView from '@/components/results/results-view';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';
import { useAuth } from '@clerk/nextjs';

export default function JobResultsPage() {
    const params = useParams();
    const id = params.id as string;
    const { getToken } = useAuth();

    const { data: job, isLoading, error } = useQuery({
        queryKey: ['job', id],
        queryFn: async () => {
            const token = await getToken();
            return scrapeService.getJob(id, token || undefined);
        },
        refetchInterval: (query) => {
            const status = query.state.data?.status;
            return status === 'completed' || status === 'failed' ? false : 2000;
        }
    });

    const saveMutation = useMutation({
        mutationFn: async (jobId: string) => {
            const token = await getToken();
            return scrapeService.saveJob(jobId, token || undefined);
        },
        onSuccess: () => {
            toast.success("Job saved to database!");
        },
        onError: () => {
            toast.error("Failed to save job");
        }
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center h-screen space-y-4 text-destructive">
                <p>Failed to load job details.</p>
                <Link href="/scrape">
                    <Button variant="outline">Go Back</Button>
                </Link>
            </div>
        );
    }

    // const { toast } = useToast(); // Removed, using direct import

    // Format data for view (wrap single object in array)
    const resultsData = job?.data ? (Array.isArray(job.data) ? job.data : [job.data]) : [];

    return (
        <div className="space-y-6">
            <div className="flex items-center space-x-4">
                <Link href="/scrape">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <div className="flex flex-col space-y-1">
                    <h1 className="text-2xl font-bold tracking-tight">Job Results</h1>
                    <p className="text-sm text-muted-foreground">
                        ID: {id} • Status: <span className="capitalize font-medium">{job?.status}</span>
                    </p>
                </div>
            </div>

            <ResultsView
                data={resultsData}
                status={job?.status || 'pending'}
                jobId={id}
                onSave={() => saveMutation.mutate(id)}
            />
        </div>
    );
}
