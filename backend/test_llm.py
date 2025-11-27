import asyncio
import os
import google.generativeai as genai
from app.services.llm import analyze_page
from app.core.config import settings

async def test_llm():
    print(f"Testing LLM with API Key: {settings.GEMINI_API_KEY[:5]}..." if settings.GEMINI_API_KEY else "No API Key found")
    
    html = """
    <html>
        <body>
            <h1>Welcome to ScraPy</h1>
            <p>This is a test page.</p>
            <div class="content">Some interesting data here.</div>
        </body>
    </html>
    """
    
    instruction = "Extract the title and the content text."
    result = await analyze_page(html, instruction)
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(test_llm())
