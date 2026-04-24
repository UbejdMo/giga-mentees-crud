"""
app.py — GigaAcademy Mentees Tracker

Level 1: Implement the four CRUD functions below, then wire up the menu loop.
Level 2: See hints at the bottom of this file and in the brief.

Rules (non-negotiable):
  - Use psycopg v3 for the database driver.
  - Use parameterised queries (%s placeholders). NEVER f-strings or concatenation.
  - Read connection details from environment variables (see .env.example).
  - Commit your inserts/updates/deletes.
"""

import os
import sys

import psycopg
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def get_connection():
    """Open a new connection using environment variables.

    Returns a psycopg.Connection. Caller is responsible for closing it,
    or use it as a context manager: `with get_connection() as conn: ...`
    """
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


# ---------------------------------------------------------------------------
# Level 1 — CRUD functions (YOU implement these)
# ---------------------------------------------------------------------------

def create_mentee(full_name: str, email: str, cohort: str) -> int:
    """Insert a new mentee. Return the new mentee's id."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Insert a new row and get back the auto-generated id in one step.
            # %s placeholders keep user input safely separate from the SQL command.
            cur.execute(
                """
                INSERT INTO mentees (full_name, email, cohort)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (full_name, email, cohort),
            )
            new_id = cur.fetchone()[0]
        # conn.__exit__ commits automatically when the `with` block succeeds.
    return new_id


def list_mentees() -> list[tuple]:
    """Return all mentees as a list of tuples, sorted by full_name.

    Each tuple: (id, full_name, email, cohort, enrolled_on).
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Retrieve every row, sorted alphabetically by name.
            cur.execute(
                """
                SELECT id, full_name, email, cohort, enrolled_on
                FROM mentees
                ORDER BY full_name
                """
            )
            return cur.fetchall()


def update_mentee(mentee_id: int, new_cohort: str) -> bool:
    """Update a mentee's cohort. Return True if a row was updated, False otherwise."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            # WHERE id = %s ensures we only touch the one intended row.
            cur.execute(
                """
                UPDATE mentees
                SET cohort = %s
                WHERE id = %s
                """,
                (new_cohort, mentee_id),
            )
            # rowcount tells us how many rows the UPDATE actually changed.
            return cur.rowcount == 1


def delete_mentee(mentee_id: int) -> bool:
    """Delete a mentee by id. Return True if a row was deleted, False otherwise."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            # WHERE id = %s ensures we only delete the one intended row.
            cur.execute(
                "DELETE FROM mentees WHERE id = %s",
                (mentee_id,),
            )
            return cur.rowcount == 1


# ---------------------------------------------------------------------------
# Menu loop (YOU implement this for Level 1)
# ---------------------------------------------------------------------------

def print_menu() -> None:
    print()
    print("GigaAcademy Mentees Tracker")
    print("  1) Add mentee")
    print("  2) List mentees")
    print("  3) Update cohort")
    print("  4) Delete mentee")
    print("  0) Quit")


def run_menu() -> None:
    """Run the interactive CLI menu until the user chooses to quit."""
    while True:
        print_menu()
        choice = input("Enter choice: ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        elif choice == "1":
            name   = input("Full name:  ").strip()
            email  = input("Email:      ").strip()
            cohort = input("Cohort:     ").strip()

            if not name or not email or not cohort:
                print("Error: all fields are required.")
                continue

            try:
                new_id = create_mentee(name, email, cohort)
                print(f"Mentee added with id {new_id}.")
            except psycopg.errors.UniqueViolation:
                # Triggered when the email already exists in the table.
                print("Error: that email address is already registered.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "2":
            try:
                rows = list_mentees()
            except Exception as e:
                print(f"Error: {e}")
                continue

            if not rows:
                print("No mentees found.")
            else:
                print(f"\n{'ID':<5} {'Name':<25} {'Email':<30} {'Cohort':<12} {'Enrolled'}")
                print("-" * 80)
                for mid, name, email, cohort, enrolled in rows:
                    print(f"{mid:<5} {name:<25} {email:<30} {cohort:<12} {enrolled}")

        elif choice == "3":
            raw_id = input("Mentee ID to update: ").strip()
            if not raw_id.isdigit():
                print("Error: please enter a valid numeric ID.")
                continue

            new_cohort = input("New cohort: ").strip()
            if not new_cohort:
                print("Error: cohort cannot be empty.")
                continue

            try:
                updated = update_mentee(int(raw_id), new_cohort)
                if updated:
                    print(f"Mentee {raw_id} updated.")
                else:
                    print(f"No mentee found with id {raw_id}.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "4":
            raw_id = input("Mentee ID to delete: ").strip()
            if not raw_id.isdigit():
                print("Error: please enter a valid numeric ID.")
                continue

            # Confirm before deleting — this action cannot be undone.
            confirm = input(f"Delete mentee {raw_id}? This cannot be undone. (yes/no): ").strip().lower()
            if confirm != "yes":
                print("Cancelled.")
                continue

            try:
                deleted = delete_mentee(int(raw_id))
                if deleted:
                    print(f"Mentee {raw_id} deleted.")
                else:
                    print(f"No mentee found with id {raw_id}.")
            except Exception as e:
                print(f"Error: {e}")

        else:
            print("Invalid choice. Please enter 0, 1, 2, 3, or 4.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        run_menu()
    except KeyboardInterrupt:
        print("\nBye.")
        sys.exit(0)


# ===========================================================================
# LEVEL 2 HINTS (ignore if you're on Level 1)
# ===========================================================================
#
# 1. Split this file. Create a package with:
#       db.py     -> get_connection()
#       queries.py -> all the SQL functions
#       cli.py     -> argparse subparsers that call into queries.py
#       app.py    -> just the entry point
#
# 2. For Part B (transactions), the pattern is:
#
#       with get_connection() as conn:
#           with conn.cursor() as cur:
#               cur.execute(...)  # insert assessment
#               for email, score in scores_by_email.items():
#                   cur.execute(...)  # insert score
#       # psycopg commits on successful __exit__ of the connection context,
#       # and rolls back if any exception propagated out.
#
# 3. For Part C, start with `argparse.ArgumentParser` and use `.add_subparsers()`
#    for the `mentee`, `report`, and `assessment` command groups.
