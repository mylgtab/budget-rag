Inserts values into a ring buffer of specified size, wrapping and truncating as needed.

## Required arguments

key

The name of the key that holds the array.

size

The size of the ring buffer window. Each value is inserted at insert_idx % size , wrapping back to index 0 when the end of the window is reached. When the buffer is full, newer values overwrite older ones. If size is smaller than the current window, the array is truncated to fit.

value

One or more string values to insert into the ring buffer. Each value is placed at the next position in the ring and the cursor advances accordingly.

## Examples

redis> ARRING readings 3 "v0"
(integer) 0
redis> ARRING readings 3 "v1"
(integer) 1
redis> ARRING readings 3 "v2"
(integer) 2
redis> ARRING readings 3 "v3"
(integer) 0
redis> ARGET readings 0
"v3"
redis> ARCOUNT readings
(integer) 3
redis> ARLASTITEMS readings 3
1) "v1"
2) "v2"
3) "v3"

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

Integer reply: The last index where a value was inserted.

-tab-sep-

Integer reply: The last index where a value was inserted.