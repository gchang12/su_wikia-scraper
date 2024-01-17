#!/usr/bin/python3
"""
Scrapes the SU Wikia for transcripts.
1. Loop through the Season_* pages.
2. Fetch episode url roots.
3. Use roots to navigate to respective transcript URL.
4. Scrape transcript into text file. 
"""

from pathlib import Path
from threading import Thread
import logging
import re

from bs4 import BeautifulSoup
import requests as r

from constants import WIKIA_ROOT, OUTPUT_NAME, LOGGING_FILE

def scrape_transcript(urlname: str):
    """
    Scrapes transcript into list of 2-tuples, each of the form (speaker, dialogue)
    """
    logging.info("scrape_transcript(%r)", urlname)
    response = r.get(urlname)
    logging.info("Sending GET request")
    response.raise_for_status()
    logging.info("Request successful. Commencing table-fetch operation.")
    transcript_table = BeautifulSoup(response.text, "html.parser").find("table", class_="wikitable bgrevo")
    logging.info("Fetching <table class='wikitable bgrevo'> tree.")
    assert transcript_table is not None
    logging.info("Tree fetched successfully. Searching contents.")
    line_list = [] # list of tuples
    for index, tr in enumerate(transcript_table.find_all("tr")):
        if index == 0:
            # skip header row of table
            continue
        if tr.find("th") is None:
            speaker = None
        else:
            speaker = tr.find("th").text.strip()
        # 5!Can't Go Back has a blank td tag in its transcript table.
        if tr.find("td") is None:
            dialogue = ""
        else:
            dialogue = tr.find("td").text.strip()
        line = (speaker, dialogue)
        line_list.append(line)
    logging.info("Scraped (%d) lines successfully. Last line: %s", index, line)
    return line_list


def scrape_episodeurls(urlname: str):
    """
    Scrapes episode URLs from a 'urlname' parameter of the form:
    - https://steven-universe.fandom.com/wiki/Season_[1-5]
    """
    # Commented to fetch Future episodes
    #assert re.fullmatch(r"https://steven-universe.fandom.com/wiki/Season_[1-5]", urlname) is not None
    #logging.info("%r is of the form, 'https://steven-universe.fandom.com/wiki/Season_[1-5]. Proceeding.", urlname)
    logging.info("scrape_episodeurls(%r)", urlname)
    response = r.get(urlname)
    logging.info("Sending GET request.")
    response.raise_for_status()
    logging.info("GET request successfully sent.")
    logging.info("Fetching <td style='border-top:0; font-weight:bold !important'> cells.")
    episode_cells = BeautifulSoup(response.text, "html.parser").find_all("td", style="border-top:0; font-weight:bold !important")
    logging.info("<td ...> cells successfully fetched. Commencing iteration.")
    episode_urls = []
    for index, td in enumerate(episode_cells):
        episode_url = td.find('a')['href']
        #logging.info("episode_url := %r.", episode_url)
        episode_name = td.text.strip().strip('"')
        #logging.info("episode_name := %r.", episode_name)
        episode_line = (episode_name, episode_url)
        #logging.info("episode_urls.append(%s)", episode_line)
        episode_urls.append(episode_line)
    logging.info("Found (%d) episodes. Last episode: %s", index, episode_line)
    return episode_urls

def format_linelist(linelist: list):
    """
    Transforms a list of 2-tuples of str-objects into a writeable str.
    """
    def speakerpipe_colon_formatter(line):
        """
        Gets a line (2-tuple of (None|str, str), and converts it to a string of the form, '(|\|speaker): dialogue'
        """
        speaker, dialogue = line
        logging.debug("speaker := %s is of type %s.", speaker, type(speaker))
        if not (isinstance(speaker, str) or speaker is None):
            raise TypeError(f"speaker := {speaker} is of type {type(speaker)}; not None or str-type.")
        assert dialogue is not None
        row_header = ("|" if speaker is None else speaker)
        logging.debug("row_header := %s is of type %s.", row_header, type(row_header))
        speakerpipe_colon_line = row_header + ": " + dialogue
        return speakerpipe_colon_line
    formatted_lines = "\n".join(map(speakerpipe_colon_formatter, linelist))
    return formatted_lines

def scrape_episodes():
    """
    Loop over all seasons.
    Create directories for each one.
    Create file in accordance with 'episode_name' str-parameter.
    Write to file using 'format_linelist' function.
    """
    num_seasons = 5
    output_dir = Path(OUTPUT_NAME)
    output_dir.mkdir(exist_ok=True)
    logging.info("Created %r output directory.", OUTPUT_NAME)

    def get_seasonurl(snum: int):
        """
        Returns the appropriate URL for the season page corresponding to the 'season_num' int parameter.
        """
        assert isinstance(snum, int)
        assert 1 <= snum <= num_seasons # from outer environment
        # everything here is just so hard-coupled
        return "https://steven-universe.fandom.com/wiki/Season_%d" % snum

    def scrape_season(snum: int):
        """
        Scrapes all episodes from a given season.
        """
        season_dir = output_dir.joinpath("Season_%d" % snum)
        season_dir.mkdir(exist_ok=True)
        logging.info("Created %r output directory.", str(season_dir))
        season_url = get_seasonurl(snum)
        logging.info("Scraping %r for episode list of Season_%d.", season_url, snum)
        episode_urls = scrape_episodeurls(season_url)
        #logging.info("Episode list for Season_%d found. %d episodes found.", snum, len(episode_urls))
        episode_indexno = 1
        for episode_name, episode_url in episode_urls:
            line_list = scrape_transcript(WIKIA_ROOT + episode_url + "/Transcript")
            logging.info("Scraping transcript for episode_name := %r from episode_url := %r", episode_name, WIKIA_ROOT + episode_url)
            formatted_lines = format_linelist(line_list)
            episode_file = season_dir.joinpath("%02d" % episode_indexno + "-" + episode_name + ".txt")
            episode_file.write_text(formatted_lines)
            logging.info("Episode transcript for Season_%d!%r written to %r", snum, episode_name, str(episode_file))
            episode_indexno += 1

    # definitely implement threading for each season
    # also, put this in a while-loop so that it works for lots of shows
    thread_list = []
    for season_num in range(1, num_seasons + 1):
        scrapejob = Thread(target=scrape_season, args=[season_num])
        thread_list.append(scrapejob)
    for scrapejob in thread_list:
        scrapejob.start()
        scrapejob.join()

def scrape_movie():
    """
    Scrapes transcript for SU: The Movie. Calls: scrape_transcript, format_linelist
    """
    urlname = "https://steven-universe.fandom.com/wiki/Steven_Universe:_The_Movie/Transcript"
    logging.info("Scraping 'Steven Universe: The Movie' transcript from %r.", urlname)
    line_list = scrape_transcript(urlname)
    formatted_lines = format_linelist(line_list)
    output_dir = Path(OUTPUT_NAME, "Movie")
    output_dir.mkdir(exist_ok=True)
    logging.info("Created %r output directory.", str(output_dir))
    output_file = output_dir.joinpath("Movie.txt")
    output_file.write_text(formatted_lines)
    logging.info("Successfully wrote 'Steven Universe: The Movie' transcript to %r.", str(output_file))

def scrape_future():
    """
    Scrapes Future episodes. Calls: scrape_episodeurls, scrape_transcript, format_linelist
    """
    urlname = "https://steven-universe.fandom.com/wiki/Steven_Universe_Future"
    logging.info("Scraping 'Steven Universe: Future' episode list from %r.", urlname)
    episode_urls = scrape_episodeurls(urlname)
    output_dir = Path(OUTPUT_NAME, "Future")
    output_dir.mkdir(exist_ok=True)
    logging.info("Created %r output directory.", str(output_dir))
    episode_indexno = 1
    # implement threading here, maybe?
    for episode_name, episode_url in episode_urls:
        logging.info("Scraping Future!%r transcript from %r.", episode_name, episode_url)
        line_list = scrape_transcript(WIKIA_ROOT + episode_url + "/Transcript")
        formatted_lines = format_linelist(line_list)
        episode_file = output_dir.joinpath("%02d" % episode_indexno + "-" + episode_name + ".txt")
        episode_file.write_text(formatted_lines)
        episode_indexno += 1

def scrape_shorts():
    """
    Scrapes shorts into ./output/Shorts/
    """
    output_dir = Path(OUTPUT_NAME, "Shorts")
    output_dir.mkdir(exist_ok=True)
    logging.info("Created %r output directory.", str(output_dir))
    # get list of URLs to scrape from.
    response = r.get("https://steven-universe.fandom.com/wiki/Category:Shorts")
    response.raise_for_status()
    shorts_cells = BeautifulSoup(response.text, 'html.parser').find_all("div", class_="category-page__member-left")
    for index, cell in enumerate(shorts_cells):
        if not index:
            # skip 'Classroom Shorts' link
            continue
        # get URL, then scrape from it
        #print(cell)
        source_url = WIKIA_ROOT + cell.find("a")['href'] + "/Transcript"
        short_title = cell.find('a')['title']
        # get transcript, then format to writeable format
        line_list = scrape_transcript(source_url)
        formatted_lines = format_linelist(line_list)
        # write to file
        output_file = output_dir.joinpath("%02d" % index + "-" + short_title + ".txt")
        output_file.write_text(formatted_lines)
        logging.info("Short #%d found: %r. Scraped and wrote %d lines to %r", index, short_title, len(line_list), str(output_file))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename=LOGGING_FILE)
    scrape_or_no = "y"
    output_dir = Path(OUTPUT_NAME)
    scrape_episodes()
    #scrape_shorts()
    """
    while scrape_or_no not in ("y", "n") and output_dir.exists():
        scrape_or_no = input(f"\n    '{str(output_dir)}' directory for transcripts already exists. Overwrite, and remake? (y/n) ")
    if scrape_or_no == "y":
        scrape_episodes()
        scrape_movie()
        scrape_future()
    """
