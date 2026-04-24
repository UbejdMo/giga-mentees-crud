import psycopg

from db.connection import get_connection


# ---------------------------------------------------------------------------
# Level 1 — Mentee CRUD
# ---------------------------------------------------------------------------

def create_mentee(full_name: str, email: str, cohort: str) -> int:
    """Insert a new mentee and return the new id."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO mentees (full_name, email, cohort)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (full_name, email, cohort),
            )
            return cur.fetchone()[0]


def list_mentees() -> list[tuple]:
    """Return all mentees sorted by name as (id, full_name, email, cohort, enrolled_on)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, full_name, email, cohort, enrolled_on
                FROM mentees
                ORDER BY full_name
                """
            )
            return cur.fetchall()


def update_mentee(mentee_id: int, new_cohort: str) -> bool:
    """Update a mentee's cohort. Return True if a row was updated."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE mentees SET cohort = %s WHERE id = %s",
                (new_cohort, mentee_id),
            )
            return cur.rowcount == 1


def delete_mentee(mentee_id: int) -> bool:
    """Delete a mentee by id. Return True if a row was deleted."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM mentees WHERE id = %s", (mentee_id,))
            return cur.rowcount == 1


# ---------------------------------------------------------------------------
# Level 2 — Assessment queries
# ---------------------------------------------------------------------------

def average_score_per_mentee() -> list[tuple]:
    """Return each mentee's average score as a percentage across all assessments.

    Result: (full_name, avg_pct) ordered from highest to lowest.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # JOIN brings together mentees, their scores, and each assessment's max_score.
            # AVG() and GROUP BY compute one average row per mentee.
            # ROUND(..., 1) gives us one decimal place.
            cur.execute(
                """
                SELECT
                    m.full_name,
                    ROUND(AVG(s.score * 100.0 / a.max_score), 1) AS avg_pct
                FROM assessment_scores s
                JOIN mentees     m ON m.id = s.mentee_id
                JOIN assessments a ON a.id = s.assessment_id
                GROUP BY m.id, m.full_name
                ORDER BY avg_pct DESC
                """
            )
            return cur.fetchall()


def mentees_below_threshold(threshold_pct: float) -> list[tuple]:
    """Return mentees whose average score percentage is below the given threshold.

    Result: (full_name, avg_pct).
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # HAVING filters groups after aggregation (WHERE filters rows before).
            cur.execute(
                """
                SELECT
                    m.full_name,
                    ROUND(AVG(s.score * 100.0 / a.max_score), 1) AS avg_pct
                FROM assessment_scores s
                JOIN mentees     m ON m.id = s.mentee_id
                JOIN assessments a ON a.id = s.assessment_id
                GROUP BY m.id, m.full_name
                HAVING AVG(s.score * 100.0 / a.max_score) < %s
                ORDER BY avg_pct ASC
                """,
                (threshold_pct,),
            )
            return cur.fetchall()


def assessment_summary() -> list[tuple]:
    """Return a summary of every assessment with participant count and average score.

    Result: (title, held_on, max_score, participant_count, avg_score).
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    a.title,
                    a.held_on,
                    a.max_score,
                    COUNT(s.mentee_id)                        AS participants,
                    ROUND(AVG(s.score * 100.0 / a.max_score), 1) AS avg_pct
                FROM assessments a
                LEFT JOIN assessment_scores s ON s.assessment_id = a.id
                GROUP BY a.id, a.title, a.held_on, a.max_score
                ORDER BY a.held_on DESC
                """
            )
            return cur.fetchall()


def record_assessment_with_scores(
    title: str,
    max_score: int,
    held_on: str,
    scores: list[tuple[int, int]],
) -> int:
    """Insert an assessment and all its scores in a single transaction.

    scores is a list of (mentee_id, score) pairs.
    Returns the new assessment id.

    If any insert fails the entire operation is rolled back automatically,
    so we never end up with a partial record in the database.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Insert the assessment first to get its id.
            cur.execute(
                """
                INSERT INTO assessments (title, max_score, held_on)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (title, max_score, held_on),
            )
            assessment_id = cur.fetchone()[0]

            # Insert every mentee's score in the same transaction.
            for mentee_id, score in scores:
                cur.execute(
                    """
                    INSERT INTO assessment_scores (mentee_id, assessment_id, score)
                    VALUES (%s, %s, %s)
                    """,
                    (mentee_id, assessment_id, score),
                )
        # conn.__exit__ commits all inserts at once, or rolls back if anything raised.
    return assessment_id
