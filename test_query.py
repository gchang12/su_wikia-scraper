#!/usr/bin/python3
"""
Contains unit tests for query.py.
- compile_matches(pattern: str)
- show_menu(pattern: str, matching_files: list, matching_lines: list, matching_linenos: list)
- main()
"""

import unittest
import query

class TestQuery(unittest.TestCase):
    """
    Contains tests for:
    - main: empty resultset, invalid pattern, non-existent pattern
    - show_menu: valid user input, or otherwise
    - compile_matches: empty resultset, non-empty resultset

    Assume that output directory has already been compiled.
    """

    def setUp(self):
        """
        Sets up parameters to be used by all methods.
        """
        # TODO: Figure out how to manually edit argparse.ArgumentParser
        pass

    def test_show_menu(self):
        """
        Tests show_menu method, and explores numerical menu input, valid or otherwise.

        Mocks: webbrowser.open_new
        """
        pass

    def test_compile_matches(self):
        """
        Tests compile_matches method, and explores resultsets, trivial or otherwise.
        """
        pass

    def test_main(self):
        """
        Tests main method, and explores resultsets, and various arguments that can be given.

        Mocks: argparse.ArgumentParser
        """
        pass

if __name__ == '__main__':
    unittest.main()
