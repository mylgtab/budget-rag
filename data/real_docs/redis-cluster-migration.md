The CLUSTER MIGRATION command provides atomic slot migration functionality for Redis Cluster. This command allows you to import slots from other nodes, monitor the progress of migration tasks, and cancel ongoing migrations.

## Required arguments

subcommand

The subcommand specifies the operation to perform:

- IMPORT start-slot end-slot [start-slot end-slot ...] : Executes on the destination master. Accepts multiple slot ranges and triggers atomic migration for the specified ranges. Returns a task ID that you can use to monitor the status of the task.

- CANCEL ID task-id | ALL : Cancels an ongoing migration task by its ID or cancels all tasks if ALL is specified. Note: Cancelling a task on the source node does not stop the migration on the destination node, which will continue retrying until it is also cancelled there.

- STATUS [ID task-id | ALL] : Displays the status of current and completed atomic slot migration tasks. If a specific task ID is provided, it returns detailed information for that task only. If ALL is specified, it returns the status of all ongoing and completed tasks.

## Examples

Import slots 0-1000 and 2000-3000 to the current node:

[code example]

Check the status of all migration tasks:

[code example]

Check the status of a specific migration task:

[code example]

Cancel a specific migration task:

[code example]

Cancel all migration tasks:

[code example]

## Details

- Cancelling a task on the source node does not automatically stop the migration on the destination node.
- In CLUSTER MIGRATION STATUS output, the "state" field will show completed for successful operations.
- Tasks with empty "last_error" fields indicate no errors occurred during the migration process.

### Key visibility during migration

During atomic slot migration operations, keys in unowned slots may be filtered out from the following commands while importing or trimming is in progress:

- KEYS 
- SCAN 
- RANDOMKEY 
- CLUSTER GETKEYSINSLOT 
- DBSIZE 
- CLUSTER COUNTKEYSINSLOT 

The INFO KEYSPACE command will continue to reflect the actual number of keys, including those being imported.

### Related configuration

- cluster-slot-migration-handoff-max-lag-bytes : After slot snapshot completion, if remaining replication stream size falls below this threshold, the source node pauses writes to hand off slot ownership. Higher values trigger handoff earlier but may cause longer write pauses. Lower values result in shorter write pauses but may be harder to reach with steady incoming writes (default: 1MB).
- cluster-slot-migration-write-pause-timeout : Maximum duration that the source node pauses writes during ASM handoff. If the destination fails to take over slots within this timeout, the source assumes migration failed and resumes writes (default: 10 seconds).

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

For the IMPORT subcommand:
Bulk string reply: task ID on success, or error message on failure.

For the CANCEL subcommand:
Integer reply: number of cancelled tasks.

For the STATUS subcommand:
Array reply: a list of migration task details. Each task is represented as an array containing field-value pairs:
- id : Task identifier
- slots : Slot range being imported or migrated
- source : Source node ID
- dest : Destination node ID
- operation : Operation type ("import" or "migrate")
- state : Current state ("completed", "in_progress", etc.)
- last_error : Last error message (empty if none)
- retries : Number of retry attempts
- create_time : Task creation timestamp
- start_time : Task start timestamp
- end_time : Task completion timestamp (if completed)
- write_pause_ms : Write pause duration in milliseconds

-tab-sep-

For the IMPORT subcommand:
Bulk string reply: task ID on success, or error message on failure.

For the CANCEL subcommand:
Integer reply: number of cancelled tasks.

For the STATUS subcommand:
Array reply: a list of migration task details. Each task is represented as an array containing field-value pairs:
- id : Task identifier
- slots : Slot range being migrated
- source : Source node ID
- dest : Destination node ID
- operation : Operation type (typically "migrate")
- state : Current state ("completed", "in_progress", etc.)
- last_error : Last error message (empty if none)
- retries : Number of retry attempts
- create_time : Task creation timestamp
- start_time : Task start timestamp
- end_time : Task completion timestamp (if completed)
- write_pause_ms : Write pause duration in milliseconds