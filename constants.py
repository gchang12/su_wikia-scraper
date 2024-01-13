#!/usr/bin/python3
"""
Contains constants used by all modules.
"""

WIKIA_ROOT = "https://steven-universe.fandom.com"
OUTPUT_NAME = "output"
LOGGING_FILE = "su-wikia_scraper.log"
SEASON_ORDER = ["Season_%d" % season_num for season_num in range(1, 5 + 1)]
SEASON_ORDER.append("Shorts")
SEASON_ORDER.append("Movie")
SEASON_ORDER.append("Future")


if __name__ == '__main__':
    pass
