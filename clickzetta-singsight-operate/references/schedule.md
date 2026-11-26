# Schedule (`--schedule`)

`trigger-eval --schedule`, `schedule-preview` and `update-schedule` take the job's `schedule_info` as JSON. Times are UTC ISO 8601; `timezone` interprets `at_time`, the hours of an HOURLY schedule, and the day and hour boundaries of the data windows.

```json
{
  "frequency": { "type": "DAILY", "at_time": "02:00" },
  "timezone": "Asia/Shanghai",
  "start_at": null,
  "end_at": null
}
```

| Field | Values | Default |
|---|---|---|
| `frequency.type` | `HOURLY`, `DAILY`, `WEEKLY` | required |
| `frequency.every` | HOURLY only: 1, 2, 3, 4, 6, 8, 12. Fires on local hours divisible by it | 1 |
| `frequency.at_minute` | HOURLY only: 0-59. Must be at least the project's dynamic-table refresh interval | 10 |
| `frequency.at_time` | DAILY / WEEKLY: `HH:mm` in `timezone`. Its distance from 00:00 must be at least the refresh interval | required |
| `frequency.days_of_week` | WEEKLY only: 1 (Monday) to 7 (Sunday) | required |
| `timezone` | IANA name, for example `Asia/Shanghai` | `UTC` |
| `start_at` / `end_at` | When the schedule is in effect. After `end_at` the schedule is `ENDED` | now / no end |

## Data window

There is no window setting: each fire evaluates the previous full period in `timezone`. For a fire planned at `T`:

```
window_end   = start of T's hour (HOURLY) or T's day (DAILY / WEEKLY)
window_start = the same boundary of the previous planned fire
```

| Schedule | Fire | Evaluates |
|---|---|---|
| Daily 02:00 | 2026-11-25 02:00 | 2026-11-24 00:00 ~ 2026-11-25 00:00 |
| Every 2 hours at :10 | 14:10 | 12:00 ~ 14:00 |
| Weekly Mon and Thu 09:30 | Monday 09:30 | Thursday 00:00 ~ Monday 00:00 |

The time between the window end and the fire (two hours for a 02:00 fire, ten minutes for :10) is what lets the window's data land, so it must be at least the project's dynamic-table refresh interval; there is no separate delay setting. The window depends only on the planned time, so a delayed run, or a rerun with `--source-run-id`, evaluates the same data. Windows are back to back. A unit belongs to the window it ends in: a SPAN by its own end time, a TRACE by the latest end time of its spans. So a trace is evaluated only after it has finished, all its spans are read, and no trace is evaluated twice. A trace that still has spans starting after the window end is left to a later window.

`rerun` without `--source-run-id` on a scheduled job evaluates the latest window that has already ended (for the daily 02:00 job at 15:20 on 11-24: 11-23 00:00 ~ 11-24 00:00).

## Overlapping and missed fires

A fire while the job's previous run is still going is recorded as a `SKIPPED` run.

Fires missed while no SingSight instance was up, or while the schedule was paused, are caught up one after another when it runs again: the latest one plus at most 24 earlier ones. Older ones are recorded as one `SKIPPED` run whose message names the skipped range. This is not configurable.

## Checking a schedule

`ss schedule-preview --schedule S` validates it (the same checks as creation) and returns:

- `fires`: the next fires, each with `fireAt`, `windowStart`, `windowEnd`.
- `recentFire`: the latest window that has already ended. Pass its `windowStart` / `windowEnd` as `time_start` / `time_end` to `ss preview` to see what one run would evaluate.
