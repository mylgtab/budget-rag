Return the position of the first bit set to 1 or 0 in a string.

The position is returned, thinking of the string as an array of bits from left to
right, where the first byte's most significant bit is at position 0, the second
byte's most significant bit is at position 8, and so forth.

The same bit position convention is followed by GETBIT and SETBIT .

By default, all the bytes contained in the string are examined.
It is possible to look for bits only in a specified interval passing the additional arguments _start_ and _end_ (it is possible to just pass _start_, the operation will assume that the end is the last byte of the string. However there are semantic differences as explained later).
By default, the range is interpreted as a range of bytes and not a range of bits, so start=0 and end=2 means to look at the first three bytes.

You can use the optional BIT modifier to specify that the range should be interpreted as a range of bits.
So start=0 and end=2 means to look at the first three bits.

Note that bit positions are returned always as absolute values starting from bit zero even when _start_ and _end_ are used to specify a range.

Like for the GETRANGE command start and end can contain negative values in
order to index bytes starting from the end of the string, where -1 is the last
byte, -2 is the penultimate, and so forth. When BIT is specified, -1 is the last
bit, -2 is the penultimate, and so forth.

If the key does not exist, it is treated as an infinite array of zero bits: searching for a clear bit (0) returns 0, while searching for a set bit (1) returns -1. In contrast, an existing empty string (a key holding "") contains no bits at all, so searching for either 0 or 1 always returns -1.

## Required arguments

key

The name of the key that holds the string.

bit

The bit value to search for: 0 or 1 .

## Optional arguments

start

The offset to start searching from. By default a byte offset; negative values count from the end of the string.

end

The offset to stop searching at, inclusive.

BYTE | BIT

Interpret start and end as byte offsets ( BYTE , the default) or bit offsets ( BIT ).

## Examples

[code example]

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x2705; Standard&#x2705; Active-Active | &#x2705; Standard&#x2705; Active-Active | |

## Return information

One of the following:
* Integer reply: the position of the first bit set to 1 or 0 according to the request
* Integer reply: -1 . In case the bit argument is 1 and the string is empty or composed of just zero bytes
If we look for set bits (the bit argument is 1) and the string is empty or composed of just zero bytes, -1 is returned.
If we look for clear bits (the bit argument is 0) and the string only contains bits set to 1, the function returns the first bit not part of the string on the right. So if the string is three bytes set to the value 0xff the command BITPOS key 0 will return 24, since up to bit 23 all the bits are 1.
The function considers the right of the string as padded with zeros if you look for clear bits and specify no range or the _start_ argument only .
However, this behavior changes if you are looking for clear bits and specify a range with both _start_ and _end_.
If a clear bit isn't found in the specified range, the function returns -1 as the user specified a clear range and there are no 0 bits in that range.

-tab-sep-

One of the following:
* Integer reply: the position of the first bit set to 1 or 0 according to the request
* Integer reply: -1 . In case the bit argument is 1 and the string is empty or composed of just zero bytes
If we look for set bits (the bit argument is 1) and the string is empty or composed of just zero bytes, -1 is returned.
If we look for clear bits (the bit argument is 0) and the string only contains bits set to 1, the function returns the first bit not part of the string on the right. So if the string is three bytes set to the value 0xff the command BITPOS key 0 will return 24, since up to bit 23 all the bits are 1.
The function considers the right of the string as padded with zeros if you look for clear bits and specify no range or the _start_ argument only .
However, this behavior changes if you are looking for clear bits and specify a range with both _start_ and _end_.
If a clear bit isn't found in the specified range, the function returns -1 as the user specified a clear range and there are no 0 bits in that range.