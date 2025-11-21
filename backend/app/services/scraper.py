import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from typing import Dict, Any, Optional

async def scrape_static(url: str, selectors: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": "ScrapeFlow/1.0"})
        response.raise_for_status()
        html = response.text
        
        if not selectors:
            return {"html": html}
            
        soup = BeautifulSoup(html, "html.parser")
        data = {}
        for key, selector in selectors.items():
            element = soup.select_one(selector)
            data[key] = element.get_text(strip=True) if element else None
            
        return data

async def scrape_dynamic(url: str, selectors: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            
            if not selectors:
                content = await page.content()
                return {"html": content}
            
            data = {}
            for key, selector in selectors.items():
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        data[key] = text.strip() if text else None
                    else:
                        data[key] = None
                except Exception:
                    data[key] = None
            return data
        finally:
            await browser.close()

