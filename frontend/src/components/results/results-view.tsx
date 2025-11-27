'use client';

import { useState } from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Download, FileJson, FileSpreadsheet, Copy } from 'lucide-react';

interface ResultsViewProps {
    data: any[];
    status: 'pending' | 'processing' | 'completed' | 'failed' | 'saved';
    jobId: string;
    onSave?: () => void;
}

export default function ResultsView({ data, status, jobId, onSave }: ResultsViewProps) {
    const [activeTab, setActiveTab] = useState('table');

    if (status === 'processing' || status === 'pending') {
        return (
            <div className="flex flex-col items-center justify-center h-64 space-y-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <p className="text-muted-foreground">Scraping in progress...</p>
            </div>
        );
    }

    if (status === 'failed') {
        return (
            <div className="flex flex-col items-center justify-center h-64 space-y-4 text-destructive">
                <p className="font-semibold">Scraping failed</p>
                <p className="text-sm text-muted-foreground">{(data as any)?.error || "Unknown error occurred"}</p>
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-64 space-y-4">
                <p className="text-muted-foreground">No data found.</p>
            </div>
        );
    }

    const headers = Object.keys(data[0]);

    const downloadJson = () => {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `scrape-${jobId}.json`;
        a.click();
    };

    const downloadCsv = () => {
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(header => JSON.stringify(row[header])).join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `scrape-${jobId}.csv`;
        a.click();
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <h2 className="text-lg font-semibold">Results</h2>
                    <Badge variant="outline">{data.length} items</Badge>
                </div>
                <div className="flex space-x-2">
                    {onSave && (
                        <Button variant="default" size="sm" onClick={onSave}>
                            Save to DB
                        </Button>
                    )}
                    <Button variant="outline" size="sm" onClick={downloadJson}>
                        <FileJson className="mr-2 h-4 w-4" />
                        JSON
                    </Button>
                    <Button variant="outline" size="sm" onClick={downloadCsv}>
                        <FileSpreadsheet className="mr-2 h-4 w-4" />
                        CSV
                    </Button>
                </div>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList>
                    <TabsTrigger value="table">Table View</TabsTrigger>
                    <TabsTrigger value="json">JSON View</TabsTrigger>
                </TabsList>

                <TabsContent value="table" className="border rounded-md">
                    <ScrollArea className="h-[500px]">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    {headers.map((header) => (
                                        <TableHead key={header}>{header}</TableHead>
                                    ))}
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {data.map((row, i) => (
                                    <TableRow key={i}>
                                        {headers.map((header) => (
                                            <TableCell key={`${i}-${header}`}>
                                                {typeof row[header] === 'object'
                                                    ? JSON.stringify(row[header])
                                                    : String(row[header])}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </ScrollArea>
                </TabsContent>

                <TabsContent value="json">
                    <div className="relative border rounded-md bg-muted/50 p-4 h-[500px] overflow-auto">
                        <Button
                            variant="ghost"
                            size="icon"
                            className="absolute top-2 right-2"
                            onClick={() => navigator.clipboard.writeText(JSON.stringify(data, null, 2))}
                        >
                            <Copy className="h-4 w-4" />
                        </Button>
                        <pre className="text-sm font-mono">
                            {JSON.stringify(data, null, 2)}
                        </pre>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}
