import { z } from 'zod';

export const scrapeFormSchema = z.object({
    url: z.string().url({ message: 'Please enter a valid URL' }),
    mode: z.enum(['guided', 'smart']),
    selectors: z.array(z.object({
        key: z.string().min(1, 'Key is required'),
        selector: z.string().min(1, 'Selector is required'),
    })).optional(),
    instruction: z.string().optional(),
    options: z.object({
        useProxy: z.boolean(),
        renderJs: z.boolean(),
    }),
}).refine((data) => {
    if (data.mode === 'guided') {
        return data.selectors && data.selectors.length > 0;
    }
    if (data.mode === 'smart') {
        return !!data.instruction;
    }
    return true;
}, {
    message: "Please provide selectors for Guided mode or instructions for Smart mode",
    path: ["mode"], // This might need adjustment to show error correctly
});

export type ScrapeFormData = z.infer<typeof scrapeFormSchema>;
