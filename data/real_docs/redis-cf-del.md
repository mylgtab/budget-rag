Deletes an item once from the filter.

If the item exists only once, it will be removed from the filter. If the item was added multiple times, it will still be present.

> [!NOTE]
> Never use this command to delete an item unless you are certain you've added the item to the filter. Deleting an item you didn't previously add may corrupt the filter and cause false negatives.

## Required arguments

key

is key name for a cuckoo filter.

item

is an item to delete.

## Complexity

O(n), where n is the number of sub-filters . Both alternative locations are
checked on all sub-filters .

## Examples

redis> CF.INSERT cf ITEMS item1 item2 item2
1) (integer) 1
2) (integer) 1
3) (integer) 1
redis> CF.DEL cf item1
(integer) 1
redis> CF.DEL cf item1
(integer) 0
redis> CF.DEL cf item2
(integer) 1
redis> CF.DEL cf item2
(integer) 1
redis> CF.DEL cf item2
(integer) 0

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Supported | &#x2705; Flexible & Annual&#x2705; Free & Fixed | |

## Return information

One of the following:
* Integer reply 1 for successfully deleting an item, or 0 if no such item was found in the filter.
* Simple error reply in these cases: invalid arguments or wrong key type.

-tab-sep-

One of the following:
* Boolean reply true for successfully deleting an item, or false if no such item was found in the filter.
* Simple error reply in these cases: invalid arguments or wrong key type.