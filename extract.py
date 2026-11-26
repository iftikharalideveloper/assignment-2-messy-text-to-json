import argparse
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

from schema import Extracted

# Project paths
ROOT_DIR = Path(__file__).resolve().parent
PROMPT_PATH = ROOT_DIR / "prompts" / "extract.txt"
ENV_PATH = ROOT_DIR / ".env"


# All logs go to standard error
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)


def build_prompt(job_text: str) -> str:
    """Read the separate prompt file and insert the job-post text."""

    if not PROMPT_PATH.exists():
        raise RuntimeError("Prompt file not found: prompts/extract.txt")

    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

    if "{job_text}" not in prompt_template:
        raise RuntimeError("The prompt is missing the {job_text} placeholder.")

    # Encode input as a JSON string to keep untrusted text clearly separated.
    safe_job_text = json.dumps(job_text, ensure_ascii=False)

    return prompt_template.replace("{job_text}", safe_job_text)


def call_model(
    prompt: str,
    schema: type[BaseModel],
) -> str:
    """Send the prompt to Gemini and request structured JSON."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your local .env file.")

    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=schema.model_json_schema(),
            ),
        )
    finally:
        client.close()

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text


def ask(
    prompt: str,
    schema: type[BaseModel],
    tries: int = 3,
):
    """Ask Gemini, validate the JSON, and retry with validation errors."""

    if tries < 1:
        raise ValueError("tries must be at least 1.")

    # The assignment allows no more than 3 attempts.
    tries = min(tries, 3)

    message = prompt

    for attempt in range(1, tries + 1):
        logger.info("Model request attempt %s/%s", attempt, tries)

        response_text = call_model(message, schema)

        try:
            result = schema.model_validate_json(response_text)
            logger.info("Pydantic validation successful.")
            return result

        except ValidationError as error:
            logger.error(
                "Validation failed on attempt %s: %s",
                attempt,
                error,
            )

            if attempt < tries:
                message = (
                    f"{prompt}\n\n"
                    "YOUR PREVIOUS RESPONSE FAILED VALIDATION.\n"
                    "Correct the JSON using this Pydantic validation error:\n"
                    f"{error}\n\n"
                    "Return only corrected JSON matching the schema."
                )

    raise RuntimeError(f"Gemini did not return valid JSON after {tries} attempts.")


def main() -> int:
    """Command-line entry point."""

    parser = argparse.ArgumentParser(
        description="Extract structured information from messy job-post text."
    )

    parser.add_argument(
        "job_text",
        nargs="?",
        default="",
        help="The messy job-post text to extract information from.",
    )

    args = parser.parse_args()

    try:
        load_dotenv(dotenv_path=ENV_PATH)

        # Handle empty input without making an unnecessary API request.
        if not args.job_text.strip():
            logger.warning("Empty input received. Returning empty schema values.")
            result = Extracted()

        else:
            prompt = build_prompt(args.job_text)
            result = ask(prompt, Extracted, tries=3)

        # Standard output contains JSON only.
        print(result.model_dump_json(indent=2))
        return 0

    except Exception as error:
        # Errors are sent to standard error, never standard output.
        logger.error("Extraction failed: %s", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
