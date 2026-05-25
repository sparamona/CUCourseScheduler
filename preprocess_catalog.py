#!/usr/bin/env python3
"""
Flatten downloaded catalog JSON into a single catalog.json for in-browser use.
Output: data/{roster}/catalog.json

Usage:
    python preprocess_catalog.py FA26
"""

import argparse
import json
import re
import datetime
from pathlib import Path

_COURSE_CODE = re.compile(r'[A-Z]{2,8}\s+\d{4}')
_OR_SIGNAL   = re.compile(r'\bor\b|one of|any of|at least one', re.I)

def parse_prereqs(text):
    if not text:
        return None
    codes = _COURSE_CODE.findall(text)
    if not codes:
        return None
    return {'codes': codes, 'logic': 'or' if _OR_SIGNAL.search(text) else 'and'}


def flatten_section(sec: dict, meetings: list) -> dict:
    flat = {
        "classNbr": sec.get("classNbr"),
        "component": sec.get("ssrComponent"),
        "componentLong": sec.get("ssrComponentLong"),
        "section": sec.get("section"),
        "openStatus": sec.get("openStatus"),  # "O" = open, "C" = closed, "W" = waitlist
        "instructionMode": sec.get("instrModeDescr"),
        "campus": sec.get("campusDescr"),
        "location": sec.get("locationDescr"),
        "meetings": [],
    }

    for m in meetings:
        instructors = [
            f"{i.get('firstName', '')} {i.get('lastName', '')}".strip()
            for i in m.get("instructors", [])
        ]
        flat["meetings"].append({
            "days": m.get("pattern", ""),
            "timeStart": m.get("timeStart", ""),
            "timeEnd": m.get("timeEnd", ""),
            "startDt": m.get("startDt", ""),
            "endDt": m.get("endDt", ""),
            "instructors": instructors,
        })

    return flat


def flatten_course(c: dict) -> dict:
    distr_attrs = [
        a for a in c.get("crseAttrs", [])
        if a.get("attrDescrShort") == "DistReq"
    ]
    explore_attrs = [
        a for a in c.get("crseAttrs", [])
        if a.get("attrDescrShort") == "ExplStudy"
    ]

    sections = []
    credits_min = None
    credits_max = None
    grading_basis = None

    for eg in c.get("enrollGroups", []):
        if credits_min is None:
            credits_min = eg.get("unitsMinimum")
            credits_max = eg.get("unitsMaximum")
            grading_basis = eg.get("gradingBasisLong")

        for sec in eg.get("classSections", []):
            flat_sec = flatten_section(sec, sec.get("meetings", []))
            flat_sec["componentsRequired"] = eg.get("componentsRequired", [])
            flat_sec["componentsOptional"] = eg.get("componentsOptional", [])
            sections.append(flat_sec)

    credits = (
        str(credits_min) if credits_min == credits_max
        else f"{credits_min}–{credits_max}"
    ) if credits_min is not None else ""

    return {
        "subject": c.get("subject", ""),
        "catalogNbr": c.get("catalogNbr", ""),
        "courseId": f"{c.get('subject', '')} {c.get('catalogNbr', '')}",
        "titleShort": c.get("titleShort", ""),
        "titleLong": c.get("titleLong", ""),
        "description": c.get("description", ""),
        "credits": credits,
        "acadCareer": c.get("acadCareer", ""),
        "acadGroup": c.get("acadGroup", ""),
        "distrReqs": [a["crseAttrValue"] for a in distr_attrs],
        "distrReqDescrs": [a["descr"] for a in distr_attrs],
        "explStudies": [a["crseAttrValue"] for a in explore_attrs],
        "explStudyDescrs": [a["descr"] for a in explore_attrs],
        "prereqs": c.get("catalogPrereq", "") or c.get("catalogPrereqCoreq", ""),
        "prereqParsed": parse_prereqs(c.get("catalogPrereq", "") or c.get("catalogPrereqCoreq", "")),
        "coreqs": c.get("catalogCoreq", ""),
        "crosslistings": c.get("catalogCrosslistings", ""),
        "enrollmentPriority": c.get("catalogEnrollmentPriority", "") or c.get("catalogPermission", ""),
        "gradingBasis": grading_basis or "",
        "lastTermsOffered": c.get("lastTermsOffered", ""),
        "whenOffered": c.get("catalogWhenOffered", ""),
        "sections": sections,
    }


def preprocess(roster: str) -> None:
    data_dir = Path("data") / roster
    files = sorted(f for f in data_dir.glob("*.json") if f.stem not in ("catalog", "distr_reqs", "adam"))

    all_courses = []
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        for c in data.get("data", {}).get("classes", []):
            all_courses.append(flatten_course(c))

    out_file = data_dir / "catalog.json"
    out_data = {
        "lastUpdated": datetime.date.today().isoformat(),
        "courses": all_courses
    }
    out_file.write_text(json.dumps(out_data), encoding="utf-8")

    size_mb = out_file.stat().st_size / 1_000_000
    print(f"Wrote {len(all_courses)} courses to {out_file} ({size_mb:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Preprocess catalog for browser use.")
    parser.add_argument("roster", help="Roster code, e.g. FA26")
    args = parser.parse_args()
    preprocess(args.roster.upper())


if __name__ == "__main__":
    main()
