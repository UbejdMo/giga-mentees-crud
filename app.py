"""
app.py — GigaAcademy Mentees Tracker (Level 2)

Entry point. Parses CLI arguments and delegates to db.queries.
Run with:  python app.py --help
"""

import argparse
import sys

import psycopg

from db.queries import (
    create_mentee,
    list_mentees,
    update_mentee,
    delete_mentee,
    average_score_per_mentee,
    mentees_below_threshold,
    assessment_summary,
    record_assessment_with_scores,
)


# ---------------------------------------------------------------------------
# mentee subcommands
# ---------------------------------------------------------------------------

def cmd_mentee_add(args: argparse.Namespace) -> None:
    try:
        new_id = create_mentee(args.name, args.email, args.cohort)
        print(f"Mentee added with id {new_id}.")
    except psycopg.errors.UniqueViolation:
        print("Error: that email address is already registered.")
        sys.exit(1)


def cmd_mentee_list(_args: argparse.Namespace) -> None:
    rows = list_mentees()
    if not rows:
        print("No mentees found.")
        return
    print(f"\n{'ID':<5} {'Name':<25} {'Email':<30} {'Cohort':<12} {'Enrolled'}")
    print("-" * 80)
    for mid, name, email, cohort, enrolled in rows:
        print(f"{mid:<5} {name:<25} {email:<30} {cohort:<12} {enrolled}")


def cmd_mentee_update(args: argparse.Namespace) -> None:
    updated = update_mentee(args.id, args.cohort)
    if updated:
        print(f"Mentee {args.id} updated.")
    else:
        print(f"No mentee found with id {args.id}.")
        sys.exit(1)


def cmd_mentee_delete(args: argparse.Namespace) -> None:
    deleted = delete_mentee(args.id)
    if deleted:
        print(f"Mentee {args.id} deleted.")
    else:
        print(f"No mentee found with id {args.id}.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# report subcommands
# ---------------------------------------------------------------------------

def cmd_report_averages(_args: argparse.Namespace) -> None:
    rows = average_score_per_mentee()
    if not rows:
        print("No scores recorded yet.")
        return
    print(f"\n{'Name':<25} {'Avg %':>7}")
    print("-" * 34)
    for name, avg in rows:
        print(f"{name:<25} {avg:>6}%")


def cmd_report_struggling(args: argparse.Namespace) -> None:
    rows = mentees_below_threshold(args.threshold)
    if not rows:
        print(f"No mentees below {args.threshold}%.")
        return
    print(f"\nMentees below {args.threshold}%:")
    print(f"\n{'Name':<25} {'Avg %':>7}")
    print("-" * 34)
    for name, avg in rows:
        print(f"{name:<25} {avg:>6}%")


def cmd_report_summary(_args: argparse.Namespace) -> None:
    rows = assessment_summary()
    if not rows:
        print("No assessments recorded yet.")
        return
    print(f"\n{'Title':<25} {'Date':<12} {'Max':>5} {'N':>4} {'Avg %':>7}")
    print("-" * 57)
    for title, held_on, max_score, count, avg in rows:
        print(f"{title:<25} {str(held_on):<12} {max_score:>5} {count:>4} {avg:>6}%")


# ---------------------------------------------------------------------------
# assessment subcommand
# ---------------------------------------------------------------------------

def cmd_assessment_record(args: argparse.Namespace) -> None:
    """Parse comma-separated 'mentee_id:score' pairs and record the assessment."""
    scores = []
    for pair in args.scores:
        try:
            mentee_id, score = pair.split(":")
            scores.append((int(mentee_id), int(score)))
        except ValueError:
            print(f"Error: '{pair}' is not a valid id:score pair.")
            sys.exit(1)

    try:
        assessment_id = record_assessment_with_scores(
            args.title, args.max_score, args.date, scores
        )
        print(f"Assessment recorded with id {assessment_id} ({len(scores)} scores).")
    except psycopg.errors.ForeignKeyViolation:
        print("Error: one or more mentee IDs do not exist.")
        sys.exit(1)
    except psycopg.errors.UniqueViolation:
        print("Error: a mentee appears more than once in the score list.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI definition
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="app.py",
        description="GigaAcademy Mentee Tracker — Level 2 CLI",
    )
    sub = parser.add_subparsers(dest="group", metavar="<command>", required=True)

    # ---- mentee ----
    mentee = sub.add_parser("mentee", help="manage mentees")
    msub = mentee.add_subparsers(dest="action", metavar="<action>", required=True)

    p = msub.add_parser("add", help="add a new mentee")
    p.add_argument("--name",   required=True)
    p.add_argument("--email",  required=True)
    p.add_argument("--cohort", required=True)
    p.set_defaults(func=cmd_mentee_add)

    p = msub.add_parser("list", help="list all mentees")
    p.set_defaults(func=cmd_mentee_list)

    p = msub.add_parser("update", help="update a mentee's cohort")
    p.add_argument("--id",     required=True, type=int)
    p.add_argument("--cohort", required=True)
    p.set_defaults(func=cmd_mentee_update)

    p = msub.add_parser("delete", help="delete a mentee by id")
    p.add_argument("--id", required=True, type=int)
    p.set_defaults(func=cmd_mentee_delete)

    # ---- report ----
    report = sub.add_parser("report", help="view reports")
    rsub = report.add_subparsers(dest="action", metavar="<action>", required=True)

    p = rsub.add_parser("averages", help="average score per mentee")
    p.set_defaults(func=cmd_report_averages)

    p = rsub.add_parser("struggling", help="mentees below a score threshold")
    p.add_argument("--threshold", required=True, type=float,
                   help="percentage threshold (e.g. 60)")
    p.set_defaults(func=cmd_report_struggling)

    p = rsub.add_parser("summary", help="summary of all assessments")
    p.set_defaults(func=cmd_report_summary)

    # ---- assessment ----
    assessment = sub.add_parser("assessment", help="record assessments")
    asub = assessment.add_subparsers(dest="action", metavar="<action>", required=True)

    p = asub.add_parser("record", help="record a new assessment with scores")
    p.add_argument("--title",     required=True)
    p.add_argument("--max-score", required=True, type=int, dest="max_score")
    p.add_argument("--date",      required=True, help="YYYY-MM-DD")
    p.add_argument("scores", nargs="+", metavar="id:score",
                   help="one or more mentee_id:score pairs, e.g. 1:85 3:72")
    p.set_defaults(func=cmd_assessment_record)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nBye.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
