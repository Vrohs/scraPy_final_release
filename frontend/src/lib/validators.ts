import { z } from 'zod';

export const scrapeFormSchema = z.object({
  url: z.string().url({ message: 'Please enter a valid URL' }),
  mode: z.enum(['guided', 'smart']),
  selectors: z.array(
    z.object({
      key: z.string(),
      selector: z.string(),
    })
  ).optional(),
  instruction: z.string().optional(),
  options: z.object({
    useProxy: z.boolean(),
    renderJs: z.boolean(),
  }),
}).superRefine((data, ctx) => {
  if (data.mode === 'guided') {
    if (!data.selectors || data.selectors.length === 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "At least one selector is required",
        path: ["selectors"]
      });
      return;
    }
    data.selectors.forEach((item, index) => {
      if (!item.key || item.key.trim() === "") {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Field name is required",
          path: ["selectors", index, "key"]
        });
      }
      if (!item.selector || item.selector.trim() === "") {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Selector is required",
          path: ["selectors", index, "selector"]
        });
      }
    });
  }

  if (data.mode === 'smart') {
    if (!data.instruction || data.instruction.trim() === "") {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Instructions are required for Smart Mode",
        path: ["instruction"]
      });
    }
  }
});

export type ScrapeFormData = z.infer<typeof scrapeFormSchema>;
