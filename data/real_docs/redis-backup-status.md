Reports the current backup state.

## Examples

[code example]

## Details

 BACKUP STATUS reports the current state of the backup state machine along with timing and error information. The reply contains the following fields:

| Field | Description |
|:------|:------------|
| state | The current backup state (see below). |
| error | The error message if the backup failed; an empty string otherwise. |
| start_time | The Unix time, in seconds, when the current backup started; 0 if no backup has started. |
| end_time | The Unix time, in seconds, when the current backup was sealed; 0 if it has not been sealed. |

The state field is one of the following:

| State | Description |
|:------|:------------|
| idle | No backup is in progress. |
| pending | A backup was requested but is waiting for an append-only file rewrite (AOFRW) to become available. |
| snapshotting | Redis is producing the BASE snapshot. |
| incrementing | The BASE snapshot is complete and pinned; Redis is accumulating incremental writes and waiting to be sealed. |
| sealed | The backup is frozen; the file set is complete and immutable, awaiting data-plane consumption and cleanup. |
| failed | The backup failed or was aborted. A new backup can be started. |

For lightweight monitoring, INFO persistence also exposes a backup_in_progress boolean. Full backup state, error, and timestamps are available only through BACKUP STATUS .

For the full workflow, see Redis persistence.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

Array reply: a flat array of field-value pairs describing the current backup state.

-tab-sep-

Map reply: a map of fields to values describing the current backup state.

## See also

 BACKUP START | BACKUP SEAL | BACKUP LIST | BACKUP ABORT | BACKUP CLEANUP 

## Related topics

- Redis persistence