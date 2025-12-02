import { z } from 'zod';

export const scrapeFormSchema = z.object({
  url: z.string().url({ message: 'Please enter a valid URL' }),
  mode: z.enum(['guided', 'smart']),
  selectors: z
    .array(
      z.object({
        key: z.string().min(1, { message: 'Field name is required' }),
        selector: z.string().min(1, { message: 'Selector is required' }),
      })
    )
    .optional(),
  instruction: z.string().optional(),
  options: z.object({
    useProxy: z.boolean().default(false),
    renderJs: z.boolean().default(false),
  }),
});

export type ScrapeFormData = z.infer<typeof scrapeFormSchema>;
