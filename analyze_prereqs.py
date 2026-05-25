#!/usr/bin/env python3
"""
Export parsed prerequisite data to CSV for manual review.
Output: data/{roster}/prereqs_analysis.csv

Usage:
    python analyze_prereqs.py FA26
    python analyze_prereqs.py FA26 --career UG
    python analyze_prereqs.py FA26 --complexity hard
    python analyze_prereqs.py FA26 --complexity hard --career UG

Complexity levels:
    simple  — 1 clause, 1 code, no vague terms  (trivially correct)
    medium  — 1-2 clauses, no vague terms        (code-checkable)
    hard    — 3+ clauses OR any vague term       (needs manual review)
"""

import argparse
import csv
import json
from pathlib import Path


def describe_clause(cl):
    sep = ' or ' if cl['logic'] == 'or' else ' + '
    codes = sep.join(cl['codes']) if cl['codes'] else '[unrecognized]'
    if cl['orEquiv']:
        codes += ' (or vague)'
    return codes


def describe_parsed(p):
    if not p or not p.get('clauses'):
        return ''
    return '  AND  '.join(describe_clause(cl) for cl in p['clauses'])


def complexity(p):
    if not p or not p.get('clauses'):
        return 'unparsed'
    clauses = p['clauses']
    has_vague = any(cl['orEquiv'] for cl in clauses)
    total_codes = sum(len(cl['codes']) for cl in clauses)
    if has_vague:
        return 'hard'
    if len(clauses) >= 3 or total_codes >= 5:
        return 'hard'
    if len(clauses) == 1 and total_codes == 1:
        return 'simple'
    return 'medium'


def main():
    parser = argparse.ArgumentParser(description='Export prereq analysis to CSV.')
    parser.add_argument('roster', help='Roster code, e.g. FA26')
    parser.add_argument('--career', help='Filter by acadCareer (e.g. UG, GR)')
    parser.add_argument('--complexity', choices=['simple', 'medium', 'hard'],
                        help='Filter by complexity level')
    args = parser.parse_args()

    roster = args.roster.upper()
    data = json.loads((Path('data') / roster / 'catalog.json').read_text(encoding='utf-8'))
    courses = data['courses']

    rows = []
    for c in courses:
        p = c.get('prereqParsed')
        if not p:
            continue
        career = c.get('acadCareer', '')
        if args.career and career != args.career.upper():
            continue
        comp = complexity(p)
        if args.complexity and comp != args.complexity:
            continue

        clauses = p.get('clauses', [])
        rows.append({
            'courseId':    c['courseId'],
            'subject':     c['subject'],
            'career':      career,
            'complexity':  comp,
            'numClauses':  len(clauses),
            'hasVague':    any(cl['orEquiv'] for cl in clauses),
            'prereqs_raw': c.get('prereqs', ''),
            'prereqs_parsed': describe_parsed(p),
        })

    suffix = ('_' + args.career.upper() if args.career else '') + \
             ('_' + args.complexity    if args.complexity else '')
    out_path = Path('data') / roster / f'prereqs_analysis{suffix}.csv'
    fieldnames = ['courseId', 'subject', 'career', 'complexity', 'numClauses',
                  'hasVague', 'prereqs_raw', 'prereqs_parsed']
    with out_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    counts = {}
    for r in rows:
        counts[r['complexity']] = counts.get(r['complexity'], 0) + 1
    print(f'Wrote {len(rows)} rows to {out_path}')
    for level in ('simple', 'medium', 'hard'):
        print(f'  {level:<8} {counts.get(level, 0):4d}')


if __name__ == '__main__':
    main()
