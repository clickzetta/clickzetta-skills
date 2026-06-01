# Job Management

Job management commands are used to view, describe, and cancel running or completed SQL jobs in Lakehouse.

---

## In This Chapter

| Page | Description |
|------|-------------|
| [SHOW JOBS](show-jobs.md) | List jobs; supports filtering by status, time, cluster, and other conditions |
| [DESC JOB](desc-job.md) | View detailed information for a single job, including the execution plan and error messages |
| [CANCEL JOB](cancel-job.md) | Cancel a job that is currently running |

---

## Common Operations

### View Jobs

```SQL
-- View all jobs (most recent records)
SHOW JOBS;

-- View running jobs
SHOW JOBS WHERE status = 'RUNNING';

-- View failed jobs
SHOW JOBS WHERE status = 'FAILED' LIMIT 20;

-- View jobs on a specific cluster
SHOW JOBS WHERE virtual_cluster = 'my_cluster' LIMIT 50;
```

### View Job Details

```SQL
-- View detailed information for a specific job (including error messages)
DESC JOB 'job_id_here';
```

### Cancel a Job

```SQL
-- Cancel a running job
CANCEL JOB 'job_id_here';
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [SQL Commands Overview](sql-commands.md) | Categorized navigation for all SQL commands |
| [INFORMATION_SCHEMA](information_schema_guide.md) | Analyze historical job data via the job_history view |
| [Compute Cluster (VCluster)](compute-resource-ddl.md) | Manage the compute clusters that execute jobs |
