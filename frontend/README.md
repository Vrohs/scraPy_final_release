# scraPy Frontend

**Modern Next.js 16 web interface with React 19 and real-time job monitoring**

---

## Overview

Professional web interface for scraPy built with Next.js App Router, featuring:

- 🎨 **Modern UI** - Radix UI + TailwindCSS
- 🔐 **Clerk Authentication** - Secure user management
- 📊 **Real-time Updates** - React Query with smart polling
- 🚀 **Server Components** - Optimized performance
- 📱 **Responsive Design** - Mobile-first approach
- ⚡ **Bundle Optimization** - Lazy loading & code splitting

---

## Tech Stack

### Core

- **Framework:** Next.js 16.0.3 (App Router)
- **React:** 19.2.0 with React Compiler
- **TypeScript:** Latest
- **Node:** 18+

### UI & Styling

- **UI Library:** Radix UI (Unstyled components)
- **Styling:** TailwindCSS 3.4+
- **Icons:** Lucide React
- **Notifications:** Sonner (Toast)

### State & Data

- **Data Fetching:** TanStack Query (React Query v5)
- **HTTP Client:** Axios
- **Forms:** React Hook Form
- **Validation:** Zod
- **State:** Zustand (minimal usage)

### Authentication

- **Provider:** Clerk
- **Method:** JWT tokens
- **Routes:** Middleware-protected

---

## Quick Start

### Installation

```bash
# Install dependencies
npm install

# Set up environment
cp .env.local.example .env.local
# Edit .env.local with your credentials
```

### Environment Variables

Create `.env.local`:

```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx
```

### Development

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test
```

### Access

- **Development:** http://localhost:3000
- **API Proxy:** Requests to `/api/*` proxied to backend

---

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Dashboard (/)
│   │   ├── scrape/
│   │   │   ├── page.tsx        # Scrape form
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Job results
│   │   ├── history/
│   │   │   └── page.tsx        # Job history
│   │   ├── api-keys/
│   │   │   └── page.tsx        # API key management
│   │   ├── webhooks/
│   │   │   └── page.tsx        # Webhook management
│   │   └── sign-in/
│   │       └── [[...sign-in]]/
│   │           └── page.tsx    # Clerk sign-in
│   ├── components/
│   │   ├── ui/                 # Radix UI components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── ...
│   │   ├── scrape-form.tsx     # Main scrape form
│   │   ├── results/
│   │   │   ├── results-view.tsx
│   │   │   └── result-card.tsx
│   │   ├── DashboardStats.tsx
│   │   └── error-boundary.tsx
│   ├── services/
│   │   ├── scrape.ts           # Scrape API client
│   │   ├── api-keys.ts         # API key operations
│   │   └── webhook.ts          # Webhook operations
│   ├── lib/
│   │   ├── api.ts              # Axios instance
│   │   └── utils.ts            # Utilities
│   └── middleware.ts           # Clerk auth middleware
├── public/                     # Static assets
├── tests/
│   └── e2e.spec.ts            # Playwright E2E tests
├── tailwind.config.ts          # TailwindCSS config
├── next.config.ts              # Next.js config
└── package.json
```

---

## Pages

### Dashboard (`/`)

**Features:**
- Welcome message
- Quick stats (total jobs, completed, average time)
- CTA to start scraping

**Components:**
- `DashboardStats` - Fetches and displays stats

**API Calls:**
```typescript
const { data: stats } = useQuery({
  queryKey: ['stats'],
  queryFn: () => api.get<Stats>('/stats')
});
```

### Scrape Form (`/scrape`)

**Features:**
- URL input with validation
- Mode selection (Guided/Smart)
- Dynamic form fields based on mode
- Option toggles (renderJs)
- Real-time submission

**Form Validation:**
```typescript
const schema = z.object({
  url: z.string().url(),
  mode: z.enum(['guided', 'smart']),
  selectors: z.record(z.string()).optional(),
  instruction: z.string().optional(),
  options: z.object({
    renderJs: z.boolean()
  })
});
```

### Job Results (`/scrape/[id]`)

**Features:**
- Real-time status polling (2s interval)
- Auto-stop when completed/failed
- Result display with JSON viewer
- Save to database button

**Polling Logic:**
```typescript
const { data: job } = useQuery({
  queryKey: ['job', id],
  queryFn: async () => {
    const token = await getToken();
    return scrapeService.getJob(id, token);
  },
  refetchInterval: (query) => {
    const status = query.state.data?.status;
    return status === 'completed' || status === 'failed' 
      ? false 
      : 2000;
  }
});
```

### Job History (`/history`)

**Features:**
- List all saved jobs
- Filterable by status
- Sortable by date
- Click to view details

### API Keys (`/api-keys`)

**Features:**
- List active API keys
- Create new keys (one-time display)
- Revoke keys
- Copy to clipboard

### Webhooks (`/webhooks`)

**Features:**
- List active webhooks
- Create webhook with URL
- Test webhook
- Delete webhook

---

## Services

### Scrape Service (`services/scrape.ts`)

```typescript
export const scrapeService = {
  // Create scraping job
  createJob: async (data: ScrapeFormData, token?: string) => {
    const headers = token 
      ? { Authorization: `Bearer ${token}` } 
      : undefined;
    const response = await api.post('/scrape', data, { headers });
    return response.data;
  },

  // Get job status
  getJob: async (id: string, token?: string) => {
    const headers = token 
      ? { Authorization: `Bearer ${token}` } 
      : undefined;
    const response = await api.get(`/scrape/${id}`, { headers });
    return response.data;
  },

  // Save job to database
  saveJob: async (id: string, token?: string) => {
    const headers = token 
      ? { Authorization: `Bearer ${token}` } 
      : undefined;
    const response = await api.post(`/scrape/${id}/save`, {}, { headers });
    return response.data;
  },

  // Get job history
  getHistory: async (token?: string) => {
    const headers = token 
      ? { Authorization: `Bearer ${token}` } 
      : undefined;
    const response = await api.get('/scrape/history/all', { headers });
    return response.data;
  }
};
```

### API Keys Service (`services/api-keys.ts`)

```typescript
export const apiKeyService = {
  listKeys: async (token: string) => {
    const response = await api.get('/api_keys', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  createKey: async (name: string, token: string) => {
    const response = await api.post('/api_keys', 
      { name },
      { headers: { Authorization: `Bearer ${token}` }}
    );
    return response.data;
  },

  revokeKey: async (keyId: string, token: string) => {
    await api.delete(`/api_keys/${keyId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
  }
};
```

---

## Authentication

### Clerk Integration

**Setup:**
```typescript
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs';

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html>
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

**Protected Routes:**
```typescript
// middleware.ts
import { clerkMiddleware } from '@clerk/nextjs/server';

export default clerkMiddleware();

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
};
```

**Getting Token:**
```typescript
import { useAuth } from '@clerk/nextjs';

const { getToken } = useAuth();
const token = await getToken();
```

---

## State Management

### React Query Setup

```typescript
// app/providers.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      refetchOnWindowFocus: false,
    },
  },
});

export function Providers({ children }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

### Query Keys

```typescript
// Organized query keys
const queryKeys = {
  stats: ['stats'],
  job: (id: string) => ['job', id],
  history: ['history'],
  apiKeys: ['apiKeys'],
  webhooks: ['webhooks']
};
```

---

## Styling

### TailwindCSS Configuration

```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        // ...
      }
    }
  },
  plugins: [require("tailwindcss-animate")]
};
```

### Component Patterns

```tsx
// Radix UI + TailwindCSS
import { Button } from "@/components/ui/button";

<Button variant="default" size="lg">
  Click me
</Button>

// Variants: default, destructive, outline, secondary, ghost, link
// Sizes: default, sm, lg, icon
```

---

## Bundle Optimization

### Next.js Config

```typescript
// next.config.ts
const nextConfig = {
  reactCompiler: true, // React 19 compiler
  
  experimental: {
    // Optimize Radix UI imports
    optimizePackageImports: [
      '@radix-ui/react-avatar',
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      // ...
    ],
  },
};
```

### Code Splitting

```typescript
// Dynamic imports for heavy components
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <Skeleton />,
  ssr: false
});
```

---

## Testing

### E2E Tests (Playwright)

```bash
# Run tests
npx playwright test

# Run with UI
npx playwright test --ui

# Run specific test
npx playwright test tests/e2e.spec.ts
```

**Test Example:**
```typescript
test('complete scrape flow', async ({ page }) => {
  await page.goto('/scrape');
  
  // Fill form
  await page.fill('input[name="url"]', 'https://example.com');
  await page.click('button[type="submit"]');
  
  // Wait for results
  await page.waitForSelector('[data-testid="results"]');
  
  // Verify data
  const results = await page.textContent('[data-testid="results"]');
  expect(results).toContain('Example Domain');
});
```

---

## Deployment

### Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Link project
vercel link

# Deploy
vercel --prod
```

### Environment Variables (Production)

Set in Vercel dashboard:

```bash
NEXT_PUBLIC_API_URL=https://your-api.railway.app
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_xxx
CLERK_SECRET_KEY=sk_live_xxx
```

### Build Optimization

```bash
# Check bundle size
npm run build

# Analyze bundle
npm install -D @next/bundle-analyzer
ANALYZE=true npm run build
```

---

## Performance

### Optimization Techniques

1. **Server Components** - Default for pages
2. **Client Components** - Only for interactivity
3. **Image Optimization** - Next.js Image component
4. **Font Optimization** - next/font
5. **Code Splitting** - Dynamic imports
6. **Lazy Loading** - React.lazy
7. **Memoization** - React.memo, useMemo
8. **Debouncing** - Input fields

### Bundle Size

- **Production Build:** ~150KB gzipped
- **First Load JS:** ~200KB
- **Shared chunks:** ~80KB

---

## Troubleshooting

### Build Errors

```bash
# Clear cache
rm -rf .next
npm run build

# Check TypeScript
npm run type-check

# Lint
npm run lint
```

### Runtime Errors

```bash
# Check console for errors
# Verify environment variables
# Check API connectivity
curl $NEXT_PUBLIC_API_URL/health
```

### Authentication Issues

```bash
# Verify Clerk keys
# Check middleware config
# Ensure publishable key starts with pk_
```

---

## Contributing

See main [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## License

MIT - See [LICENSE](../LICENSE)
