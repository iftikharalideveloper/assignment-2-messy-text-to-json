# Messy Text to JSON — Job Post Extractor

A simple Python command-line tool that turns messy job advertisements into clean JSON using **Google Gemini** and **Pydantic**.

The application extracts job details, checks the response against a data schema, and retries when the response is invalid.

- **Model:** `gemini-3.5-flash-lite`
- **Author:** Iftikhar Ali
- **GitHub:** [iftikharalideveloper](https://github.com/iftikharalideveloper)
- **Repository:** [Messy Text to JSON](https://github.com/iftikharalideveloper/assignment-2-messy-text-to-json)
- **Email:** [iftikharali.developer@gmail.com](mailto:iftikharali.developer@gmail.com)

---

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

Missing optional fields are returned as `null`. Missing requirements are returned as an empty list: `[]`.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
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
GEMINI_MODEL=gemini-3.5-flash-lite
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

1. You provide job-post text through the command line.
2. The application reads `prompts/extract.txt`.
3. Gemini returns structured JSON using the `Extracted` schema.
4. Pydantic validates the response.
5. If validation fails, the error is sent back to Gemini. The application tries up to three times.
6. Valid JSON is printed to the terminal. Logs and errors are sent separately to standard error.

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

## Samples and edge cases

Normal job-post inputs are stored in `samples/`:

| Input file        | Example                  | Saved JSON                 | Saved log                 |
| ----------------- | ------------------------ | -------------------------- | ------------------------- |
| `job_post_01.txt` | Complete job details     | `outputs/job_post_01.json` | `outputs/job_post_01.log` |
| `job_post_02.txt` | Missing information      | `outputs/job_post_02.json` | `outputs/job_post_02.log` |
| `job_post_03.txt` | Messy, unstructured text | `outputs/job_post_03.json` | `outputs/job_post_03.log` |
| `job_post_04.txt` | Short job post           | `outputs/job_post_04.json` | `outputs/job_post_04.log` |
| `job_post_05.txt` | International remote job | `outputs/job_post_05.json` | `outputs/job_post_05.log` |

Special inputs are stored in `edge_cases/`:

| Input file         | What it checks              | Saved JSON                  | Saved log                  |
| ------------------ | --------------------------- | --------------------------- | -------------------------- |
| `empty.txt`        | Empty input; no Gemini call | `outputs/empty.json`        | `outputs/empty.log`        |
| `multilingual.txt` | Spanish job post            | `outputs/multilingual.json` | `outputs/multilingual.log` |
| `junk.txt`         | Irrelevant text             | `outputs/junk.json`         | `outputs/junk.log`         |
| `injection.txt`    | Prompt-injection attempt    | `outputs/injection.json`    | `outputs/injection.log`    |

## Run and save all samples

The easiest way to process all five samples and all four edge cases is:

```bash
uv run run_samples.py
```

The script reads each `.txt` file, runs the CLI, and saves the JSON and log separately in `outputs/`. For example:

```text
samples/job_post_01.txt
        |
        v
outputs/job_post_01.json
outputs/job_post_01.log
```

The same naming pattern is used for the other sample and edge-case files. A successful, validated response is saved as `.json`. Logs and any failure details are saved as `.log`.

## Run one sample manually

Example using the first sample in PowerShell:

```powershell
$jobText = Get-Content samples/job_post_01.txt -Raw
uv run extract.py $jobText
```

To run a different sample, change the filename. For example:

```powershell
$jobText = Get-Content samples/job_post_02.txt -Raw
uv run extract.py $jobText
```

## Run one edge case manually

Spanish input:

```powershell
$jobText = Get-Content edge_cases/multilingual.txt -Raw
uv run extract.py $jobText
```

Junk text:

```powershell
$jobText = Get-Content edge_cases/junk.txt -Raw
uv run extract.py $jobText
```

Prompt-injection input:

```powershell
$jobText = Get-Content edge_cases/injection.txt -Raw
uv run extract.py $jobText
```

Empty input:

```powershell
uv run extract.py ""
```

Use `uv run run_samples.py` when you want the JSON and log files saved automatically for every input.

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

The project has successfully completed local automated testing and live Gemini API extraction using `gemini-3.5-flash-lite`.

### Verification Results

- 9/9 automated unit tests passed.
- 5/5 normal job-post samples successfully extracted.
- 4/4 edge cases processed, including empty input, Spanish text, junk text, and prompt injection.
- All 9 saved JSON files passed Pydantic validation.
- UTF-8 encoding verified for multilingual output.
- Validation retry mechanism tested, including the three-attempt limit.
- Fresh-clone installation and CLI tests passed.
- Git security scans found no obvious API keys or private keys.

### Model

Google Gemini `gemini-3.5-flash-lite`

---

**Assignment:** Agentic AI Developer — Assignment 2, Week 2
**Domain:** Job Posts
**Technologies:** Python, uv, Google Gemini API, Pydantic
