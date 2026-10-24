Returns an estimation of the number of times a given item was added to a cuckoo filter.

If you just want to check that a given item was added to a cuckoo filter, use CF.EXISTS .

## Required arguments

key

is key name for a cuckoo filter.

item

is an item to check.

## Examples

redis> CF.INSERT cf ITEMS item1 item2 item2
1) (integer) 1
2) (integer) 1
3) (integer) 1
redis> CF.COUNT cf item1
(integer) 1
redis> CF.COUNT cf item2
(integer) 2

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Supported | &#x2705; Flexible & Annual&#x2705; Free & Fixed | |

## Return information

One of the following:
* Integer reply, where a positive value is an estimation of the number of times item was added to the filter. An overestimation is possible, but not an underestimation. 0 means that key does not exist or that item had not been added to the filter. See the note in CF.DEL .
* Simple error in these cases: invalid arguments or wrong key type.

-tab-sep-

One of the following:
* Integer reply, where a positive value is an estimation of the number of times item was added to the filter. An overestimation is possible, but not an underestimation. 0 means that key does not exist or that item had not been added to the filter. See the note in CF.DEL .
* Simple error in these cases: invalid arguments or wrong key type.