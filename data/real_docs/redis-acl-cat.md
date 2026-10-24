The command shows the available ACL categories if called without arguments.
If a category name is given, the command shows all the Redis commands in
the specified category.

ACL categories are very useful in order to create ACL rules that include or
exclude a large set of commands at once, without specifying every single
command. For instance, the following rule will let the user karin perform
everything but the most dangerous operations that may affect the server
stability:

 ACL SETUSER karin on +@all -@dangerous

We first add all the commands to the set of commands that karin is able
to execute, but then we remove all the dangerous commands.

Checking for all the available categories is as simple as:

[code example]

Then we may want to know what commands are part of a given category:

[code example]

## Optional arguments

category

List only the commands in the given ACL category. If omitted, all categories are listed.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | Not supported for scripts. |

## Return information

One of the following:
* Array reply: an array of Bulk string reply elements representing ACL categories or commands in a given category.
* Simple error reply: the command returns an error if an invalid category name is given.

-tab-sep-

One of the following:
* Array reply: an array of Bulk string reply elements representing ACL categories or commands in a given category.
* Simple error reply: the command returns an error if an invalid category name is given.