# Task Instance Configuration and Its Effect on Instance Execution

The task instance information configuration provides three mechanisms for controlling how instances are handled at different lifecycle stages. The three settings are independent of each other and apply to the **waiting stage**, **the moment an instance enters the running state**, and the **running stage** respectively.

***

## Run Timeout Duration

**Applies to**: Instances in the Running state

If the actual run time of a task instance exceeds the configured value, the system will immediately set that instance to **Failed** status, preventing abnormal tasks from hanging indefinitely and continuously consuming compute resources.

***

## Schedule Wait Duration

**Applies to**: Instances that have reached their scheduled trigger time and are waiting for upstream tasks to complete

Starting from the scheduled trigger time, if an instance remains in the waiting state (neither entering the running state nor finishing) for longer than the configured duration, the system will immediately set that instance to **Failed**, preventing scheduling backlogs caused by upstream tasks taking too long.

> **Example**: A task is scheduled to trigger daily at 01:00, with a schedule wait duration of 2 hours. If the instance is still waiting for upstream at 03:00, the system sets it to Failed.

***

## Delayed Run Skip Duration

**Applies to**: The moment an instance transitions from the waiting state to the running state

The system calculates the difference between the **actual time the instance enters the running state** and the **originally scheduled trigger time**. If the difference exceeds the configured duration, the system performs a **dry-run skip** on that instance and sets its status to **Succeeded**, avoiding meaningless repeated computation on severely delayed instances.

> **Example**: A task is scheduled every 5 minutes, with a skip duration of 6 minutes. The instance scheduled to trigger at 14:05 does not enter the running state until 14:12 due to upstream delays (a delay of 7 minutes > 6 minutes). The system performs a dry-run skip and sets it to Succeeded.

***

## Comprehensive Example: Self-Dependent Periodic Task

**Configuration background**: A self-dependent task scheduled every 5 minutes, with all three timeout settings at **10 minutes**. The first instance (T1) starts running at 14:00 and actually takes 20 minutes to complete.

### Scenario 1: Run Timeout Duration

|                                        |                                                                                  |
| -------------------------------------- | -------------------------------------------------------------------------------- |
| Time                                   | Event                                                                            |
| 14:00                                  | T1 starts running                                                                |
| 14:10                                  | Run time reaches the 10-minute limit; T1 is set to Failed                        |
| Subsequent instances from 14:05 onward | All self-dependent subsequent instances are suspended because upstream T1 failed |

^

### Scenario 2: Schedule Wait Duration

|       |                                                                                                                |
| ----- | -------------------------------------------------------------------------------------------------------------- |
| Time  | Event                                                                                                          |
| 14:00 | T1 starts running normally (not affected by this setting)                                                      |
| 14:05 | T2 reaches its trigger time and enters the waiting-for-upstream (T1) state                                     |
| 14:15 | T2's wait time reaches the 10-minute limit; T2 is set to Failed. T1 can continue running normally              |
| 14:10 | T3 reaches its trigger time and enters the waiting state; its downstream tasks are suspended because T2 failed |
| 14:20 | T3's wait time reaches the 10-minute limit; T3 is set to Failed. T1 completes normally                         |

> The schedule wait duration triggers independently for each instance; T1's normal execution is not affected.
>

### Scenario 3: Delayed Run Skip Duration

|       |                                                                                            |
| ----- | ------------------------------------------------------------------------------------------ |
| Time  | Event                                                                                      |
| 14:00 | T1 starts running normally                                                                 |
| 14:05 | T2 reaches its trigger time and waits for T1 to complete                                   |
| 14:20 | T1 completes; T2 enters the running state. Delay = 14:20 − 14:05 = 15 minutes > 10 minutes |
| 14:20 | T2 is dry-run skipped and set to Succeeded, triggering T3's scheduling                     |

> A dry-run skip does not execute any actual business logic; it only marks the instance as Succeeded to keep the scheduling chain moving.

***

^

***

^
