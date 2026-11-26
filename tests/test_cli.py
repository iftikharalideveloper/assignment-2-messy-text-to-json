import io
import json
import sys
import unittest

from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

from extract import main
from schema import Extracted


class CLITests(unittest.TestCase):

    def test_non_empty_input_prints_only_json(self):

        fake_result = Extracted(
            job_title="Python Developer",
            company="ABC Tech",
            requirements=["Python", "REST APIs"],
        )

        captured_stdout = io.StringIO()
        captured_stderr = io.StringIO()

        with (
            patch("sys.argv", ["extract.py", "Hiring Python Developer at ABC Tech"]),
            patch("extract.ask", return_value=fake_result) as mocked_ask,
            redirect_stdout(captured_stdout),
            redirect_stderr(captured_stderr),
        ):

            exit_code = main()

        # Application should finish successfully.
        self.assertEqual(exit_code, 0)

        # Standard output must contain valid JSON only.
        output_data = json.loads(captured_stdout.getvalue())

        # Validate the output against our Pydantic schema.
        Extracted.model_validate(output_data)

        self.assertEqual(output_data["job_title"], "Python Developer")

        # Extraction function must receive the user's input.
        mocked_ask.assert_called_once()

        prompt = mocked_ask.call_args.args[0]

        self.assertIn("Hiring Python Developer at ABC Tech", prompt)

        # No extra text should appear in standard error
        # during this mocked execution.
        self.assertEqual(captured_stderr.getvalue(), "")

    def test_empty_input_does_not_call_gemini(self):

        captured_stdout = io.StringIO()

        with self.assertLogs("extract", level="WARNING") as logs:
            with (
                patch("sys.argv", ["extract.py", ""]),
                patch("extract.ask") as mocked_ask,
                redirect_stdout(captured_stdout),
            ):
                exit_code = main()

        # Empty input should finish successfully.
        self.assertEqual(exit_code, 0)

        # Output must be valid JSON.
        data = json.loads(captured_stdout.getvalue())
        result = Extracted.model_validate(data)

        # Missing fields should have empty/default values.
        self.assertIsNone(result.job_title)
        self.assertIsNone(result.company)
        self.assertEqual(result.requirements, [])

        # Gemini must not be called for empty input.
        mocked_ask.assert_not_called()

        # Warning must be generated.
        self.assertTrue(
            any("Empty input received" in message for message in logs.output)
        )

    def test_api_error_returns_clean_failure(self):

        captured_stdout = io.StringIO()

        with self.assertLogs("extract", level="ERROR") as logs:
            with (
                patch("sys.argv", ["extract.py", "Python Developer at ABC Tech"]),
                patch("extract.ask", side_effect=RuntimeError("Simulated API failure")),
                redirect_stdout(captured_stdout),
            ):
                exit_code = main()

        # Application should return failure status.
        self.assertEqual(exit_code, 1)

        # Failed extraction must not print fake JSON.
        self.assertEqual(captured_stdout.getvalue(), "")

        # A clear error must be logged.
        self.assertTrue(
            any("Simulated API failure" in message for message in logs.output)
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
