Begins an incremental save of the cuckoo filter.

This command is useful for large cuckoo filters that cannot fit into the DUMP and RESTORE model.

The first time this command is called, the value of iter should be 0. 

This command returns successive (iter, data) pairs until (0, NULL) indicates completion.

## Required arguments

key

is key name for a cuckoo filter to save.

iterator

Iterator value; either 0 or the iterator from a previous invocation of this command

## Examples

redis> CF.RESERVE cf 8
OK
redis> CF.ADD cf item1
(integer) 1
redis> CF.SCANDUMP cf 0
1) (integer) 1
2) "\x01\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x14\x00\x01\x00"
redis> CF.SCANDUMP cf 1
1) (integer) 9
2) "\x00\x00\x00\x00\a\x00\x00\x00"
redis> CF.SCANDUMP cf 9
1) (integer) 0
2) (nil) 
redis> DEL cf
(integer) 1
redis> CF.LOADCHUNK cf 1 "\x01\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x14\x00\x01\x00"
OK
redis> CF.LOADCHUNK cf 9 "\x00\x00\x00\x00\a\x00\x00\x00"
OK
redis> CF.EXISTS cf item1
(integer) 1

Python code:

chunks = []
iter = 0
while True:
 iter, data = CF.SCANDUMP(key, iter)
 if iter == 0:
 break
 else:
 chunks.append([iter, data])

# Load it back
for chunk in chunks:
 iter, data = chunk
 CF.LOADCHUNK(key, iter, data)

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Supported | &#x2705; Flexible & Annual&#x2705; Free & Fixed | |

## Return information

One of the following:
* Array reply: a two-element array of an Integer reply (_Iterator_) and a Bulk string reply (_Data_).
* Simple error reply in these cases: invalid arguments, the key was not found, or the key is of the wrong type.

The Iterator is passed as input to the next invocation of CF.SCANDUMP . If _Iterator_ is 0, then it means iteration has completed.

The iterator-data pair should also be passed to CF.LOADCHUNK when restoring the filter.

-tab-sep-

One of the following:
* Array reply: a two-element array of an Integer reply (_Iterator_) and a Bulk string reply (_Data_).
* Simple error reply in these cases: invalid arguments, the key was not found, or the key is of the wrong type.

The Iterator is passed as input to the next invocation of CF.SCANDUMP . If _Iterator_ is 0, then it means iteration has completed.

The iterator-data pair should also be passed to CF.LOADCHUNK when restoring the filter.