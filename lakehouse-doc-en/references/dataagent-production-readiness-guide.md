# Data Engineering Agent Production Readiness Guide

This guide is for teams preparing to use the Data Engineering Agent in production environments. It answers one core question: beyond knowing how to use the Agent, what else needs to be in place to use it reliably.

## Get Directory Governance in Place First

Before using the Agent in production, task directories must be clearly defined. At a minimum, distinguish between test tasks, temporary development, official production tasks, and different business domains or projects. Do not pile all tasks into a single directory — otherwise finding tasks, publishing, cleaning up, and managing permissions all become much harder over time.

## Draft First, Then Run, Then Publish

This should be the default rhythm, not the exception. The recommended order is: create draft → review code or canvas → save schedule configuration → publish. Do not treat "draft created successfully" as "ready to go live."

## Always Verify the DAG for Composite Tasks

For composite tasks, Flows, and multi-node orchestrations, having the object in the task tree is not enough. You must open the canvas and confirm the nodes and dependency edges. This is a critical step before production — do not rely solely on the Agent's verbal confirmation.

## Start DQC with Basic Rules and Weak Rules

During the production readiness phase, it is not recommended to add a large number of strong rules right away. A more reliable order is to start with basic rules such as row count, non-null, and deduplication, use weak rules with manual triggers first, and upgrade once rules are validated.

## Accept That Empty Monitoring Is Also a Valid Result

Production readiness does not mean all workspaces will immediately have rich monitoring data. In new workspaces, empty monitoring typically means tasks have not yet been executed, tasks have not yet been published, or the workspace is still in the preparation phase. The monitoring investigation workflow must treat empty state as a normal branch, not an error.

## High-Impact Operations Must Retain Explicit Confirmation

Actions such as publishing, cancelling publishing, re-running, backfilling, deleting, and modifying dependencies should not be treated as ordinary routine operations. In production, they should retain an explicit confirmation step.

## Test Objects Must Be Cleanable

Production readiness will always produce test tasks, test rules, and test composite tasks. Teams should establish consistent habits around naming conventions, placing objects in test directories, and cleaning up promptly after validation. Otherwise the environment becomes hard to govern over time.

## A Minimal Production Readiness Checklist

A team should confirm at least the following:

* Task directory structure has been planned
* The boundaries between draft, run, and publish have been explained clearly
* Composite task DAG review process has been defined
* The first set of DQC rules has been determined
* The approach for explaining empty monitoring state has been agreed upon
* Confirmation workflows for deletion, backfill, and re-run have been defined
* Test object cleanup mechanism has been established

## Related Guides

* [Data Engineering Agent](dataagent.md)
* [Safe Operation Guide](dataagent-safe-operation-guide.md)
* [Task Development Guide](dataagent-task-development-guide.md)
* [Task Group and Composite Task Guide](dataagent-task-group-guide.md)
* [DQC Data Quality Rules Guide](dataagent-dqc-guide.md)
* [DQC Best Practices](dataagent-dqc-best-practices.md)
* [Run Monitoring Guide](dataagent-monitoring-guide.md)
* [Pipeline Launch Checklist](dataagent-pipeline-launch-checklist.md)
