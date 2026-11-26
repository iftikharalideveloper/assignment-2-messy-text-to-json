import json
import subprocess
import sys
from pathlib import Path

from pydantic import ValidationError

from schema import Extracted

ROOT_DIR = Path(__file__).resolve().parent
SAMPLES_DIR = ROOT_DIR / "samples"
EDGE_CASES_DIR = ROOT_DIR / "edge_cases"
OUTPUTS_DIR = ROOT_DIR / "outputs"
EXTRACT_SCRIPT = ROOT_DIR / "extract.py"


def main() -> int:
    """Run all sample inputs and save validated JSON and logs."""

    OUTPUTS_DIR.mkdir(exist_ok=True)

    input_files = sorted(SAMPLES_DIR.glob("*.txt")) + sorted(
        EDGE_CASES_DIR.glob("*.txt")
    )

    if not input_files:
        print("Error: No sample files found.", file=sys.stderr)
        return 1

    failed = 0

    for input_file in input_files:
        job_text = input_file.read_text(encoding="utf-8")

        output_file = OUTPUTS_DIR / f"{input_file.stem}.json"
        log_file = OUTPUTS_DIR / f"{input_file.stem}.log"

        print(f"Processing: {input_file.name}")

        # Execute the actual CLI application.
        completed = subprocess.run(
            [sys.executable, str(EXTRACT_SCRIPT), job_text],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        # Save application logs separately.
        log_content = completed.stderr or "No logs generated.\n"

        if completed.returncode != 0:
            log_file.write_text(
                log_content + f"\nExit code: {completed.returncode}\n",
                encoding="utf-8",
            )
            print(
                f"FAILED: {input_file.name}. See {log_file.name}",
                file=sys.stderr,
            )
            failed += 1
            continue

        try:
            data = json.loads(completed.stdout)
            result = Extracted.model_validate(data)

        except (json.JSONDecodeError, ValidationError) as error:
            log_file.write_text(
                log_content + f"\nOutput verification failed: {error}\n",
                encoding="utf-8",
            )
            print(
                f"FAILED: Invalid JSON output for {input_file.name}",
                file=sys.stderr,
            )
            failed += 1
            continue

        # Save only genuine, successfully validated output.
        output_file.write_text(
            result.model_dump_json(indent=2) + "\n",
            encoding="utf-8",
        )

        log_file.write_text(log_content, encoding="utf-8")

        print(f"PASSED: Saved {output_file.name}")

    print(f"\nTotal inputs: {len(input_files)}")
    print(f"Successful: {len(input_files) - failed}")
    print(f"Failed: {failed}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
