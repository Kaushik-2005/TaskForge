\set ON_ERROR_STOP on
BEGIN;
\i db/schema.sql
\i db/seed.sql

DO $$
DECLARE
    visible_task_count integer;
    zero_task_project_count integer;
BEGIN
    SELECT count(*)
    INTO visible_task_count
    FROM memberships AS m
    JOIN projects AS p
        ON p.workspace_id = m.workspace_id
    JOIN tasks AS t
        ON t.project_id = p.id
    WHERE m.user_id = '00000000-0000-4000-8000-000000000101'
      AND m.workspace_id = '00000000-0000-4000-8000-000000000201'
      AND p.workspace_id = '00000000-0000-4000-8000-000000000201';

    IF visible_task_count <> 2 THEN
        RAISE EXCEPTION 'expected 2 visible tasks, got %', visible_task_count;
    END IF;

    SELECT count(*)
    INTO zero_task_project_count
    FROM (
        SELECT
            p.id AS project_id,
            p.name AS project_name,
            count(t.id) AS task_count
        FROM projects AS p
        LEFT JOIN tasks AS t
            ON t.project_id = p.id
        WHERE p.workspace_id = '00000000-0000-4000-8000-000000000201'
        GROUP BY p.id, p.name
    ) AS project_counts
    WHERE project_name = 'Zero task project'
      AND task_count = 0;

    IF zero_task_project_count <> 1 THEN
        RAISE EXCEPTION 'expected zero-task project to be present once, got %', zero_task_project_count;
    END IF;
END $$;

ROLLBACK;
