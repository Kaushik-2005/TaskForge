\set ON_ERROR_STOP on
BEGIN;
\i db/schema.sql
\i db/seed.sql

DO $$
BEGIN
    BEGIN
        INSERT INTO projects (workspace_id, name)
        VALUES ('00000000-0000-4000-8000-000000009999', 'Broken project');
        RAISE EXCEPTION 'expected foreign key violation for project workspace_id';
    EXCEPTION WHEN foreign_key_violation THEN
        NULL;
    END;

    BEGIN
        INSERT INTO memberships (user_id, workspace_id, role)
        VALUES (
            '00000000-0000-4000-8000-000000000101',
            '00000000-0000-4000-8000-000000000201',
            'owner'
        );
        RAISE EXCEPTION 'expected duplicate membership violation';
    EXCEPTION WHEN unique_violation THEN
        NULL;
    END;

    BEGIN
        INSERT INTO tasks (project_id, title, status)
        VALUES (
            '00000000-0000-4000-8000-000000000401',
            'Invalid status task',
            'blocked'
        );
        RAISE EXCEPTION 'expected task status check violation';
    EXCEPTION WHEN check_violation THEN
        NULL;
    END;
END $$;

ROLLBACK;
