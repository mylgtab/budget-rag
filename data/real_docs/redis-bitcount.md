Count the number of set bits (population counting) in a string.

By default all the bytes contained in the string are examined.
It is possible to specify the counting operation only in an interval passing the
additional arguments _start_ and _end_.

Like for the GETRANGE command start and end can contain negative values in
order to index bytes starting from the end of the string, where -1 is the last
byte, -2 is the penultimate, and so forth.

Non-existent keys are treated as empty strings, so the command will return zero.

By default, the additional arguments _start_ and _end_ specify a byte index.
We can use an additional argument BIT to specify a bit index.
So 0 is the first bit, 1 is the second bit, and so forth.
For negative values, -1 is the last bit, -2 is the penultimate, and so forth.

## Required arguments

key

The name of the key that holds the string.

## Optional arguments

start end

Count set bits only within the range from start to end (inclusive). By default these are byte offsets; negative values count from the end of the string.

BYTE | BIT

Interpret start and end as byte offsets ( BYTE , the default) or bit offsets ( BIT ).

## Examples

redis> SET mykey "foobar"
OK
redis> BITCOUNT mykey
(integer) 26
redis> BITCOUNT mykey 0 0
(integer) 4
redis> BITCOUNT mykey 1 1
(integer) 6
redis> BITCOUNT mykey 1 1 BYTE
(integer) 6
redis> BITCOUNT mykey 5 30 BIT
(integer) 17

## Details

### Pattern: real-time metrics using bitmaps

Bitmaps are a very space-efficient representation of certain kinds of
information.
One example is a Web application that needs the history of user visits, so that
for instance it is possible to determine what users are good targets of beta
features.

Using the SETBIT command this is trivial to accomplish, identifying every day
with a small progressive integer.
For instance day 0 is the first day the application was put online, day 1 the
next day, and so forth.

Every time a user performs a page view, the application can register that in
the current day the user visited the web site using the SETBIT command setting
the bit corresponding to the current day.

Later it will be trivial to know the number of single days the user visited the
web site simply calling the BITCOUNT command against the bitmap.

A similar pattern where user IDs are used instead of days is described
in the article called "Fast easy realtime metrics using Redis
bitmaps".

### Performance considerations

In the above example of counting days, even after 10 years the application is
online we still have just 365*10 bits of data per user, that is just 456 bytes
per user.
With this amount of data BITCOUNT is still as fast as any other O(1) Redis
command like GET or INCR .

When the bitmap is big, there are two alternatives:

* Taking a separated key that is incremented every time the bitmap is modified.
 This can be very efficient and atomic using a small Redis Lua script.
* Running the bitmap incrementally using the BITCOUNT _start_ and _end_
 optional parameters, accumulating the results client-side, and optionally
 caching the result into a key.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

Integer reply: the number of bits set to 1.

-tab-sep-

Integer reply: the number of bits set to 1.