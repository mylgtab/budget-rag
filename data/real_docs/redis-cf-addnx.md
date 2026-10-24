Adds an item to a cuckoo filter if the item does not exist.

This command is similar to the combination of CF.EXISTS and CF.ADD . It does not add an item into the filter if its fingerprint already exists.

Notes:

- This command is slower than CF.ADD because it first checks whether the item exists.
- Since CF.EXISTS can result in false positive, CF.ADDNX may not add an item because it is supposedly already exist, which may be wrong.

## Required arguments

key

is key name for a cuckoo filter to add items to.

If key does not exist - a new cuckoo filter is created.

item

is an item to add.

## Examples

redis> CF.ADDNX cf item
(integer) 1
redis> CF.ADDNX cf item
(integer) 0

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Supported | &#x2705; Flexible & Annual&#x2705; Free & Fixed | |

## Return information

One of the following:
* Integer reply: 1 for successfully adding an item to the filter or 0 if the item's fingerprint already exists in the filter.
* Simple error reply in these cases: invalid arguments, wrong key type, or when the filter is full.

-tab-sep-

One of the following:
* Boolean reply: true for successfully adding an item to the filter or false if the item's fingerprint already exists in the filter.
* Simple error reply in these cases: invalid arguments, wrong key type, or when the filter is full.