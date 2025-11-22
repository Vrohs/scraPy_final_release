import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';
import { DashboardStats } from '@/components/DashboardStats';

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <section className="space-y-4 pb-8 pt-6 md:pb-12 md:pt-10 lg:py-32">
        <div className="container mx-auto flex max-w-[64rem] flex-col items-center gap-4 text-center">
          <h1 className="font-heading text-3xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight">
            Extract data from any website
          </h1>
          <p className="max-w-[42rem] leading-normal text-muted-foreground sm:text-xl sm:leading-8">
            Turn websites into structured data with our intelligent scraping platform.
            Use guided selectors or let AI do the work for you.
          </p>
          <div className="space-x-4">
            <Link href="/scrape">
              <Button size="lg" className="gap-2">
                Start Scraping <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/history">
              <Button variant="outline" size="lg">
                View History
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <DashboardStats />
    </div>
  );
}

