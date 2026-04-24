-- Optional seed data for local testing.
-- Run manually: docker exec -i giga_mentees_db psql -U giga -d giga_mentees < sql/seed.sql

INSERT INTO mentees (full_name, email, cohort) VALUES
    ('Blend Sejdiu',     'blend@example.com',    'B5'),
    ('Dren Xhyliqi',     'dren@example.com',     'B5'),
    ('Alketa Shala',     'alketa@example.com',   'B5'),
    ('Lis Spahija',      'lis@example.com',      'B5'),
    ('Vigan Pireva',     'vigan@example.com',    'B5'),
    ('Alma Sadrija',     'alma@example.com',     'B5'),
    ('Ereza Greicevci',  'ereza@example.com',    'B5'),
    ('Fjolla Lushta',    'fjolla@example.com',   'B5'),
    ('Vese Emini',       'vese@example.com',     'B5')
ON CONFLICT (email) DO NOTHING;
