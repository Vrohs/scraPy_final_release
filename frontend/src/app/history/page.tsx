'use client';

import { useQuery } from '@tanstack/react-query';
import { scrapeService } from '@/services/scrape';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { Eye } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

import { useAuth } from '@clerk/nextjs';

export default function HistoryPage() {
    const { getToken } = useAuth();
    const { data: jobs, isLoading } = useQuery({
        queryKey: ['history'],
        queryFn: async () => {
            const token = await getToken();
            return scrapeService.getHistory(token || undefined);
        },
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-bold tracking-tight">History</h1>
                <p className="text-muted-foreground">
                    View your past scraping jobs.
                </p>
            </div>

            <div className="border rounded-md">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>URL</TableHead>
                            <TableHead>Mode</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Created</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {jobs?.map((job) => (
                            <TableRow key={job.job_id || job.id}>
                                <TableCell className="font-medium truncate max-w-[300px]">
                                    {job.url}
                                </TableCell>
                                <TableCell>
                                    <Badge variant="outline" className="capitalize">
                                        {job.mode}
                                    </Badge>
                                </TableCell>
                                <TableCell>
                                    <Badge
                                        variant={job.status === 'completed' ? 'default' : 'secondary'}
                                        className="capitalize"
                                    >
                                        {job.status}
                                    </Badge>
                                </TableCell>
                                <TableCell>
                                    {job.created_at && formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                                </TableCell>
                                <TableCell className="text-right">
                                    <Link href={`/scrape/${job.job_id || job.id}`}>
                                        <Button variant="ghost" size="icon">
                                            <Eye className="h-4 w-4" />
                                        </Button>
                                    </Link>
                                </TableCell>
                            </TableRow>
                        ))}
                        {(!jobs || jobs.length === 0) && (
                            <TableRow>
                                <TableCell colSpan={5} className="h-24 text-center">
                                    No jobs found.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
