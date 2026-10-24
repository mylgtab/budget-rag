The command shows a list of recent ACL security events:

1. Failed authentications with AUTH or HELLO (reason = auth)
2. Commands violating the current ACL rules
 - Disallowed commands (reason = command).
 - Disallowed keys (reason = key).
 - Disallowed pub/sub channel (reason = channel).

The optional argument specifies how many entries to show. By default
up to ten failures are returned. The special RESET argument clears the log.
Entries are displayed starting from the most recent.

## Optional arguments

count | RESET

The number of recent entries to return, or RESET to clear the log.

## Examples

[code example]

## Details

Each log entry is composed of the following fields:

1. count : The number of security events detected within a 60 second period that are represented by this entry.
2. reason : The reason that the security events were logged. Either command , key , channel , or auth .
3. context : The context that the security events were detected in. Either toplevel , multi , lua , or module .
4. object : The resource that the user had insufficient permissions to access. auth when the reason is auth .
5. username : The username that executed the command that caused the security events or the username that had a failed authentication attempt.
6. age-seconds : Age of the log entry in seconds.
7. client-info : Displays the client info of a client which caused one of the security events.
8. entry-id : The sequence number of the entry (starting at 0) since the server process started. Can also be used to check if items were "lost", if they fell between periods.
9. timestamp-created : A UNIX timestamp in milliseconds at the time the entry was first created.
10. timestamp-last-updated : A UNIX timestamp in milliseconds at the time the entry was last updated.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

When called to show security events:
* Array reply: an array of Bulk string reply elements representing ACL security events.
When called with RESET :
* Simple string reply: OK if the security log was cleared.

-tab-sep-

When called to show security events:
* Array reply: an array of Bulk string reply elements representing ACL security events.
When called with RESET :
* Simple string reply: OK if the security log was cleared.