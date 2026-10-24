Freezes the current backup, producing the final immutable file set: the BASE snapshot, the incremental append-only file (INCR), and a standalone manifest.

## Examples

[code example]

## Details

 BACKUP SEAL moves the backup state machine from incrementing to sealed . Restore loads BASE + INCR , so the restored dataset reflects the state at the seal boundary, not merely the earlier BASE snapshot. Sealing performs the following steps:

* Flushes and fsyncs the current INCR file.
* Hard-links the INCR file into the backup directory.
* Writes a standalone manifest that references only this backup's {BASE, INCR} file set.
* Rotates the live AOF when AOF persistence is enabled.
* Stops and removes the temporary AOF state when the backup created it for an appendonly no instance.

After sealing, the file set is complete and immutable. The data plane can copy the files reported by BACKUP LIST , then call BACKUP CLEANUP to release them.

For the full workflow and restore procedure, see Redis persistence.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

Simple string reply: OK .

-tab-sep-

Simple string reply: OK .

## See also

 BACKUP START | BACKUP STATUS | BACKUP LIST | BACKUP ABORT | BACKUP CLEANUP 

## Related topics

- Redis persistence