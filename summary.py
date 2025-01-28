#!/usr/bin/env python3
# FileName: summary.py
# version 1.4
# Summary: A command-line tool to scan Python files in a project directory for:
#   - FileName
#   - version
#   - Summary
#   - Tags
#
# Tags: help, info, summary, tool
#
# Features:
#   - Automatic discovery of *.py files (except itself, if desired)
#   - Filtering by file(s), tags, or a search term (checks file name, FileName line,
#     version, summary, and tags)
#   - Optionally printing the full code for each matched file
#   - Saving summary data as JSON:
#      --save-json with no argument => automatically names file in ./summary_print/
#      --save-json myfile.json => saves with a custom name
#   - NEW: Saving all matched files’ code to a .txt file (with line breaks) via --save-code

import os
import re
import json
import sys
import argparse
from datetime import datetime
from typing import List, Dict

# Regex patterns for the 4 lines:
RE_FILEHEADER = re.compile(r'^#\s*FileName\s*:\s*(.*)$', re.IGNORECASE)
RE_VERSION    = re.compile(r'^#\s*version\s*:\s*(.*)$', re.IGNORECASE)
RE_SUMMARY    = re.compile(r'^#\s*Summary\s*:\s*(.*)$', re.IGNORECASE)
RE_TAGS       = re.compile(r'^#\s*Tags\s*:\s*(.*)$', re.IGNORECASE)


class CustomArgParser(argparse.ArgumentParser):
    """
    Subclass ArgumentParser so that when there's an error
    (e.g., an unrecognized argument), it prints the full
    help text instead of just a short usage message.
    Also overrides help to be more concise & colored.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Provide a custom usage line, remove default 'positional arguments' display
        self.usage = "\033[1;34mUsage:\033[0m summary.py [OPTIONS] [FILES...]"

    def error(self, message):
        # Print our custom help on error
        sys.stderr.write(f"\n\033[1;31mError:\033[0m {message}\n\n")
        self.print_help()
        sys.exit(2)

    def print_help(self):
        # Print a simpler, colored help message (override default).
        # We omit big details about "positional arguments," synonyms, etc.
        help_text = f"""
\033[1;34mUsage:\033[0m summary.py [OPTIONS] [FILES...]

\033[1;36mScan Python files for FileName, version, Summary, and Tags.\033[0m

\033[1;33mOptions:\033[0m
  \033[1;32m-r, --root\033[0m
    Root directory to search for .py files (default is current dir).

  \033[1;32m-f, --files\033[0m
    Specific .py files to summarize. Overrides auto-discovery.

  \033[1;32m-t, --tags\033[0m
    Filter results by these tag(s). Multiple tags => include if any match.

  \033[1;32m-s, --search\033[0m
    Case-insensitive search in OS filename, FileName header, version, summary, or tags.

  \033[1;32m-pc, --print-code\033[0m
    Print the full code for each matched file to console.

  \033[1;32m-sj, --save-json\033[0m  [optional filename or no argument]
    Save results to JSON file. No argument => auto-naming.

  \033[1;32m-sc, --save-code\033[0m  [optional filename or no argument]
    Save all matched files' code to a .txt file, with a blank line separating each file.
    No argument => auto-naming.

  \033[1;32m-h, --help\033[0m
    Show this help message and exit.

Examples:
  summary.py --root . --tags engine --print-code
  summary.py -s 'animation' -pc -sc code_dump.txt
"""
        sys.stdout.write(help_text + "\n")


def gather_all_py_files(root_dir: str) -> List[str]:
    """
    Recursively gather all .py files under root_dir.
    """
    all_py = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".py"):
                full_path = os.path.join(dirpath, fname)
                all_py.append(full_path)
    return all_py


def parse_summaries_from_file(filepath: str) -> Dict:
    """
    Parse the file for:
        # FileName: ...
        # version: ...
        # Summary: ...
        # Tags: ...
    Returns a dict with:
       {
         "filename": os.path.basename(filepath),
         "fullpath": filepath,
         "header_filename": str or None,
         "version": str or None,
         "summary": str or None,
         "tags": [list of strings],
       }
    """
    header_filename = None
    version_str     = None
    summary_str     = None
    tags_list       = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line_stripped = line.strip()

                # Check for each pattern
                match_fileheader = RE_FILEHEADER.match(line_stripped)
                if match_fileheader:
                    header_filename = match_fileheader.group(1).strip()
                    continue

                match_version = RE_VERSION.match(line_stripped)
                if match_version:
                    version_str = match_version.group(1).strip()
                    continue

                match_summary = RE_SUMMARY.match(line_stripped)
                if match_summary:
                    summary_str = match_summary.group(1).strip()
                    continue

                match_tags = RE_TAGS.match(line_stripped)
                if match_tags:
                    raw_tags = match_tags.group(1).strip()
                    tags_list = [
                        t.strip()
                        for t in re.split(r'[,\s]+', raw_tags)
                        if t.strip()
                    ]
    except (IOError, OSError):
        pass

    return {
        "filename": os.path.basename(filepath),
        "fullpath": filepath,
        "header_filename": header_filename,
        "version": version_str,
        "summary": summary_str,
        "tags": tags_list
    }


def main():
    parser = CustomArgParser(
        add_help=False,  # We'll add our custom -h/--help
        description="Scan Python files for FileName, version, Summary, and Tags."
    )

    # Add a simple custom help
    parser.add_argument(
        "-h", "--help",
        action="store_true",
        help=argparse.SUPPRESS
    )

    parser.add_argument(
        "-r", "--root",
        default=".",
        help="Root directory to search for .py files (default current dir)."
    )
    parser.add_argument(
        "-f", "--files",
        nargs="*",
        default=None,
        help="Specific .py files to summarize. This overrides auto-discovery."
    )
    parser.add_argument(
        "-t", "--tags",
        nargs="*",
        default=None,
        help="Filter results by these tag(s). Multiple tags => any match triggers inclusion."
    )
    parser.add_argument(
        "-s", "--search",
        default=None,
        help="Search term (case-insensitive) in OS filename, # FileName, version, summary, or tags."
    )
    parser.add_argument(
        "-pc", "--print-code",
        action="store_true",
        help="If specified, also print the full code for each matched file."
    )
    # Save JSON (auto or custom name)
    parser.add_argument(
        "-sj", "--save-json",
        nargs="?",
        const="AUTO",
        default=None,
        help="Save results as JSON to a file. If no argument => auto-naming."
    )
    # Save code to a .txt file (auto or custom name)
    parser.add_argument(
        "-sc", "--save-code",
        nargs="?",
        const="AUTO",
        default=None,
        help="Save full code of matched files to a .txt file. If no argument => auto-naming."
    )

    # Hidden positional argument(s), not shown in help
    parser.add_argument(
        "files_pos",
        nargs="*",
        help=argparse.SUPPRESS
    )

    args = parser.parse_args()

    # If user asked for help, show it and exit
    if args.help:
        parser.print_help()
        sys.exit(0)

    # Merge positional files with --files if any
    if args.files_pos:
        if args.files is not None:
            args.files.extend(args.files_pos)
        else:
            args.files = args.files_pos

    # 1) Determine which files to process
    if args.files:
        py_files = [os.path.abspath(f) for f in args.files]
    else:
        py_files = gather_all_py_files(os.path.abspath(args.root))

    # 2) Parse each file for summaries
    all_summaries = []
    for fpath in py_files:
        info = parse_summaries_from_file(fpath)
        all_summaries.append(info)

    # 3) Filter by tags if specified
    if args.tags:
        lower_tags = [t.lower() for t in args.tags]
        filtered = []
        for summ in all_summaries:
            file_tags_lower = [t.lower() for t in summ["tags"]]
            if any(t in file_tags_lower for t in lower_tags):
                filtered.append(summ)
        all_summaries = filtered

    # 4) Filter by search term (checks file name, FileName line, version, summary, and tags)
    if args.search:
        search_lower = args.search.lower()
        filtered = []
        for summ in all_summaries:
            text_to_search = summ["filename"].lower()
            if summ["header_filename"]:
                text_to_search += " " + summ["header_filename"].lower()
            if summ["version"]:
                text_to_search += " " + summ["version"].lower()
            if summ["summary"]:
                text_to_search += " " + summ["summary"].lower()
            if summ["tags"]:
                text_to_search += " " + " ".join(t.lower() for t in summ["tags"])
            if search_lower in text_to_search:
                filtered.append(summ)
        all_summaries = filtered

    # 5) Display results in console (with some color)
    for summ in all_summaries:
        print(f"\033[93m{'=' * 60}\033[0m")
        print(f"\033[92mFile:\033[0m {summ['filename']}  \033[94m(Path:\033[0m {summ['fullpath']}\033[94m)\033[0m")
        print(f"\033[92mFileName header:\033[0m {summ['header_filename'] or '[None found]'}")
        print(f"\033[92mVersion:\033[0m {summ['version'] or '[None found]'}")
        print(f"\033[92mSummary:\033[0m {summ['summary'] or '[None found]'}")
        if summ["tags"]:
            print(f"\033[92mTags:\033[0m {', '.join(summ['tags'])}")
        else:
            print("\033[92mTags:\033[0m [None found]")

        # 6) Print code if requested
        if args.print_code:
            print(f"\033[96m{'-' * 60}\033[0m")
            print("\033[95mFile Content:\033[0m")
            print(f"\033[96m{'-' * 60}\033[0m")
            try:
                with open(summ["fullpath"], "r", encoding="utf-8") as fc:
                    code_lines = fc.read()
                print(code_lines)
            except Exception as e:
                print(f"Error reading file content: {e}")

    # 7) If requested, save results to JSON
    #    (We do the "stype + date" naming if user didn't provide a filename)
    json_file_path = None
    if args.save_json is not None:
        if args.save_json == "AUTO":
            # Automatic filename
            if args.search:
                stype = f"search_{args.search}"
            elif args.tags:
                stype = "tags_" + "_".join(args.tags)
            elif args.files:
                stype = "files"
            else:
                stype = "all"
            short_dt = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("./summary_print", exist_ok=True)
            json_file_path = f"./summary_print/{stype}_results_{short_dt}.json"
        else:
            json_file_path = args.save_json

        try:
            with open(json_file_path, "w", encoding="utf-8") as outfile:
                json.dump(all_summaries, outfile, indent=2)
            print(f"\n\033[92mSaved summary data to JSON:\033[0m {json_file_path}")
        except Exception as e:
            print(f"Error saving JSON data: {e}")

    # 8) If requested, save the full code of matched files to a text file
    #    (We reuse the same "stype + date" pattern as JSON, just .txt)
    if args.save_code is not None:
        if args.save_code == "AUTO":
            # If we already auto-named for JSON, use the same base
            if json_file_path and args.save_json == "AUTO":
                # same base name as the JSON, but with .txt
                outfile_code_path = os.path.splitext(json_file_path)[0] + ".txt"
            else:
                # Automatic naming if JSON not used or user provided a custom JSON path
                if args.search:
                    stype = f"search_{args.search}"
                elif args.tags:
                    stype = "tags_" + "_".join(args.tags)
                elif args.files:
                    stype = "files"
                else:
                    stype = "all"
                short_dt = datetime.now().strftime("%Y%m%d_%H%M%S")
                os.makedirs("./summary_print", exist_ok=True)
                outfile_code_path = f"./summary_print/{stype}_results_{short_dt}.txt"
        else:
            outfile_code_path = args.save_code

        try:
            os.makedirs(os.path.dirname(outfile_code_path), exist_ok=True)
        except OSError:
            # Might happen if user gave just a filename without directory
            pass

        try:
            with open(outfile_code_path, "w", encoding="utf-8") as out_file:
                for idx, summ in enumerate(all_summaries):
                    # Attempt to read the file code
                    code_data = ""
                    try:
                        with open(summ["fullpath"], "r", encoding="utf-8") as fc:
                            code_data = fc.read()
                    except Exception as e:
                        code_data = f"Error reading file: {e}\n"

                    # Write a header, then the code, then a blank line
                    out_file.write(f"==== File: {summ['filename']} ====\n")
                    out_file.write(code_data)
                    out_file.write("\n\n")  # blank line between files

            print(f"\n\033[92mSaved code to:\033[0m {outfile_code_path}")
        except Exception as e:
            print(f"Error saving code to file: {e}")


if __name__ == "__main__":
    main()
