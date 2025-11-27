import google.generativeai as genai
from app.core.config import settings
from typing import Dict, Any
import json

if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

async def analyze_page(html_content: str, instruction: str) -> Dict[str, Any]:
    if not settings.GEMINI_API_KEY:
        return {"error": "Gemini API key not configured"}

    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Truncate HTML to fit context window if necessary (simple approach)
    truncated_html = html_content[:30000] 
    
    prompt = f"""
    You are a web scraping assistant. Extract data from the following HTML based on the user's instruction.
    Return ONLY a valid JSON object. Do not include markdown formatting.
    
    Instruction: {instruction}
    
    HTML:
    {truncated_html}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean up potential markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}
