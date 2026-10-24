Begins an incremental save of the Bloom filter.

This command is useful for large Bloom filters that cannot fit into the DUMP and RESTORE model.

The first time this command is called, the value of iter should be 0. 

This command returns successive (iter, data) pairs until (0, NULL) to indicate completion.

## Required arguments

key

is key name for a Bloom filter to save.

iterator

Iterator value; either 0 or the iterator from a previous invocation of this command

## Examples

redis> BF.RESERVE bf 0.1 10
OK
redis> BF.ADD bf item1
(integer) 1
redis> BF.SCANDUMP bf 0
1) (integer) 1
2) "\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00\x02\x00\x00\x00\b\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x9a\x99\x99\x99\x99\x99\xa9?J\xf7\xd4\x9e\xde\xf0\x18@\x05\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x00"
redis> BF.SCANDUMP bf 1
1) (integer) 9
2) "\x01\b\x00\x80\x00\x04 \x00"
redis> BF.SCANDUMP bf 9
1) (integer) 0
2) ""
redis> DEL bf
(integer) 1
redis> BF.LOADCHUNK bf 1 "\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00\x02\x00\x00\x00\b\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x9a\x99\x99\x99\x99\x99\xa9?J\xf7\xd4\x9e\xde\xf0\x18@\x05\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x00"
OK
redis> BF.LOADCHUNK bf 9 "\x01\b\x00\x80\x00\x04 \x00"
OK
redis> BF.EXISTS bf item1
(integer) 1

Python code:

chunks = []
iter = 0
while True:
 iter, data = BF.SCANDUMP(key, iter)
 if iter == 0:
 break
 else:
 chunks.append([iter, data])

# Load it back
for chunk in chunks:
 iter, data = chunk
 BF.LOADCHUNK(key, iter, data)

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Supported | &#x2705; Flexible & Annual&#x2705; Free & Fixed | |

## Return information

One of the following:
* Array reply: a two-element array of an Integer reply (_Iterator_) and a Bulk string reply (_Data_).
* Simple error reply in these cases: invalid arguments, the key was not found, or the key is of the wrong type.

The Iterator is passed as input to the next invocation of BF.SCANDUMP . If _Iterator_ is 0, then it means iteration has completed.

The iterator-data pair should also be passed to BF.LOADCHUNK when restoring the filter.

-tab-sep-

One of the following:
* Array reply: a two-element array of an Integer reply (_Iterator_) and a Bulk string reply (_Data_).
* Simple error reply in these cases: invalid arguments, the key was not found, or the key is of the wrong type.

The Iterator is passed as input to the next invocation of BF.SCANDUMP . If _Iterator_ is 0, then it means iteration has completed.

The iterator-data pair should also be passed to BF.LOADCHUNK when restoring the filter.