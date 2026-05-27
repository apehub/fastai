"""Tests for the package entrypoint."""

import unittest
from unittest.mock import patch


class ModuleEntrypointTests(unittest.TestCase):
    def test_module_entrypoint_delegates_to_fastai_main(self):
        with patch("fastai.fastai.main", return_value=7) as fake_main:
            from fastai.__main__ import main

            self.assertEqual(main(), 7)
            fake_main.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
