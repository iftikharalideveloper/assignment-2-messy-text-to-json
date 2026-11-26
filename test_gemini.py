import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from schema import Extracted


def main():
    # Load API key and model settings from .env
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env", file=sys.stderr)
        raise SystemExit(1)

    # Connect to Gemini
    client = genai.Client(api_key=api_key)

    try:
        # Send a real request with structured JSON output
        response = client.models.generate_content(
            model=model,
            contents=(
                "Extract job information from this job post. "
                "Use only explicitly provided information. "
                "Job title: Python Developer. "
                "Company: ABC Tech. "
                "Location: Remote. "
                "Employment: Full-time. "
                "Required skills: Python and REST APIs."
            ),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=Extracted.model_json_schema(),
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        # Validate Gemini's JSON using our Pydantic model
        result = Extracted.model_validate_json(response.text)

        print(result.model_dump_json(indent=2))

    finally:
        client.close()


if __name__ == "__main__":
    main()
