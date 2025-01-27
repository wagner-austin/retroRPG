#!/usr/bin/env python3
"""
summary.py

A command-line tool to scan Python files in a project directory for short/long
summaries, tags, and optionally search in filenames, short/long summaries, and tags.

Features:
  - Automatically discover all *.py files (except itself).
  - Extract short/long summaries and tags from special comment lines:
        # Summary (short): ...
        # Summary (long):  ...
        # Tags: ...
  - Filter by file(s), tags, or search terms.
  - Print code from chosen files.
  - Save summary data as JSON. If "--save-json" is given with no argument,
    it automatically creates:
      ./summary_print/<search_type>_results_YYYYMMDD_HHMMSS.json
"""

import os
import re
import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional

# Regex patterns for single-line extraction:
RE_SHORT = re.compile(r'^#\s*Summary\s*short\s*:\s*(.*)$', re.IGNORECASE)
RE_LONG  = re.compile(r'^#\s*Summary\s*long\s*:\s*(.*)$', re.IGNORECASE)
RE_TAGS  = re.compile(r'^#\s*Tags\s*:\s*(.*)$', re.IGNORECASE)

def gather_all_py_files(root_dir: str) -> List[str]:
    """
    Recursively gather all .py files under root_dir, excluding summary.py itself.
    """
    all_py = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".py") and fname != "summary.py":
                full_path = os.path.join(dirpath, fname)
                all_py.append(full_path)
    return all_py

def parse_summaries_from_file(filepath: str) -> Dict:
    """
    Parse the file for single-line summary info:
        # Summary (short): ...
        # Summary (long):  ...
        # Tags: ...
    Returns a dict with:
       {
         "filename":  (basename),
         "fullpath":  (absolute path),
         "short_summary": str or None,
         "long_summary":  str or None,
         "tags": [list of strings],
       }
    """
    short_summary = None
    long_summary  = None
    tags_list     = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line_stripped = line.strip()
                
                m_short = RE_SHORT.match(line_stripped)
                if m_short:
                    short_summary = m_short.group(1).strip()
                    continue

                m_long = RE_LONG.match(line_stripped)
                if m_long:
                    long_summary = m_long.group(1).strip()
                    continue

                m_tags = RE_TAGS.match(line_stripped)
                if m_tags:
                    raw_tags = m_tags.group(1).strip()
                    # split by commas or whitespace
                    tags_list = [t.strip() for t in re.split(r'[,\s]+', raw_tags) if t.strip()]
    except (IOError, OSError):
        pass

    return {
        "filename": os.path.basename(filepath),
        "fullpath": filepath,
        "short_summary": short_summary,
        "long_summary": long_summary,
        "tags": tags_list
    }

def main():
    parser = argparse.ArgumentParser(
        description="Scan Python files for short/long summaries and tags."
    )

    parser.add_argument(
        "--root",
        default=".",
        help="Root directory to search for .py files (default current dir)."
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="Specific .py files to summarize (overrides auto-discovery)."
    )
    parser.add_argument(
        "--tags",
        nargs="*",
        default=None,
        help="Filter results by these tag(s). Multiple tags => any match triggers inclusion."
    )
    parser.add_argument(
        "--search",
        default=None,
        help="Search term (case-insensitive) in filename, short/long summary, or tags."
    )
    parser.add_argument(
        "--summary-type",
        choices=["short", "long", "both"],
        default="short",
        help="Display short summary, long summary, or both. (default: short)"
    )
    parser.add_argument(
        "--print-code",
        action="store_true",
        help="If specified, also print the full code for each matched file."
    )
    # We set nargs='?' so user can do:
    #   --save-json        (auto-generate name)
    #   --save-json myfile.json (use a custom name)
    #   or omit it entirely
    parser.add_argument(
        "--save-json",
        nargs="?",
        const="AUTO",
        default=None,
        help="Save results as JSON to a file. If given with no argument => auto-naming."
    )

    args = parser.parse_args()

    # Determine which files to process
    if args.files:
        py_files = [os.path.abspath(f) for f in args.files]
    else:
        py_files = gather_all_py_files(os.path.abspath(args.root))

    # Parse each file for summaries
    all_summaries = []
    for fpath in py_files:
        info = parse_summaries_from_file(fpath)
        all_summaries.append(info)

    # Filter by tags
    if args.tags:
        lower_tags = [t.lower() for t in args.tags]
        filtered = []
        for summ in all_summaries:
            file_tags_lower = [t.lower() for t in summ["tags"]]
            if any(t in file_tags_lower for t in lower_tags):
                filtered.append(summ)
        all_summaries = filtered

    # Filter by search
    if args.search:
        search_lower = args.search.lower()
        filtered = []
        for summ in all_summaries:
            # We'll search filename, short_summary, long_summary, and tags
            text_to_search = summ["filename"].lower()  # filename
            if summ["short_summary"]:
                text_to_search += " " + summ["short_summary"].lower()
            if summ["long_summary"]:
                text_to_search += " " + summ["long_summary"].lower()
            if summ["tags"]:
                text_to_search += " " + " ".join(t.lower() for t in summ["tags"])
            if search_lower in text_to_search:
                filtered.append(summ)
        all_summaries = filtered

    # Display results in console
    for summ in all_summaries:
        print("="*60)
        print(f"File: {summ['filename']}  (Path: {summ['fullpath']})")
        if args.summary_type in ("short", "both"):
            if summ["short_summary"]:
                print(f"Short Summary: {summ['short_summary']}")
            else:
                print("Short Summary: [None found]")
        if args.summary_type in ("long", "both"):
            if summ["long_summary"]:
                print(f"Long Summary: {summ['long_summary']}")
            else:
                print("Long Summary: [None found]")
        if summ["tags"]:
            print(f"Tags: {', '.join(summ['tags'])}")
        else:
            print("Tags: [None found]")

        # Print code if requested
        if args.print_code:
            print("-"*60)
            print("File Content:")
            print("-"*60)
            try:
                with open(summ["fullpath"], "r", encoding="utf-8") as fc:
                    code_lines = fc.read()
                print(code_lines)
            except Exception as e:
                print(f"Error reading file content: {e}")

    # If requested, save results to JSON
    if args.save_json is not None:
        # If user typed just --save-json (no argument), args.save_json == "AUTO"
        if args.save_json == "AUTO":
            # We figure out an automatic name
            # Decide the "search_type"
            if args.search:
                stype = f"search_{args.search}"
            elif args.tags:
                stype = "tags_" + "_".join(args.tags)
            elif args.files:
                stype = "files"
            else:
                stype = "all"

            short_dt = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Ensure our output dir exists
            os.makedirs("./summary_print", exist_ok=True)
            auto_filename = f"./summary_print/{stype}_results_{short_dt}.json"
            outfile_path = auto_filename
        else:
            # A custom path was given
            outfile_path = args.save_json

        try:
            with open(outfile_path, "w", encoding="utf-8") as outfile:
                json.dump(all_summaries, outfile, indent=2)
            print(f"\nSaved summary data to JSON: {outfile_path}")
        except Exception as e:
            print(f"Error saving JSON data: {e}")


if __name__ == "__main__":
    main()