import unittest

from hello import message


class HelloTest(unittest.TestCase):
    def test_message(self) -> None:
        self.assertEqual(message("lab"), "Hello from a Python lab!")


if __name__ == "__main__":
    unittest.main()
