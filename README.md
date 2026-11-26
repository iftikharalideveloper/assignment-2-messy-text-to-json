# Messy Text to JSON — Job Post Extractor

A Python command-line application that converts messy, unstructured job-post text into clean, validated JSON using Google's Gemini API and Pydantic.

The application extracts job information, validates the response against a Pydantic schema, and retries when validation fails.

## Features

- Extracts structured information from messy job advertisements.
- Uses Gemini structured JSON output.
- Validates results with Pydantic.
- Retries validation failures by sending the error back to the model.
- Allows a maximum of three attempts.
- Supports missing information through optional fields.
- Keeps the extraction prompt in a separate file.
- Prints JSON only to standard output.
- Sends logs and errors to standard error.
- Includes tests for empty input, invalid responses, retries, and prompt-injection instructions.

## Extracted Information

The `Extracted` Pydantic model contains ten fields:

| Field             | Description                          |
| ----------------- | ------------------------------------ |
| `job_title`       | Advertised job position              |
| `company`         | Hiring company                       |
| `location`        | Job location                         |
| `employment_type` | Full-time, part-time, contract, etc. |
| `salary`          | Advertised compensation              |
| `experience`      | Required experience                  |
| `description`     | Job responsibilities                 |
| `requirements`    | Skills and qualifications            |
| `application_url` | Application link                     |
| `contact_email`   | Recruitment email                    |

Missing optional information is represented by `null`. Missing requirements are represented by an empty array.

## Requirements

- Python 3.11 or newer
- uv
- A Google Gemini API key

## Installation

Clone the repository:

```bash
git clone https://github.com/iftikharalideveloper/assignment-2-messy-text-to-json.git
cd assignment-2-messy-text-to-json
```

Install project dependencies:

```bash
uv sync
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key
GEMINI_MODEL=gemini-3.8-flash
```

Never commit the real `.env` file or share your API key.

## Usage

Run the application:

```bash
uv run extract.py "Hiring Python Developer at ABC Technologies. Location: Islamabad. Experience: 2 years."
```

The application returns structured JSON.

Example output:

```json
{
  "job_title": "Python Developer",
  "company": "ABC Technologies",
  "location": "Islamabad",
  "employment_type": null,
  "salary": null,
  "experience": "2 years",
  "description": null,
  "requirements": [],
  "application_url": null,
  "contact_email": null
}
```

The example illustrates the expected JSON structure; actual extracted values depend on the supplied job post and Gemini response.

## Empty Input

The application handles empty input without calling Gemini:

```bash
uv run extract.py ""
```

Missing fields are returned with their default values.

## Validation and Retry Mechanism

The application uses the following process:

1. Send the extraction prompt to Gemini.
2. Receive structured JSON.
3. Validate the JSON using Pydantic.
4. If validation fails, send the validation error back to Gemini.
5. Retry up to three total attempts.
6. Return a clear error if all attempts fail.

## Prompt Engineering

The extraction instructions are stored separately in:

```text
prompts/extract.txt
```

The prompt defines the AI role, extraction task, missing-value rules, output format, and security instructions.

Job-post content is treated as untrusted input.

## Testing

Run the automated test suite:

```bash
uv run python -m unittest discover -s tests -v
```

The tests cover:

- Empty input handling.
- Non-empty command-line workflow.
- API failure handling.
- Pydantic validation retries.
- Maximum three attempts.
- Five normal sample files.
- Four required edge cases.
- Prompt construction.
- Prompt-injection protection instructions.

The unit tests use mocked model responses where appropriate and do not require live Gemini API requests.

## Sample Data and Outputs

Five normal job-post samples are stored in:

```text
samples/
```

Special test cases are stored in:

```text
edge_cases/
```

These cover:

- Empty text.
- Another language.
- Junk text.
- Prompt injection.

Run the sample processing utility when Gemini API access is available:

```bash
uv run run_samples.py
```

Successful JSON responses and corresponding logs are saved separately in:

```text
outputs/
```

Failed requests are documented in their corresponding log files. Failed responses are not saved as successful JSON outputs.

## Project Structure

```text
assignment-2-messy-text-to-json/
│
├── extract.py
├── schema.py
├── run_samples.py
├── test_gemini.py
├── pyproject.toml
├── uv.lock
├── README.md
├── .python-version
├── .env.example
├── .gitignore
│
├── src/
│   └── assignment_2_messy_text_to_json/
│       └── __init__.py
│
├── prompts/
│   └── extract.txt
│
├── samples/
│   ├── job_post_01.txt
│   ├── job_post_02.txt
│   ├── job_post_03.txt
│   ├── job_post_04.txt
│   └── job_post_05.txt
│
├── edge_cases/
│   ├── empty.txt
│   ├── multilingual.txt
│   ├── junk.txt
│   └── injection.txt
│
├── tests/
│   ├── test_cli.py
│   ├── test_retry.py
│   └── test_samples.py
│
└── outputs/
    ├── empty.json
    ├── empty.log
    └── (additional sample outputs and logs)
```

## Security

- API keys are stored in `.env`.
- `.env` is excluded from Git.
- `.env.example` contains placeholders only.
- Job-post text is treated as untrusted input.
- Prompt-injection instructions are not followed intentionally.

Prompt-level instructions are safeguards, not a guarantee against every possible prompt-injection attack.

## Development Status

The local automated tests have passed. Live Gemini extraction and saved model-generated sample outputs still require successful API availability and verification.

---

**Assignment:** Agentic AI Developer — Assignment 2, Week 2
**Domain:** Job Posts
**Technologies:** Python, uv, Google Gemini API, Pydantic
