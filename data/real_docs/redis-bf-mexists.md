Determines whether one or more items were added to a Bloom filter.

This command is similar to BF.EXISTS , except that more than one item can be checked.

## Required arguments

key

is key name for a Bloom filter.

item...

One or more items to check.

## Examples

redis> BF.MADD bf item1 item2
1) (integer) 1
2) (integer) 1
redis> BF.MEXISTS bf item1 item2 item3
1) (integer) 1
2) (integer) 1
3) (integer) 0

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Supported | &#x2705; Flexible & Annual&#x2705; Free & Fixed | |

## Return information

One of the following:
* An array of integers, where each element corresponds to an item in the request. A value of 1 means the item was probably already added to the filter. A value of 0 means the item was definitely not added, key does not exist, or key contains a value of the wrong type.
* Simple error reply if invalid arguments are passed.

-tab-sep-

One of the following:
* An array of booleans, where each element corresponds to an item in the request. A value of true means the item was probably already added to the filter. A value of false means the item was definitely not added, key does not exist, or key contains a value of the wrong type.
* Simple error reply if invalid arguments are passed.