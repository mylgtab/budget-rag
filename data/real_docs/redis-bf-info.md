Returns information about a Bloom filter.

## Required arguments

key

is key name for a Bloom filter.

## Optional arguments

CAPACITY

Return the number of unique items that can be stored in this Bloom filter before scaling would be required (including already added items).

SIZE

Return the memory size: number of bytes allocated for this Bloom filter.

FILTERS

Return the number of sub-filters.

ITEMS

Return the number of items that were added to this Bloom filter and detected as unique (items that caused at least one bit to be set in at least one sub-filter).

EXPANSION

Return the expansion rate.

## Examples

redis> BF.ADD bf1 observation1
(integer) 1
redis> BF.INFO bf1
 1) Capacity
 2) (integer) 100
 3) Size
 4) (integer) 240
 5) Number of filters
 6) (integer) 1
 7) Number of items inserted
 8) (integer) 1
 9) Expansion rate
10) (integer) 2
redis> BF.INFO bf1 CAPACITY
1) (integer) 100

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Supported | &#x2705; Flexible & Annual&#x2705; Free & Fixed | |

## Return information

One of the following:
* A singleton array reply with an integer representing the value of the requested property.
* An array reply with simple string and integer pairs.
* Simple error reply in these cases: invalid arguments, wrong key type, or when the key does not exist.

-tab-sep-

One of the following:
* Map reply with simple string and integer pairs.
* Simple error reply in these cases: invalid arguments, wrong key type, or when the key does not exist.