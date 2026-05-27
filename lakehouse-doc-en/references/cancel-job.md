# Cancel Job

## Description

This function allows users to terminate running jobs or cancel all jobs under a specific virtual cluster. Through this function, users can effectively manage job progress and avoid resource waste.

## Syntax

```
-- Cancel a single job
CANCEL JOB 'jobid';

-- Cancel all jobs under a specific VIRTUAL CLUSTER
ALTER VCLUSTER [ IF EXISTS ] vc_name CANCEL ALL JOBS;
```

## Parameter Description

1. `jobid`: The unique identifier for the job run, in string format. When the job runs, the log will print out the jobid, and the corresponding jobid will also be displayed in the [show jobs](<show-jobs.md>) command.
2. `vc_name`: The name of the specified virtual cluster. If the virtual cluster does not exist, using the `IF EXISTS` option can avoid errors caused by not finding the cluster.

## Example

**Example 1: Cancel a single job**
Suppose you need to cancel a job with the jobid `201xxxxxxxxxx`. You can use the following command to achieve this:

```
CANCEL JOB '201xxxxxxxxxx';
```

**Example 2: Cancel All Jobs in a Specific Virtual Cluster**
Assuming you need to cancel all jobs in the virtual cluster named `my_vc`. First, use the following command to cancel all jobs in that virtual cluster:

```
ALTER VCLUSTER  my_vc CANCEL ALL JOBS;
```

If you are concerned about errors caused by the non-existence of a virtual cluster, you can use the `IF EXISTS` option:

```
ALTER VCLUSTER IF EXISTS my_vc CANCEL ALL JOBS;
```

## Precautions

* Ensure that you input the correct `jobid` or `vc_name` when executing the job termination operation to avoid affecting the normal operation of other jobs or virtual clusters.
* After terminating the job, the used resources will be released, but please note that the consumed time and costs may not be refunded.

^
