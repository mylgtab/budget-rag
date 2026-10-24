Adds an item to the cuckoo filter.

Cuckoo filters can contain the same item multiple times, and consider each addition as separate.
Use CF.ADDNX to add an item only if it does not exist.

## Required arguments

key

is key name for a cuckoo filter to add the item to.

If key does not exist - a new cuckoo filter is created.

item

is an item to add.

## Complexity

O(n + i), where n is the number of sub-filters and i is maxIterations .
Adding items requires up to 2 memory accesses per sub-filter .
But as the filter fills up, both locations for an item might be full.
The filter attempts to Cuckoo swap items up to maxIterations times.

## Examples

redis> CF.ADD cf item1
(integer) 1
redis> CF.ADD cf item1
(integer) 1

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Supported | &#x2705; Flexible & Annual&#x2705; Free & Fixed | |

## Return information

One of the following:
* Integer reply: 1 for successfully adding an item to the filter.
* Simple error reply in these cases: invalid arguments, wrong key type, or when the filter is full.

-tab-sep-

One of the following:
* Boolean reply: true for successfully adding an item to the filter.
* Simple error reply in these cases: invalid arguments, wrong key type, or when the filter is full.