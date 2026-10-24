Adds one or more items to a Bloom filter.

This command is similar to BF.ADD , except that you can add more than one item.

This command is similar to BF.INSERT , except that the error rate, capacity, and expansion cannot be specified.

## Required arguments

key

is key name for a Bloom filter to add the items to.

If key does not exist - a new Bloom filter is created with default error rate, capacity, and expansion (see BF.RESERVE ).

item...

One or more items to add.

## Examples

redis> BF.MADD bf item1 item2 item2
1) (integer) 1
2) (integer) 1
3) (integer) 0

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Supported | &#x2705; Flexible & Annual&#x2705; Free & Fixed | |

## Return information

One of the following:
* Array reply where each element is either
 * an integer reply, where 1 means that the item has been added successfully, and 0 means there's a probability that the item was already added to the filter.
 * a simple error reply when the item cannot be added because the filter is full.
* Simple error reply in these cases: invalid arguments, key not found, wrong key type, or when the filter is full.

-tab-sep-

One of the following:
* Array reply where each element is either
 * a boolean reply, where true means that the item has been added successfully, and false means there's a probability that the item was already added to the filter.
 * a simple error reply when the item cannot be added because the filter is full.
* Simple error reply in these cases: invalid arguments, key not found, wrong key type, or when the filter is full.