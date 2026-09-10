INSERT INTO users (id, email, password_hash)
VALUES
    ('00000000-0000-4000-8000-000000000101', 'owner@example.com', 'synthetic-hash-owner'),
    ('00000000-0000-4000-8000-000000000102', 'member@example.com', 'synthetic-hash-member')
ON CONFLICT (email) DO NOTHING;

INSERT INTO workspaces (id, name)
VALUES
    ('00000000-0000-4000-8000-000000000201', 'Launch workspace'),
    ('00000000-0000-4000-8000-000000000202', 'Empty workspace')
ON CONFLICT (id) DO NOTHING;

INSERT INTO memberships (id, user_id, workspace_id, role)
VALUES
    (
        '00000000-0000-4000-8000-000000000301',
        '00000000-0000-4000-8000-000000000101',
        '00000000-0000-4000-8000-000000000201',
        'owner'
    ),
    (
        '00000000-0000-4000-8000-000000000302',
        '00000000-0000-4000-8000-000000000102',
        '00000000-0000-4000-8000-000000000201',
        'member'
    )
ON CONFLICT (user_id, workspace_id) DO NOTHING;

INSERT INTO projects (id, workspace_id, name)
VALUES
    (
        '00000000-0000-4000-8000-000000000401',
        '00000000-0000-4000-8000-000000000201',
        'Launch plan'
    ),
    (
        '00000000-0000-4000-8000-000000000402',
        '00000000-0000-4000-8000-000000000201',
        'Zero task project'
    )
ON CONFLICT (id) DO NOTHING;

INSERT INTO tasks (id, project_id, title, status)
VALUES
    (
        '00000000-0000-4000-8000-000000000501',
        '00000000-0000-4000-8000-000000000401',
        'Draft checklist',
        'todo'
    ),
    (
        '00000000-0000-4000-8000-000000000502',
        '00000000-0000-4000-8000-000000000401',
        'Review launch notes',
        'in_progress'
    )
ON CONFLICT (id) DO NOTHING;
