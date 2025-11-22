'use client';

import { useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { scrapeFormSchema, type ScrapeFormData } from '@/lib/validators';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { scrapeService } from '@/services/scrape';
import { toast } from 'sonner';
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from '@/components/ui/form';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Plus, Trash2, Loader2 } from 'lucide-react';

export default function ScrapeForm() {
    // const [isLoading, setIsLoading] = useState(false); // Removed unused state

    const form = useForm<ScrapeFormData>({
        resolver: zodResolver(scrapeFormSchema),
        defaultValues: {
            mode: 'guided',
            url: '',
            selectors: [{ key: '', selector: '' }],
            instruction: '',
            options: {
                useProxy: false,
                renderJs: false,
            },
        },
    });

    const { fields, append, remove } = useFieldArray({
        control: form.control,
        name: 'selectors',
    });

    const router = useRouter();
    const { getToken } = useAuth();
    // const { toast } = useToast(); // Removed, using direct import

    const mutation = useMutation({
        mutationFn: async (data: ScrapeFormData) => {
            const token = await getToken();
            return scrapeService.createJob(data, token || undefined);
        },
        onSuccess: (data) => {
            toast.success("Job started successfully!");
            router.push(`/scrape/${data.job_id}`);
        },
        onError: (error) => {
            toast.error("Failed to start job");
            console.error(error);
        }
    });

    function onSubmit(data: ScrapeFormData) {
        mutation.mutate(data);
    }

    return (
        <Card className="w-full max-w-2xl mx-auto">
            <CardHeader>
                <CardTitle>Start Scraping</CardTitle>
                <CardDescription>
                    Choose your preferred method to extract data.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                        <FormField
                            control={form.control}
                            name="url"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Target URL</FormLabel>
                                    <FormControl>
                                        <Input placeholder="https://example.com" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <Tabs
                            defaultValue="guided"
                            onValueChange={(value) => form.setValue('mode', value as 'guided' | 'smart')}
                            className="w-full"
                        >
                            <TabsList className="grid w-full grid-cols-2">
                                <TabsTrigger value="guided">Guided Mode</TabsTrigger>
                                <TabsTrigger value="smart">Smart Mode</TabsTrigger>
                            </TabsList>

                            <TabsContent value="guided" className="space-y-4 mt-4">
                                <div className="space-y-4">
                                    <div className="flex items-center justify-between">
                                        <FormLabel>Data Selectors</FormLabel>
                                        <Button
                                            type="button"
                                            variant="outline"
                                            size="sm"
                                            onClick={() => append({ key: '', selector: '' })}
                                        >
                                            <Plus className="h-4 w-4 mr-2" />
                                            Add Field
                                        </Button>
                                    </div>
                                    {fields.map((field, index) => (
                                        <div key={field.id} className="flex gap-4 items-start">
                                            <FormField
                                                control={form.control}
                                                name={`selectors.${index}.key`}
                                                render={({ field }) => (
                                                    <FormItem className="flex-1">
                                                        <FormControl>
                                                            <Input placeholder="Field Name (e.g. price)" {...field} />
                                                        </FormControl>
                                                        <FormMessage />
                                                    </FormItem>
                                                )}
                                            />
                                            <FormField
                                                control={form.control}
                                                name={`selectors.${index}.selector`}
                                                render={({ field }) => (
                                                    <FormItem className="flex-[2]">
                                                        <FormControl>
                                                            <Input placeholder="CSS Selector (e.g. .product-price)" {...field} />
                                                        </FormControl>
                                                        <FormMessage />
                                                    </FormItem>
                                                )}
                                            />
                                            <Button
                                                type="button"
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => remove(index)}
                                                disabled={fields.length === 1}
                                            >
                                                <Trash2 className="h-4 w-4 text-destructive" />
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            </TabsContent>

                            <TabsContent value="smart" className="space-y-4 mt-4">
                                <FormField
                                    control={form.control}
                                    name="instruction"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Instructions</FormLabel>
                                            <FormControl>
                                                <Textarea
                                                    placeholder="Describe what data you want to extract in plain English..."
                                                    className="min-h-[100px]"
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormDescription>
                                                Our AI will analyze the page and extract the data based on your description.
                                            </FormDescription>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                            </TabsContent>
                        </Tabs>

                        <div className="flex gap-6 pt-4 border-t">
                            <FormField
                                control={form.control}
                                name="options.useProxy"
                                render={({ field }) => (
                                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm flex-1">
                                        <div className="space-y-0.5">
                                            <FormLabel>Use Proxy</FormLabel>
                                            <FormDescription>
                                                Rotate IP addresses
                                            </FormDescription>
                                        </div>
                                        <FormControl>
                                            <Switch
                                                checked={field.value}
                                                onCheckedChange={field.onChange}
                                            />
                                        </FormControl>
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="options.renderJs"
                                render={({ field }) => (
                                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm flex-1">
                                        <div className="space-y-0.5">
                                            <FormLabel>Render JS</FormLabel>
                                            <FormDescription>
                                                Use headless browser
                                            </FormDescription>
                                        </div>
                                        <FormControl>
                                            <Switch
                                                checked={field.value}
                                                onCheckedChange={field.onChange}
                                            />
                                        </FormControl>
                                    </FormItem>
                                )}
                            />
                        </div>

                        <Button type="submit" className="w-full" disabled={mutation.isPending}>
                            {mutation.isPending ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Starting Job...
                                </>
                            ) : (
                                'Start Scraping'
                            )}
                        </Button>
                    </form>
                </Form>
            </CardContent>
        </Card>
    );
}
