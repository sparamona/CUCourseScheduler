#!/usr/bin/env python3
"""
Download the full Cornell course catalog for a given roster, one subject at a time.
Results are stored in ./data/{roster}/ as JSON files.

Usage:
    python download_catalog.py FA26
    python download_catalog.py SP26
"""

import argparse
import json
import sys
import time
from pathlib import Path

import urllib.request
import urllib.error
from tqdm import tqdm

BASE_URL = "https://classes.cornell.edu/api/2.0"
DELAY_SECONDS = 1.5


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "CUCourseScheduler/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def get_subjects(roster: str) -> list[dict]:
    url = f"{BASE_URL}/config/subjects.json?roster={roster}"
    data = fetch_json(url)
    return data["data"]["subjects"]


def download_catalog(roster: str, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching subject list for {roster}...")
    subjects = get_subjects(roster)
    print(f"Found {len(subjects)} subjects.")

    skipped = 0
    errors = []

    with tqdm(subjects, desc=roster, unit="subj", dynamic_ncols=True) as bar:
        for subject in bar:
            code = subject["value"]
            out_file = out_dir / f"{code}.json"

            if out_file.exists():
                skipped += 1
                bar.set_postfix(subject=code, status="skip")
                continue

            url = f"{BASE_URL}/search/classes.json?roster={roster}&subject={code}"
            try:
                data = fetch_json(url)
                out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                count = len(data.get("data", {}).get("classes", []))
                bar.set_postfix(subject=code, classes=count)
            except urllib.error.HTTPError as e:
                errors.append(code)
                bar.set_postfix(subject=code, status=f"HTTP {e.code}")
            except Exception as e:
                errors.append(code)
                bar.set_postfix(subject=code, status="ERR")

            time.sleep(DELAY_SECONDS)

    print(f"\nDone. Files written to {out_dir}")
    if skipped:
        print(f"Skipped {skipped} already-downloaded subjects.")
    if errors:
        print(f"Errors on: {', '.join(errors)}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Download Cornell course catalog.")
    parser.add_argument("roster", help="Roster code, e.g. FA26, SP26, FA25")
    args = parser.parse_args()

    roster = args.roster.upper()
    out_dir = Path("data") / roster
    download_catalog(roster, out_dir)


if __name__ == "__main__":
    main()
