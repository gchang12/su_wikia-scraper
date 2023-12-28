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

from scraper import OUTPUT_NAME

def print_matches(parsed_args: argparse.Namespace):
    """
    """
    pattern = parsed_args.pattern.pop(0)
    # compile list of matching files.
    matching_files = []
    matching_lines = []
    os.chdir(OUTPUT_NAME)
    for season_path in Path(".").iterdir():
        for episode_file in season_path.iterdir():
            for line in episode_file.read_text().splitlines():
                if re.search(pattern, line) is None:
                    continue
                matching_files.append(episode_file)
                matching_lines.append(line)
                break
            # get text
            # check if match is found
            # if so, print matching first matching line, along with index number.
            # increment index number
            # go on to next episode
    # present option to navigate to file to search
    return matching_files, matching_lines

def show_menu(matching_files: list, matching_lines: list):
    """
    """
    match_indices = set()
    # TODO: use textwrap module or something for indentation
    header = "List of Matching Episodes"
    print(f"\n    {header}\n    {'=' * len(header)}")
    for match_index, episode_file in enumerate(matching_files):
        episode_name = str(episode_file)
        print("    %3d: '%s': %s" % (match_index, episode_name.replace(".txt", ""), matching_lines[match_index]))
        match_indices.add(str(match_index))
    matching_lines.clear()
    file_to_open = input("\n    Please select the number corresponding the file you wish to open: ")
    if file_to_open in match_indices:
        file_indexno = int(file_to_open)
        filename = matching_files[file_indexno]
        print("    Opening '%s' in browser...", filename)
        webbrowser.open_new(str(filename))
    else:
        print("    '%s' was an invalid selection. Please try again.", file_to_open)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="grep for lines in SU episodes")
    parser.add_argument('pattern', type=str, nargs=1, help='regex to grep for')
    parsed_args = parser.parse_args()
    matching_files, matching_lines = print_matches(parsed_args)
    show_menu(matching_files, matching_lines)
