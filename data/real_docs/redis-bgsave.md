Save the DB in background.

Normally the OK code is immediately returned.
Redis forks, the parent continues to serve the clients, the child saves the DB
on disk then exits.

An error is returned if there is already a background save running or if there
is another non-background-save process running, specifically an in-progress AOF
rewrite.

If BGSAVE SCHEDULE is used, the command will immediately return OK when an
AOF rewrite is in progress and schedule the background save to run at the next
opportunity.

A client may be able to check if the operation succeeded using the LASTSAVE 
command.

See the persistence documentation for detailed information.

## Optional arguments

SCHEDULE

Schedule the save to run after any in-progress BGSAVE finishes, instead of returning an error.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

One of the following:
* Simple string reply: Background saving started .
* Simple string reply: Background saving scheduled .

-tab-sep-

One of the following:
* Simple string reply: Background saving started .
* Simple string reply: Background saving scheduled .