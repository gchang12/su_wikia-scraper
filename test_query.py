#!/usr/bin/python3
"""
Contains unit tests for query.py.
- compile_matches(pattern: str)
- show_menu(pattern: str, matching_files: list, matching_lines: list, matching_linenos: list)
- main()
"""

import logging
import os
import unittest
from unittest.mock import patch
import argparse

import query
from constants import LOGGING_FILE

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

    @patch("webbrowser.open_new")
    @patch("builtins.input")
    def test_show_menu(self, mockinput, mockopener):
        """
        Tests show_menu method, and explores numerical menu input, valid or otherwise.

        Mocks: webbrowser.open_new
        """
        matching_files = ['weh']
        matching_lines = ['arrr']
        matching_linenos = [0]
        logging.info("Setting input.return_value = ''.")
        mockinput.return_value = ""
        query.show_menu(matching_files, matching_lines, matching_linenos)
        logging.info("Assert: webbrowser.open_new is not called.")
        mockopener.assert_not_called()
        matching_files = ['weh']
        matching_lines = ['arrr']
        matching_linenos = [0]
        logging.info("Setting input.return_value = '0'.")
        mockinput.return_value = "0"
        #mockinput.side_effect = lambda *args, **kwds: print(0)
        query.show_menu(matching_files, matching_lines, matching_linenos)
        logging.info("Assert: webbrowser.open_new is called once with '%s'.", matching_files[0])
        mockopener.assert_called_once_with(matching_files[0])

    def test_compile_matches(self):
        """
        Tests compile_matches method, and explores resultsets, trivial or otherwise.
        """
        # confirmed via manual input to return results as listed.
        pattern = "nye"
        logging.info("pattern := '%s'", pattern)
        matching_files, matching_lines, matching_linenos = query.compile_matches(pattern)
        logging.info("Assert: Return value has length 1.")
        assert len(matching_files) == 1
        assert len(matching_lines) == 1
        assert len(matching_linenos) == 1
        logging.info("Currently in '%s'.", os.getcwd())
        os.chdir('..')
        logging.info("chdir ..; Currently in '%s'.", os.getcwd())
        pattern = "lapis"
        logging.info("pattern := '%s'", pattern)
        logging.info("Assert: Return value has length 0.")
        matching_files, matching_lines, matching_linenos = query.compile_matches(pattern)
        assert len(matching_files) == 0
        assert len(matching_lines) == 0
        assert len(matching_linenos) == 0
        logging.info("Currently in '%s'.", os.getcwd())
        os.chdir('..')
        logging.info("chdir ..; Currently in '%s'.", os.getcwd())

    @unittest.skip # not really decoupled from the other two.
    def test_main(self):
        """
        Tests main method, and explores resultsets, and various arguments that can be given.

        Mocks: argparse.ArgumentParser
        """
        pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
        #format="%(levelname)s:su-wikia_scraper.query:%(msg)s", # format strings don't expand for some reason.
        filename=LOGGING_FILE)
    unittest.main()
