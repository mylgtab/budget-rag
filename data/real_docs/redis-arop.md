Performs aggregate operations on array elements in a range.

## Required arguments

key

The name of the key that holds the array.

start

The zero-based integer index of the first element in the range to aggregate.

end

The zero-based integer index of the last element in the range to aggregate (inclusive). The command always scans from the lower to the higher index regardless of argument order.

operation

The aggregate function to apply to all non-empty elements in [start, end] . One of:

- SUM — Returns the sum of all numeric values as a bulk string.
- MIN — Returns the minimum numeric value as a bulk string.
- MAX — Returns the maximum numeric value as a bulk string.
- AND — Returns the bitwise AND of all values, treating each as an integer (floats are truncated toward zero).
- OR — Returns the bitwise OR of all values, treating each as an integer (floats are truncated toward zero).
- XOR — Returns the bitwise XOR of all values, treating each as an integer (floats are truncated toward zero).
- MATCH value — Returns the count of elements whose value equals value as an integer reply.
- USED — Returns the count of non-empty elements in the range as an integer reply.

 SUM , MIN , and MAX return nil when no numeric elements are present in the range. AND , OR , and XOR return nil when the range is empty.

## Examples

redis> ARMSET myarray 0 "10" 1 "20" 2 "30"
(integer) 3
redis> AROP myarray 0 2 SUM
"60"
redis> AROP myarray 0 2 MIN
"10"
redis> AROP myarray 0 2 MAX
"30"
redis> AROP myarray 0 2 MATCH "10"
(integer) 1
redis> AROP myarray 0 2 USED
(integer) 3
redis> ARMSET flags 0 "255" 1 "15" 2 "240"
(integer) 3
redis> AROP flags 0 2 AND
(integer) 0
redis> AROP flags 0 2 OR
(integer) 255

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

One of the following:
* Bulk string reply: Result of the operation.
* Integer reply: Integer result for MATCH, USED, AND, OR, XOR.
* Nil reply: Null if no elements match the operation.

-tab-sep-

One of the following:
* Bulk string reply: Result of the operation.
* Integer reply: Integer result for MATCH, USED, AND, OR, XOR.
* Null reply: Null if no elements match the operation.