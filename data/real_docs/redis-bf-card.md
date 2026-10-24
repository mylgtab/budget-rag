Returns the cardinality of a Bloom filter - number of items that were added to a Bloom filter and detected as unique (items that caused at least one bit to be set in at least one sub-filter)

(since RedisBloom 2.4.4)

## Required arguments

key

is key name for a Bloom filter.

## Examples

redis> BF.ADD bf1 item_foo
(integer) 1
redis> BF.CARD bf1
(integer) 1
redis> BF.CARD bf_new
(integer) 0

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Supported | &#x2705; Flexible & Annual&#x2705; Free & Fixed | |

## Return information

One of the following:
* Integer reply: the number of items detected as unique that were added to the Bloom filter (items that caused at least one bit to be set in at least one sub-filter), or 0 when the given key does not exist.
* Simple error reply in these cases: invalid arguments, wrong key type, or when the filter is full.

Note: when key exists, BF.CARD returns the same value as BF.INFO key ITEMS .

-tab-sep-

One of the following:
* Integer reply: the number of items detected as unique that were added to the Bloom filter (items that caused at least one bit to be set in at least one sub-filter), or 0 when the given key does not exist.
* Simple error reply in these cases: invalid arguments, wrong key type, or when the filter is full.

Note: when key exists, BF.CARD returns the same value as BF.INFO key ITEMS .