'use client';

import { useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiKeyService, ApiKey } from '@/services/api-keys';
import { webhookService, Webhook } from '@/services/webhook';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';
import { Trash2, Plus, Copy, Check } from 'lucide-react';
import { toast } from 'sonner';
import { formatDistanceToNow } from 'date-fns';

export default function SettingsPage() {
    const { getToken } = useAuth();
    const queryClient = useQueryClient();
    const [newKeyName, setNewKeyName] = useState('');
    const [createdKey, setCreatedKey] = useState<string | null>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [copied, setCopied] = useState(false);

    // Webhook state
    const [newWebhookUrl, setNewWebhookUrl] = useState('');
    const [isWebhookDialogOpen, setIsWebhookDialogOpen] = useState(false);

    const { data: keys, isLoading } = useQuery({
        queryKey: ['api-keys'],
        queryFn: async () => {
            const token = await getToken();
            if (!token) return [];
            return apiKeyService.listKeys(token);
        },
    });

    const { data: webhooks, isLoading: isLoadingWebhooks } = useQuery({
        queryKey: ['webhooks'],
        queryFn: async () => {
            const token = await getToken();
            if (!token) return [];
            return webhookService.listWebhooks(token);
        },
    });

    const createMutation = useMutation({
        mutationFn: async (name: string) => {
            const token = await getToken();
            if (!token) throw new Error("Not authenticated");
            return apiKeyService.createKey(name, token);
        },
        onSuccess: (data) => {
            setCreatedKey(data.key || null);
            setNewKeyName('');
            queryClient.invalidateQueries({ queryKey: ['api-keys'] });
            toast.success("API Key created successfully");
        },
        onError: () => {
            toast.error("Failed to create API Key");
        }
    });

    const revokeMutation = useMutation({
        mutationFn: async (id: string) => {
            const token = await getToken();
            if (!token) throw new Error("Not authenticated");
            return apiKeyService.revokeKey(id, token);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['api-keys'] });
            toast.success("API Key revoked");
        },
        onError: () => {
            toast.error("Failed to revoke API Key");
        }
    });

    const createWebhookMutation = useMutation({
        mutationFn: async (url: string) => {
            const token = await getToken();
            if (!token) throw new Error("Not authenticated");
            return webhookService.createWebhook(url, token);
        },
        onSuccess: () => {
            setNewWebhookUrl('');
            queryClient.invalidateQueries({ queryKey: ['webhooks'] });
            toast.success("Webhook created successfully");
        },
        onError: () => {
            toast.error("Failed to create Webhook");
        }
    });

    const deleteWebhookMutation = useMutation({
        mutationFn: async (id: string) => {
            const token = await getToken();
            if (!token) throw new Error("Not authenticated");
            return webhookService.deleteWebhook(id, token);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['webhooks'] });
            toast.success("Webhook deleted");
        },
        onError: () => {
            toast.error("Failed to delete Webhook");
        }
    });

    const handleCreate = () => {
        if (!newKeyName.trim()) return;
        createMutation.mutate(newKeyName);
    };

    const handleCopy = () => {
        if (createdKey) {
            navigator.clipboard.writeText(createdKey);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
            toast.success("Copied to clipboard");
        }
    };

    const handleCreateWebhook = () => {
        if (!newWebhookUrl.trim()) return;
        createWebhookMutation.mutate(newWebhookUrl);
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
                <p className="text-muted-foreground">
                    Manage your API keys and webhooks.
                </p>
            </div>

            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle>API Keys</CardTitle>
                            <CardDescription>
                                Manage API keys for accessing the scraPy API programmatically.
                            </CardDescription>
                        </div>
                        <Dialog open={isDialogOpen} onOpenChange={(open: boolean) => {
                            setIsDialogOpen(open);
                            if (!open) setCreatedKey(null); // Reset on close
                        }}>
                            <DialogTrigger asChild>
                                <Button>
                                    <Plus className="mr-2 h-4 w-4" />
                                    Create New Key
                                </Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Create API Key</DialogTitle>
                                    <DialogDescription>
                                        Enter a name for your new API key.
                                    </DialogDescription>
                                </DialogHeader>

                                {!createdKey ? (
                                    <div className="grid gap-4 py-4">
                                        <Input
                                            placeholder="Key Name (e.g. Production)"
                                            value={newKeyName}
                                            onChange={(e) => setNewKeyName(e.target.value)}
                                        />
                                    </div>
                                ) : (
                                    <div className="space-y-4 py-4">
                                        <div className="rounded-md bg-muted p-4">
                                            <p className="text-sm font-medium mb-2">Your API Key</p>
                                            <div className="flex items-center justify-between bg-background border rounded p-2">
                                                <code className="text-sm font-mono break-all">{createdKey}</code>
                                                <Button variant="ghost" size="icon" onClick={handleCopy}>
                                                    {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                                                </Button>
                                            </div>
                                        </div>
                                        <div className="text-sm text-muted-foreground text-yellow-600 bg-yellow-50 p-3 rounded border border-yellow-200">
                                            <strong>Important:</strong> Copy this key now. You won't be able to see it again!
                                        </div>
                                    </div>
                                )}

                                <DialogFooter>
                                    {!createdKey ? (
                                        <Button onClick={handleCreate} disabled={createMutation.isPending || !newKeyName.trim()}>
                                            {createMutation.isPending ? "Creating..." : "Create Key"}
                                        </Button>
                                    ) : (
                                        <Button onClick={() => setIsDialogOpen(false)}>
                                            Done
                                        </Button>
                                    )}
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>
                    </div>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Name</TableHead>
                                <TableHead>Key Prefix</TableHead>
                                <TableHead>Created</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {keys?.map((key) => (
                                <TableRow key={key.id}>
                                    <TableCell className="font-medium">{key.name}</TableCell>
                                    <TableCell className="font-mono">{key.key_prefix}...</TableCell>
                                    <TableCell>
                                        {formatDistanceToNow(new Date(key.created_at), { addSuffix: true })}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            onClick={() => revokeMutation.mutate(key.id)}
                                            disabled={revokeMutation.isPending}
                                        >
                                            <Trash2 className="h-4 w-4 text-destructive" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                            {(!keys || keys.length === 0) && (
                                <TableRow>
                                    <TableCell colSpan={4} className="h-24 text-center text-muted-foreground">
                                        No API keys found. Create one to get started.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle>Webhooks</CardTitle>
                            <CardDescription>
                                Receive real-time notifications when jobs are completed.
                            </CardDescription>
                        </div>
                        <Dialog open={isWebhookDialogOpen} onOpenChange={setIsWebhookDialogOpen}>
                            <DialogTrigger asChild>
                                <Button variant="outline">
                                    <Plus className="mr-2 h-4 w-4" />
                                    Add Webhook
                                </Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Add Webhook</DialogTitle>
                                    <DialogDescription>
                                        Enter the URL where you want to receive notifications.
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="grid gap-4 py-4">
                                    <Input
                                        placeholder="https://your-api.com/webhook"
                                        value={newWebhookUrl}
                                        onChange={(e) => setNewWebhookUrl(e.target.value)}
                                    />
                                </div>
                                <DialogFooter>
                                    <Button onClick={handleCreateWebhook} disabled={createWebhookMutation.isPending || !newWebhookUrl.trim()}>
                                        {createWebhookMutation.isPending ? "Adding..." : "Add Webhook"}
                                    </Button>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>
                    </div>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>URL</TableHead>
                                <TableHead>Events</TableHead>
                                <TableHead>Created</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {webhooks?.map((webhook) => (
                                <TableRow key={webhook.id}>
                                    <TableCell className="font-medium truncate max-w-[300px]">{webhook.url}</TableCell>
                                    <TableCell>
                                        {webhook.events.map(e => (
                                            <span key={e} className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
                                                {e}
                                            </span>
                                        ))}
                                    </TableCell>
                                    <TableCell>
                                        {formatDistanceToNow(new Date(webhook.created_at), { addSuffix: true })}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            onClick={() => deleteWebhookMutation.mutate(webhook.id)}
                                            disabled={deleteWebhookMutation.isPending}
                                        >
                                            <Trash2 className="h-4 w-4 text-destructive" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                            {(!webhooks || webhooks.length === 0) && (
                                <TableRow>
                                    <TableCell colSpan={4} className="h-24 text-center text-muted-foreground">
                                        No webhooks configured.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
