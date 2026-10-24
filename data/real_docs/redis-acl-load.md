When Redis is configured to use an ACL file (with the aclfile configuration
option), this command will reload the ACLs from the file, replacing all
the current ACL rules with the ones defined in the file. The command makes
sure to have an *all or nothing* behavior, that is:

* If every line in the file is valid, all the ACLs are loaded.
* If one or more line in the file is not valid, nothing is loaded, and the old ACL rules defined in the server memory continue to be used.

Starting with Redis 8.8, your ACL file is allowed to have comment lines; lines that begin with the # character.
Any such comment lines are stripped when the ACL file is loaded and they are not persisted across ACL LOAD / ACL SAVE commands.
Make sure you save a backup of your ACL file. This is the only way to preserve comments.

## Examples

[code example]

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

Simple string reply: OK on success.
The command may fail with an error for several reasons: if the file is not readable, if there is an error inside the file, and in such cases, the error will be reported to the user in the error.
Finally, the command will fail if the server is not configured to use an external ACL file.

-tab-sep-

Simple string reply: OK on success.
The command may fail with an error for several reasons: if the file is not readable, if there is an error inside the file, and in such cases, the error will be reported to the user in the error.
Finally, the command will fail if the server is not configured to use an external ACL file.