# TaskForge load baseline

The Locust scenario uses authenticated users and seeded workspace/project IDs.
Create the default 20-workspace, 400-project, and 40,000-task dataset with:

```powershell
python -m scripts.seed_load_data
```

The seeder is deterministic and repeatable. It creates missing rows and resets
the password for the `load-user-*` accounts only. It also writes
`.dist/load-test.env.ps1`.

Load those generated values into the current PowerShell session:

```powershell
. .\.dist\load-test.env.ps1
```

You can verify the variables before starting Locust:

```powershell
$env:TASKFORGE_LOAD_USERS = "user1@example.com:password,user2@example.com:password"
$env:TASKFORGE_LOAD_WORKSPACE_ID = "<workspace-uuid>"
$env:TASKFORGE_LOAD_PROJECT_ID = "<project-uuid>"
```

Run a local baseline with the API already serving traffic:

```powershell
locust -f load_tests/locustfile.py --headless `
  --host http://127.0.0.1:8000 `
  --users 50 `
  --spawn-rate 0.5 `
  --run-time 12m `
  --csv results/taskforge-baseline
```

The workload weights are 70% task-list reads, 20% task creation, and 10% export
creation plus one status read. Record the actual warmup, measurement window,
dataset, software versions, pool settings, cache state, CPU, memory, queue age,
and export duration with every result. Run once after clearing Redis and once
with the same dataset after the cache is warm.
