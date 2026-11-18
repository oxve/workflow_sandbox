"""Unit tests for str_util."""

import unittest

from str_util import normalize_whitespace, slugify, truncate


class TestStrUtil(unittest.TestCase):
    def test_normalize_whitespace_normal_and_edge(self) -> None:
        self.assertEqual(
            normalize_whitespace("  hello   world  "), "hello world"
        )
        self.assertEqual(normalize_whitespace("a\t\nb\r\n  c"), "a b c")
        self.assertEqual(normalize_whitespace("a\u00a0\u00a0b"), "a b")
        self.assertEqual(normalize_whitespace("   \t\n "), "")
        self.assertEqual(normalize_whitespace(""), "")

    def test_slugify_normal_and_edge(self) -> None:
        self.assertEqual(slugify("Hello, World! 2026"), "hello-world-2026")
        self.assertEqual(slugify("Café crème & Co."), "cafe-creme-co")
        self.assertEqual(
            slugify("  ---Foo__Bar---  ", separator="_"), "foo_bar"
        )
        self.assertEqual(slugify(""), "")
        self.assertEqual(slugify("!!!"), "")
        with self.assertRaises(ValueError):
            slugify("abc", separator="")

    def test_truncate_normal_and_edge(self) -> None:
        self.assertEqual(truncate("hello", 5), "hello")
        self.assertEqual(truncate("hello", 10), "hello")
        self.assertEqual(truncate("hello world", 8), "hello...")
        self.assertEqual(truncate("hello   world", 8), "hello...")
        self.assertEqual(truncate("hello   world", 9), "hello...")
        self.assertEqual(truncate("   abcdef", 5), "...")
        self.assertEqual(truncate("abcdefghij", 7, suffix="~"), "abcdef~")
        self.assertEqual(truncate("hello", 2), "..")
        self.assertEqual(truncate("hello", 0), "")
        self.assertEqual(truncate("", 0), "")
        with self.assertRaises(ValueError):
            truncate("hello", -1)


if __name__ == "__main__":
    unittest.main()
