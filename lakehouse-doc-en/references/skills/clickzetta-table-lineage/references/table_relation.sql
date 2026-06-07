-- Build table production lineage graph based on job execution over the past {N} days
with raw as (
    select split(input_objects, ',') as input, split(output_objects, ',') as output
    from information_schema.job_history
    where start_time>=now() - interval {N} day
        and output_objects is not null
        and job_type != 'COMPACTION_JOB' -- exclude compaction jobs as they add noise to lineage
),
normalized as (
    select public.__normalize_objects(input) as input,
        public.__normalize_objects(output) as output
    from raw
),
exploded (
    select table_name, explode(input) as upstream 
    from (
        select explode(output) as table_name, input
        from normalized
    )
)
select table_name, upstream
from exploded
where table_name is not null and  table_name != '' and upstream is not null and upstream != ''
group by table_name, upstream
;