#!/usr/bin/env python3
"""
Collate all distribution requirements from a locally downloaded catalog.
Reads data/{roster}/*.json and produces:
  - data/{roster}/distr_reqs.json   — all unique req codes with metadata + which courses carry them
  - printed summary table to stdout

Usage:
    python collate_distr_reqs.py FA26
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path


def collate(roster: str) -> None:
    data_dir = Path("data") / roster
    if not data_dir.exists():
        raise SystemExit(f"No data found at {data_dir}. Run download_catalog.py {roster} first.")

    files = sorted(data_dir.glob("*.json"))
    # Exclude any previously generated output files
    files = [f for f in files if f.stem not in ("distr_reqs",)]

    # code -> {crseAttr, crseAttrValue, descr, descrformal, courses: [{subject, catalogNbr, title}]}
    reqs: dict[str, dict] = {}

    total_classes = 0
    total_with_distr = 0

    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        classes = data.get("data", {}).get("classes", [])
        total_classes += len(classes)

        for c in classes:
            attrs = c.get("crseAttrs", [])
            distr_attrs = [a for a in attrs if a.get("attrDescrShort") == "DistReq"]
            if not distr_attrs:
                continue

            total_with_distr += 1
            course_ref = {
                "subject": c.get("subject", ""),
                "catalogNbr": c.get("catalogNbr", ""),
                "titleShort": c.get("titleShort", ""),
            }

            for attr in distr_attrs:
                code = attr["crseAttrValue"]
                if code not in reqs:
                    reqs[code] = {
                        "crseAttr": attr.get("crseAttr", ""),
                        "crseAttrValue": code,
                        "descr": attr.get("descr", ""),
                        "descrformal": attr.get("descrformal", ""),
                        "course_count": 0,
                        "courses": [],
                    }
                reqs[code]["course_count"] += 1
                reqs[code]["courses"].append(course_ref)

    # Sort by code
    sorted_reqs = dict(sorted(reqs.items()))

    out_file = data_dir / "distr_reqs.json"
    out_file.write_text(json.dumps(sorted_reqs, indent=2), encoding="utf-8")

    # Print summary table
    subjects_covered = len(files)
    print(f"Roster:   {roster}")
    print(f"Subjects: {subjects_covered}")
    print(f"Classes:  {total_classes}  ({total_with_distr} have at least one distr req)")
    print(f"Unique distribution requirement codes: {len(reqs)}")
    print()
    print(f"{'Code':<16} {'Count':>6}  Description")
    print("-" * 60)
    for code, meta in sorted_reqs.items():
        print(f"{code:<16} {meta['course_count']:>6}  {meta['descr']}")

    print(f"\nFull data written to {out_file}")


def main():
    parser = argparse.ArgumentParser(description="Collate distribution requirements from local catalog.")
    parser.add_argument("roster", help="Roster code, e.g. FA26")
    args = parser.parse_args()
    collate(args.roster.upper())


if __name__ == "__main__":
    main()
