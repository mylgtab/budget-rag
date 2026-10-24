Iterates existing elements in a range, returning index-value pairs.

## Required arguments

key

The name of the key that holds the array.

start

The zero-based integer index at which to begin scanning. If start is greater than end , elements are returned in reverse index order.

end

The zero-based integer index at which to stop scanning (inclusive).

## Optional arguments

LIMIT

The maximum number of index-value pairs to return. When omitted, all elements in the range are returned. Unlike ARGETRANGE , empty slots are not included in the output, so LIMIT caps the number of existing elements returned.

## Examples

redis> ARSET myarray 0 "a"
(integer) 1
redis> ARSET myarray 5 "b"
(integer) 1
redis> ARSET myarray 9 "c"
(integer) 1
redis> ARSCAN myarray 0 10
1) 1) (integer) 0
 2) "a"
2) 1) (integer) 5
 2) "b"
3) 1) (integer) 9
 2) "c"
redis> ARSCAN myarray 0 10 LIMIT 2
1) 1) (integer) 0
 2) "a"
2) 1) (integer) 5
 2) "b"

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

Array reply: Array of index-value pairs, each a two-element array: [[idx1, val1], [idx2, val2], ...] 

-tab-sep-

Array reply: Array of index-value pairs, each a two-element array: [[idx1, val1], [idx2, val2], ...]