'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { UserButton, SignedIn, SignedOut, SignInButton } from '@clerk/nextjs';

export default function Navbar() {
    return (
        <nav className="border-b bg-background">
            <div className="container mx-auto flex h-16 items-center justify-between px-4">
                <Link href="/" className="flex items-center space-x-2">
                    <span className="text-xl font-bold">scraPy</span>
                </Link>

                <div className="flex items-center space-x-4">
                    <SignedIn>
                        <Link href="/scrape">
                            <Button variant="ghost" size="sm">
                                Scrape
                            </Button>
                        </Link>
                        <Link href="/history">
                            <Button variant="ghost" size="sm">
                                History
                            </Button>
                        </Link>
                        <UserButton afterSignOutUrl="/" />
                    </SignedIn>
                    <SignedOut>
                        <SignInButton mode="modal">
                            <Button variant="default" size="sm">
                                Sign In
                            </Button>
                        </SignInButton>
                    </SignedOut>
                </div>
            </div>
        </nav>
    );
}
