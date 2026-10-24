Starts a new backup, opening a backup window and producing a fresh BASE snapshot in the directory named by the backupdirname configuration setting.

## Examples

[code example]

## Details

 BACKUP START moves the backup state machine from idle to snapshotting and begins producing a fresh BASE snapshot through an append-only file rewrite (AOFRW). It works whether or not AOF persistence is enabled:

* If AOF is enabled, Redis reuses the existing multi-part AOF directly.
* If AOF is disabled, Redis temporarily starts the AOF machinery without changing the configured appendonly value.
* If an AOFRW is already active or scheduled and can be reused, the backup attaches to it.
* If another child process is active, the backup enters the pending state and starts when an AOFRW can run.

After the snapshot rewrite completes, Redis hard-links the BASE file into the backup directory and enters the incrementing state, where it continues to accumulate incremental writes until you call BACKUP SEAL .

The backup directory (named by backupdirname and resolved under the Redis working directory dir ) must be empty when you call BACKUP START . Only one backup can be in progress at a time.

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

 BACKUP SEAL | BACKUP STATUS | BACKUP LIST | BACKUP ABORT | BACKUP CLEANUP 

## Related topics

- Redis persistence