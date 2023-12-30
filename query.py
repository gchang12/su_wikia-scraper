#!/usr/bin/python3
"""
Print list of files that match the regex provided. (i.e. grep corollary)
Provides season number, and episode title.
Provides option to navigate to matching file via menu interface.

# Ought I try this and the scraper in rust, perhaps?
"""

import argparse             # for processing cmdline args
import os                   # for chdir to OUTPUT_NAME
import re                   # because this is essentially grep
import webbrowser           # to open matching file
from pathlib import Path    # to iterate over files.
from textwrap import indent  # to display text more cleanly

from constants import OUTPUT_NAME, SEASON_ORDER

def compile_matches(pattern: str):
    """
    Compiles a table of files, lines, and line numbers matching the 'pattern' str parameter.
    """
    # compile list of matching files.
    matching_files = []
    matching_lines = []
    matching_linenos = []
    os.chdir(OUTPUT_NAME)

    # to get matches in order
    def order_seasons(spath):
        """
        Returns index of the season as defined by SEASON_ORDER.
        spath: pathlib.Path
        """
        sstr = str(spath)
        return SEASON_ORDER.index(sstr)

    # to get matches in order
    def order_episodes(efile):
        """
        Returns ordering of episode in the season.

        efile: pathlib.Path
        """
        episode_filename = efile.name
        if episode_filename == "Movie.txt":
            return 0
        episode_num = re.search(r"(\d+).+", episode_filename).group(1)
        return int(episode_num)

    for season_path in sorted(Path(".").iterdir(), key=order_seasons):
        for episode_file in sorted(season_path.iterdir(), key=order_episodes):
            # get text
            # check if match is found
            for lineno, line in enumerate(episode_file.read_text().splitlines(), start=1):
                if re.search(pattern, line) is None:
                    continue
                matching_files.append(episode_file)
                matching_lines.append(line)
                matching_linenos.append(lineno)
                break
    return matching_files, matching_lines, matching_linenos

def show_menu(matching_files: list, matching_lines: list, matching_linenos: list):
    """
    Presents a menu that displays files that contain a line that matches the pattern.

    The menu contains a line number, and presents an interface for the user to open the file.
    """
    # present option to navigate to file to search
    prefix = " " * 4
    print()
    match_indices = set()
    header = "List of Matching Episodes"
    print(indent(header, prefix))
    #print()
    print(indent(("=" * len(header)), prefix))
    for match_index, episode_file in enumerate(matching_files):
        episode_name = str(episode_file)
        print(indent("%3d: %r@L%d" % (match_index, episode_name, matching_linenos[match_index]), prefix))
        print(indent(matching_lines[match_index], "  " + prefix * 2))
        match_indices.add(str(match_index))
    # ultimately for clearing space, but functionality-wise entirely optional
    matching_lines.clear()
    matching_linenos.clear()
    print()
    print(indent("Please select the number corresponding the file you wish to open: ", prefix), end="")
    file_to_open = input()
    print()
    #breakpoint()
    if file_to_open in match_indices:
        file_indexno = int(file_to_open)
        filename = matching_files[file_indexno]
        print(indent("Opening %r in browser." % str(filename), prefix))
        webbrowser.open_new(str(filename))
    else:
        print(indent("%r was an invalid selection. Please try again." % file_to_open, prefix))

def main():
    """
    Accepts cmdline argument 'pattern' for which the transcripts are searched.

    Presents a menu for the end-user to open a file that contains a matching line.
    """
    parser = argparse.ArgumentParser(description="grep for lines in SU episodes")
    parser.add_argument('pattern', type=str, nargs=1, help='regex to grep for')
    pattern = parser.parse_args().pattern.pop()
    matching_files, matching_lines, matching_linenos = compile_matches(pattern)
    if not matching_files:
        print(indent("The regex pattern %r did not match any dialogue or characters. Please try again." % pattern, prefix))
        exit()
    show_menu(matching_files, matching_lines, matching_linenos)

if __name__ == '__main__':
    main()
