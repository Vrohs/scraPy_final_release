import { test, expect } from '@playwright/test';

test('scrape flow', async ({ page }) => {
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));

    // Mock Clerk auth by setting cookies or bypassing (if possible)
    // For now, we assume the app is accessible or we handle the redirect

    // Go to home
    await page.goto('/');

    // If redirected to sign-in (due to auth), we might be stuck if we don't have credentials.
    // However, we are running locally.
    // Let's assume we can access /scrape if we are "signed in" or if we disabled middleware.

    // Navigate to scrape page
    await page.goto('/scrape');

    // Fill form
    await page.getByLabel('Target URL').fill('https://example.com');
    await page.getByRole('tab', { name: 'Guided Mode' }).click();

    // Add selector
    await page.getByPlaceholder('Field Name').fill('title');
    await page.getByPlaceholder('CSS Selector').fill('h1');

    // Submit
    await page.getByRole('button', { name: 'Start Scraping' }).click();

    // Expect redirect to results
    await expect(page).toHaveURL(/\/scrape\/[a-f0-9-]+/);

    // Wait for results
    await expect(page.getByText('Example Domain')).toBeVisible({ timeout: 30000 });

    // Check status
    await expect(page.getByText('completed', { exact: false })).toBeVisible();

    // Save
    await page.getByRole('button', { name: 'Save to DB' }).click();
    await expect(page.getByText('Job saved')).toBeVisible();

    // Check history
    await page.goto('/history');
    await expect(page.getByText('https://example.com').first()).toBeVisible();
});
