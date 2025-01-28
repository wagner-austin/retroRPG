# FileName: summary.py
# version 1.3
# Summary: A command-line tool to scan Python files in a project directory for:
#   - FileName
#   - version
#   - Summary
#   - Tags
# 

# Tags: help, info, summary, tool

# It supports:
#   - Automatic discovery of all *.py files (except itself)
#   - Filtering by file(s), tags, or a search term (checks file name, FileName line,
#     version, summary, and tags)
#   - Optionally printing the full code for each matched file
#   - Saving summary data as JSON:
#      --save-json with no argument => automatically names file in ./summary_print/
#      --save-json myfile.json => saves with a custom name

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
    """
    def error(self, message):
        print(f"Error: {message}\n")
        self.print_help()
        sys.exit(2)


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
                    tags_list = [t.strip() for t in re.split(r'[,\s]+', raw_tags) if t.strip()]
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
        description="Scan Python files for FileName, version, Summary, and Tags.",
        usage="%(prog)s [options] [files ...]",  # Show positional usage
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Option flags/arguments: add multiple aliases (case/short forms)
    parser.add_argument(
        "-r", "--root", "--Root", "--ROOT",
        default=".",
        help="Root directory to search for .py files (default current dir)."
    )
    parser.add_argument(
        "-f", "--files", "--Files", "--FILES",
        nargs="*",
        default=None,
        help="Specific .py files to summarize. This overrides auto-discovery."
    )
    parser.add_argument(
        "-t", "--tags", "--tag", "--Tag", "--Tags", "--TAGS",
        nargs="*",
        default=None,
        help="Filter results by these tag(s). Multiple tags => any match triggers inclusion."
    )
    parser.add_argument(
        "-s", "--search", "--Search", "--SEARCH",
        default=None,
        help="Search term (case-insensitive) in OS filename, # FileName, version, summary, or tags."
    )
    parser.add_argument(
        "-pc", "--print-code", "--Print-code", "--PRINT-CODE",
        action="store_true",
        help="If specified, also print the full code for each matched file."
    )
    # We set nargs='?' so user can do:
    #   --save-json            (auto-generate name)
    #   --save-json myfile.json (use a custom name)
    parser.add_argument(
        "-sj", "--save-json", "--Save-json", "--SAVE-JSON",
        nargs="?",
        const="AUTO",
        default=None,
        help="Save results as JSON to a file. If given with no argument => auto-naming."
    )

    # Positional argument(s): user can place files at the end without --files
    parser.add_argument(
        "files_pos",
        nargs="*",
        help="One or more .py files to process directly without using --files."
    )

    args = parser.parse_args()

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

    # 4) Filter by search term (checks file name, # FileName, version, summary, and tags)
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

    # 5) Display results in console
    for summ in all_summaries:
        print("=" * 60)
        print(f"File: {summ['filename']}  (Path: {summ['fullpath']})")
        print(f"FileName header: {summ['header_filename'] or '[None found]'}")
        print(f"Version: {summ['version'] or '[None found]'}")
        print(f"Summary: {summ['summary'] or '[None found]'}")
        if summ["tags"]:
            print(f"Tags: {', '.join(summ['tags'])}")
        else:
            print("Tags: [None found]")

        # 6) Print code if requested
        if args.print_code:
            print("-" * 60)
            print("File Content:")
            print("-" * 60)
            try:
                with open(summ["fullpath"], "r", encoding="utf-8") as fc:
                    code_lines = fc.read()
                print(code_lines)
            except Exception as e:
                print(f"Error reading file content: {e}")

    # 7) If requested, save results to JSON
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
            outfile_path = f"./summary_print/{stype}_results_{short_dt}.json"
        else:
            outfile_path = args.save_json

        try:
            with open(outfile_path, "w", encoding="utf-8") as outfile:
                json.dump(all_summaries, outfile, indent=2)
            print(f"\nSaved summary data to JSON: {outfile_path}")
        except Exception as e:
            print(f"Error saving JSON data: {e}")


if __name__ == "__main__":
    main()