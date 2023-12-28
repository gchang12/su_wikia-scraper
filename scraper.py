#!/usr/bin/python3
"""
Scrapes the SU Wikia for transcripts.
1. Loop through the Season_* pages.
2. Fetch episode url roots.
3. Use roots to navigate to respective transcript URL.
4. Scrape transcript into text file. 
"""

from pathlib import Path
import logging
import re

from bs4 import BeautifulSoup
import requests as r

from constants import WIKIA_ROOT, OUTPUT_NAME, LOGGING_FILE

def scrape_transcript(urlname: str):
    """
    Scrapes transcript into list of 2-tuples, each of the form (speaker, dialogue)
    """
    logging.info("scrape_transcript('%s')", urlname)
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
    logging.info("Scraped (%d) lines successfully. Last line: %s", index + 1, line)
    return line_list


def scrape_episodeurls(urlname: str):
    """
    Scrapes episode URLs from a 'urlname' parameter of the form:
    - https://steven-universe.fandom.com/wiki/Season_[1-5]
    """
    # Commented to fetch future episodes
    #assert re.fullmatch(r"https://steven-universe.fandom.com/wiki/Season_[1-5]", urlname) is not None
    #logging.info("'%s' is of the form, 'https://steven-universe.fandom.com/wiki/Season_[1-5]. Proceeding.", urlname)
    logging.info("scrape_episodeurls('%s')", urlname)
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
        #logging.info("episode_url := '%s'.", episode_url)
        episode_name = td.text.strip().strip('"')
        #logging.info("episode_name := '%s'.", episode_name)
        episode_line = (episode_name, episode_url)
        #logging.info("episode_urls.append(%s)", episode_line)
        episode_urls.append(episode_line)
    logging.info("Found (%d) episodes. Last episode: %s", index, episode_line)
    return episode_urls

def format_linelist(linelist: list):
    """
    Transforms a list of 2-tuples of str-objects into a writeable str.
    """
    new_linelist = []
    for speaker, dialogue in linelist:
        if speaker is None:
            row_header = "|"
        elif isinstance(speaker, str):
            row_header = speaker
        else:
            raise TypeError("speaker := %s is not None or of str-type." % speaker)
        assert isinstance(dialogue, str)
        row_content = dialogue
        new_linelist.append(row_header + ": " + row_content)
    formatted_lines = "\n".join(new_linelist)
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
    logging.info("Created '%s' output directory.", OUTPUT_NAME)

    def get_seasonurl(snum: int):
        """
        Returns the appropriate URL for the season page corresponding to the 'season_num' int parameter.
        """
        assert isinstance(snum, int)
        assert 1 <= snum <= num_seasons # from outer environment
        return "https://steven-universe.fandom.com/wiki/Season_%d" % snum

    for season_num in range(1, num_seasons + 1):
        season_dir = output_dir.joinpath("Season_%d" % season_num)
        season_dir.mkdir(exist_ok=True)
        logging.info("Created '%s' output directory.", str(season_dir))
        season_url = get_seasonurl(season_num)
        logging.info("Scraping '%s' for episode list of Season_%d.", season_url, season_num)
        episode_urls = scrape_episodeurls(season_url)
        #logging.info("Episode list for Season_%d found. %d episodes found.", season_num, len(episode_urls))
        episode_indexno = 1
        for episode_name, episode_url in episode_urls:
            line_list = scrape_transcript(WIKIA_ROOT + episode_url + "/Transcript")
            logging.info("Scraping transcript for episode_name := '%s' from episode_url := '%s'", episode_name, WIKIA_ROOT + episode_url)
            formatted_lines = format_linelist(line_list)
            episode_file = season_dir.joinpath(str(episode_indexno) + "-" + episode_name + ".txt")
            episode_file.write_text(formatted_lines)
            logging.info("Episode transcript for Season_%d!'%s' written to '%s'", season_num, episode_name, str(episode_file))
            episode_indexno += 1

def scrape_movie():
    """
    Scrapes transcript for SU: The Movie. Calls: scrape_transcript, format_linelist
    """
    urlname = "https://steven-universe.fandom.com/wiki/Steven_Universe:_The_Movie/Transcript"
    logging.info("Scraping 'Steven Universe: The Movie' transcript from '%s'.", urlname)
    line_list = scrape_transcript(urlname)
    formatted_lines = format_linelist(line_list)
    output_dir = Path(OUTPUT_NAME, "Movie")
    output_dir.mkdir(exist_ok=True)
    logging.info("Created '%s' output directory.", str(output_dir))
    output_file = output_dir.joinpath("Movie.txt")
    output_file.write_text(formatted_lines)
    logging.info("Successfully wrote 'Steven Universe: The Movie' transcript to '%s'.", str(output_file))

def scrape_future():
    """
    Scrapes Future episodes. Calls: scrape_episodeurls, scrape_transcript, format_linelist
    """
    urlname = "https://steven-universe.fandom.com/wiki/Steven_Universe_Future"
    logging.info("Scraping 'Steven Universe: Future' episode list from '%s'.", urlname)
    episode_urls = scrape_episodeurls(urlname)
    output_dir = Path(OUTPUT_NAME, "Future")
    output_dir.mkdir(exist_ok=True)
    logging.info("Created '%s' output directory.", str(output_dir))
    episode_indexno = 1
    for episode_name, episode_url in episode_urls:
        logging.info("Scraping Future!'%s' transcript from '%s'.", episode_name, episode_url)
        line_list = scrape_transcript(WIKIA_ROOT + episode_url + "/Transcript")
        formatted_lines = format_linelist(line_list)
        episode_file = output_dir.joinpath(str(episode_indexno) + "-" + episode_name + ".txt")
        episode_file.write_text(formatted_lines)
        episode_indexno += 1

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename=LOGGING_FILE)
    scrape_or_no = ""
    output_dir = Path(OUTPUT_NAME)
    while scrape_or_no not in ("y", "n") and output_dir.exists():
        scrape_or_no = input(f"\n    '{str(output_dir)}' directory for transcripts already exists. Overwrite, and remake? (y/n) ")
    if scrape_or_no == "y":
        scrape_episodes()
        scrape_movie()
        scrape_future()
