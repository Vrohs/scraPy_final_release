import ScrapeForm from "@/components/scrape/scrape-form";

export default function ScrapePage() {
    return (
        <div className="space-y-6">
            <div className="flex flex-col items-center justify-center text-center space-y-2">
                <h1 className="text-3xl font-bold tracking-tight">New Scraping Job</h1>
                <p className="text-muted-foreground">
                    Configure your scraping parameters below.
                </p>
            </div>
            <ScrapeForm />
        </div>
    );
}
