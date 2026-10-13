import unittest
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

from openrouter_client import OpenRouterClient, answer_numbers


class OpenRouterV3Tests(unittest.TestCase):
    def test_answer_numbers_extracts_numbers_only(self):
        self.assertEqual(answer_numbers("The correct answers are 2 and 4."), ["2", "4"])

    def test_lettered_multiple_choice_is_converted_to_numbers(self):
        question_response = "B. Yellow"
        self.assertEqual(answer_numbers(question_response), ["2"])

    def test_missing_key_is_reported_before_network_call(self):
        client = OpenRouterClient("")
        with self.assertRaisesRegex(RuntimeError, "OPENROUTER_API_KEY"):
            client.chat("hello")

    def test_free_model_fallback_returns_second_model(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return b'{"choices":[{"message":{"content":"2"}}]}'

        with patch("openrouter_client.request.urlopen", side_effect=[
            HTTPError("url", 429, "busy", {}, BytesIO(b"")), Response()
        ]) as urlopen:
            client = OpenRouterClient("test-key", models=("first:free", "second:free"))
            self.assertEqual(client.chat("question"), "2")

        self.assertEqual(urlopen.call_count, 2)
        self.assertIn('"model": "first:free"', urlopen.call_args_list[0].args[0].data.decode())
        self.assertIn('"model": "second:free"', urlopen.call_args_list[1].args[0].data.decode())


if __name__ == "__main__":
    unittest.main()
