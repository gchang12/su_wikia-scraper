#!/usr/bin/python3
"""
"""

import logging
import unittest

import scraper
import requests as r

class ScraperTest(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        self.transcript_page = "https://steven-universe.fandom.com/wiki/Political_Power/Transcript"
        self.index_page = "https://steven-universe.fandom.com/wiki/Season_1"
        self.line_list = [
            (None, "dances fervently"),
            ("Ronald", "We ain't gonna do magic, then?"),
            ]

    def test_scrape_transcript(self):
        line_list = scraper.scrape_transcript(self.transcript_page)
        for speaker, dialogue in line_list:
            if type(speaker) != str and speaker is not None:
                assert TypeError("speaker := %s is not None or str-type")
            assert isinstance(dialogue, str)

    def test_scrape_episodeurls(self):
        episode_urls = scraper.scrape_episodeurls(self.index_page)
        num_episodes = 52
        self.assertIsInstance(episode_urls, list)
        self.assertEqual(len(episode_urls), num_episodes)
        wikia_root = scraper.WIKIA_ROOT
        for episode_name, episode_url in episode_urls:
            assert isinstance(episode_name, str)
            assert isinstance(episode_url, str)
            full_episode_url = wikia_root + episode_url
            logging.info("Assert: '%s' is a valid URL", full_episode_url)
            response = r.get(full_episode_url)
            response.raise_for_status()

    def test_format_linelist(self):
        self.line_list.insert(0, (42, None))
        with self.assertRaises(TypeError):
            # because speaker is int (i.e. not None or str)
            scraper.format_linelist(self.line_list)
        self.line_list.pop(0)
        self.line_list.insert(0, (None, None))
        with self.assertRaises(AssertionError):
            # because dialogue is None (i.e. not str)
            scraper.format_linelist(self.line_list)
        self.line_list.pop(0)
        formatted_lines = scraper.format_linelist(self.line_list)
        self.assertEqual(len(self.line_list), len(formatted_lines.split("\n")))
        expected = "|: dances fervently\nRonald: We ain't gonna do magic, then?"
        self.assertEqual(expected, formatted_lines)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
