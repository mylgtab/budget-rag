Adds one or more items to a cuckoo filter if they did not exist previously, allowing the filter to be created with a custom capacity if it does not exist yet.

This command is similar to CF.ADDNX , except that more than one item can be added and capacity can be specified.

Notes:

- This command is slower than CF.INSERT because it first checks whether each item exists.
- Since CF.EXISTS can result in false positive, CF.INSERTNX may not add an item because it is supposedly already exist, which may be wrong.
 

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

redis> CF.INSERTNX cf CAPACITY 1000 ITEMS item1 item2 
1) (integer) 1
2) (integer) 1

redis> CF.INSERTNX cf CAPACITY 1000 ITEMS item1 item2 item3
1) (integer) 0
2) (integer) 0
3) (integer) 1

redis> CF.INSERTNX cf_new CAPACITY 1000 NOCREATE ITEMS item1 item2 
(error) ERR not found

## Details

### Complexity

O(n + i), where n is the number of sub-filters and i is maxIterations .
Adding items requires up to 2 memory accesses per sub-filter .
But as the filter fills up, both locations for an item might be full. The filter attempts to Cuckoo swap items up to maxIterations times.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Supported | &#x2705; Flexible & Annual&#x2705; Free & Fixed | |

## Return information

One of the following:

* Array reply, where each element is an integer reply: 0 when the item's fingerprint already exists in the filter, 1 when the item is added successfully, or -1 when the item cannot be added because the filter is full.
* Simple error reply when the number of arguments or key type is incorrect, and also when NOCREATE is specified and key does not exist.

-tab-sep-

* Array reply, where each element is an integer reply: 0 means that the item's fingerprint already exists in the filter, 1 for successfully adding an item, or -1 when the item cannot be added because the filter is full.
* Simple error reply when the number of arguments or key type is incorrect, and also when NOCREATE is specified and key does not exist.