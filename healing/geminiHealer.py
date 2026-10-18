import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

class GeminiHealer:

    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    def suggestLocator(self, originalLocator, candidates):

        prompt = f"""
        You are helping repair a broken Playwright locator.

        Original locator: {originalLocator}

        Available HTML elements:
        {candidates}

        Identify the most likely replacement element.

        Return only its CSS selector.
        If uncertain, return NONE.
        """

        response = self.client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        return response.text.strip()