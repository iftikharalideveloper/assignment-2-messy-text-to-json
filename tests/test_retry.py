import unittest
from unittest.mock import patch

from extract import ask
from schema import Extracted

INVALID_JSON = """
{
    "job_title": "Python Developer",
    "requirements": "Python, REST APIs"
}
"""

VALID_JSON = """
{
    "job_title": "Python Developer",
    "requirements": ["Python", "REST APIs"]
}
"""


class RetryTests(unittest.TestCase):

    def test_validation_error_is_sent_back(self):

        with patch(
            "extract.call_model", side_effect=[INVALID_JSON, VALID_JSON]
        ) as mocked_call:

            result = ask("Extract this job post.", Extracted, tries=3)

            self.assertEqual(result.job_title, "Python Developer")
            self.assertEqual(result.requirements, ["Python", "REST APIs"])

            # Exactly two API attempts were made.
            self.assertEqual(mocked_call.call_count, 2)

            # The second prompt must contain the validation error.
            retry_prompt = mocked_call.call_args_list[1].args[0]

            self.assertIn("YOUR PREVIOUS RESPONSE FAILED VALIDATION", retry_prompt)

            self.assertIn("requirements", retry_prompt)

    def test_stops_after_three_attempts(self):

        with patch(
            "extract.call_model", side_effect=[INVALID_JSON, INVALID_JSON, INVALID_JSON]
        ) as mocked_call:

            with self.assertRaisesRegex(RuntimeError, "after 3 attempts"):
                ask("Extract this job post.", Extracted, tries=10)

            # Even when 10 is requested, maximum must be 3.
            self.assertEqual(mocked_call.call_count, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
