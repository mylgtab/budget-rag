Adds one or more items to a cuckoo filter, allowing the filter to be created with a custom capacity if it does not exist yet.

This command is similar to CF.ADD , except that more than one item can be added and capacity can be specified.

## Required arguments

key

is key name for a cuckoo filter to add items to.

If key does not exist - a new cuckoo filter is created.

ITEMS item...

One or more items to add.

## Optional arguments

CAPACITY capacity
 
Specifies the desired capacity of the new filter, if this filter does not exist yet.
 
If the filter already exists, then this parameter is ignored.
 
If the filter does not exist yet and this parameter is *not* specified, then the filter is created with the module-level default capacity which is 1024.

See CF.RESERVE for more information on cuckoo filter capacities.

 
NOCREATE
 
If specified, prevents automatic filter creation if the filter does not exist (Instead, an error is returned).
 
This option is mutually exclusive with CAPACITY .

## Examples

redis> CF.INSERT cf CAPACITY 1000 ITEMS item1 item2 
1) (integer) 1
2) (integer) 1

redis> CF.INSERT cf1 CAPACITY 1000 NOCREATE ITEMS item1 item2 
(error) ERR not found

redis> CF.RESERVE cf2 2 BUCKETSIZE 1 EXPANSION 0
OK
redis> CF.INSERT cf2 ITEMS 1 1 1 1
1) (integer) 1
2) (integer) 1
3) (integer) -1
4) (integer) -1

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Supported | &#x2705; Flexible & Annual&#x2705; Free & Fixed | |

## Return information

One of the following:

* Array reply, where each element is an integer reply: 1 when the item is added successfully, or -1 when the item cannot be added because the filter is full.
* Simple error reply when the number of arguments or key type is incorrect, and also when NOCREATE is specified and key does not exist.

-tab-sep-

* Array reply, where each element is either a boolean reply of true for successfully adding an item, or an integer reply of -1 when the item cannot be added because the filter is full.
* Simple error reply when the number of arguments or key type is incorrect, and also when NOCREATE is specified and key does not exist.