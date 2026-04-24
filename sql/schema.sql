-- GigaAcademy Mentees Tracker — schema
-- This file is auto-loaded by the Postgres container on first boot.
-- For Level 1 you only need the `mentees` table.
-- For Level 2, uncomment the `assessments` and `assessment_scores` tables.

CREATE TABLE IF NOT EXISTS mentees (
    id          SERIAL PRIMARY KEY,
    full_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    cohort      VARCHAR(20)  NOT NULL,
    enrolled_on DATE         DEFAULT CURRENT_DATE
);

-- ================================
-- Uncomment below for Level 2
-- ================================

-- CREATE TABLE IF NOT EXISTS assessments (
--     id        SERIAL PRIMARY KEY,
--     title     VARCHAR(120) NOT NULL,
--     max_score INT          NOT NULL CHECK (max_score > 0),
--     held_on   DATE         NOT NULL
-- );

-- CREATE TABLE IF NOT EXISTS assessment_scores (
--     mentee_id     INT NOT NULL REFERENCES mentees(id)     ON DELETE CASCADE,
--     assessment_id INT NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
--     score         INT NOT NULL CHECK (score >= 0),
--     PRIMARY KEY (mentee_id, assessment_id)
-- );
