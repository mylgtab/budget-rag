> [!NOTE]
> This command's behavior varies in clustered Redis environments. See the multi-key operations page for more information.

Perform a bitwise operation between multiple keys (containing string values) and
store the result in the destination key.

The BITOP command supports eight bitwise operations: AND , OR , XOR ,
 NOT , DIFF , DIFF1 , ANDOR , and ONE . The valid forms to call the command are:

* BITOP AND destkey srckey1 srckey2 srckey3 ... srckeyN 

 A bit in destkey is set only if it is set in all source bitmaps.
* BITOP OR destkey srckey1 srckey2 srckey3 ... srckeyN 

 A bit in destkey is set only if it is set in at least one source bitmap.
* BITOP XOR destkey srckey1 srckey2 srckey3 ... srckeyN 

 Mostly used with two source bitmaps, a bit in destkey is set only if its value differs between the two source bitmaps.
* BITOP NOT destkey srckey 

 NOT is a unary operator and only supports a single source bitmap; set the bit to the inverse of its value in the source bitmap.
* BITOP DIFF destkey X [Y1 Y2 ...] 1

 A bit in destkey is set if it is set in X , but not in any of Y1, Y2, ... .
* BITOP DIFF1 destkey X [Y1 Y2 ...] 1

 A bit in destkey is set if it is set in one or more of Y1, Y2, ... , but not in X .
* BITOP ANDOR destkey X [Y1 Y2 ...] 1

 A bit in destkey is set if it is set in X and also in one or more of Y1, Y2, ... .
* BITOP ONE destkey X1 [X2 X3 ...] 1

 A bit in destkey is set if it is set in exactly one of X1, X2, ... .

The result of each operation is always stored at destkey .

1. Added in Redis 8.2.

## Required arguments

operation

The bitwise operation to perform: AND , OR , XOR , NOT , DIFF , DIFF1 , ANDOR , or ONE . NOT accepts exactly one source key.

destkey

The key to store the result in.

key [key ...]

One or more source keys.

## Examples

1. Basic usage example using the AND operator:

redis> BITFIELD key1 SET i8 #0 255
1) (integer) 0
redis> BITFIELD key2 SET i8 #0 85
1) (integer) 0
redis> BITOP AND dest key1 key2
(integer) 1
redis> BITFIELD dest GET i8 #0
1) (integer) 85

2. Suppose you want to expose people to a book-related ad. The target audience is people who love to read books and are interested in fantasy, adventure, or science fiction. Assume you have the following bitmaps:

* LRB - people who love to read books.
* B:F - people interested in fantasy.
* B:A - people interested in adventure.
* B:SF - people interested in science fiction.

To create a bitmap representing the target audience, use the following command:

[code example]

## Details

### Handling of strings with different lengths

When an operation is performed between strings having different lengths, all the
strings shorter than the longest string in the set are treated as if they were
zero-padded up to the length of the longest string.

The same holds true for non-existent keys, that are considered as a stream of
zero bytes up to the length of the longest string.

### Pattern: real time metrics using bitmaps

 BITOP is a good complement to the pattern documented in the BITCOUNT command
documentation.
Different bitmaps can be combined in order to obtain a target bitmap where
the population counting operation is performed.

See the article called "Fast easy realtime metrics using Redis
bitmaps" for an interesting use cases.

### Performance considerations

 BITOP is a potentially slow command as it runs in O(N) time.
Care should be taken when running it against long input strings.

For real-time metrics and statistics involving large inputs a good approach is
to use a replica (with replica-read-only option enabled) where the bit-wise
operations are performed to avoid blocking the master instance.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

Integer reply: the size of the string stored in the destination key is equal to the size of the longest input string.

-tab-sep-

Integer reply: the size of the string stored in the destination key is equal to the size of the longest input string.