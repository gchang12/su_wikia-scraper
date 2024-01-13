#!/usr/bin/python3
"""
Renames episode transcripts to have zero-padded episode numbers
that are of length two.
"""

from pathlib import Path
import re
import logging

#OUTPUT_NAME = "transcripts"
from constants import OUTPUT_NAME

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(module)s.%(funcName)s: %(message)s",
    )

for season_dir in Path(OUTPUT_NAME).iterdir():
    for episode_file in season_dir.iterdir():
        match = re.search("(\d+)-(.+)", episode_file.name)
        if match is None:
            logging.info("Episode number for '%s' not found. Skipping.", episode_file)
            continue
        episode_num = int(match.group(1))
        episode_name_tail = match.group(2)
        logging.info("Episode number for '%s' found: %d", episode_file, episode_num)
        new_epnum = "%02d" % episode_num
        new_epname = new_epnum + "_" + episode_name_tail
        logging.info("Renaming '%s' to '%s'.", episode_file, new_epname)
        episode_file.rename(episode_file.with_name(new_epname))


if __name__ == '__main__':
    pass
