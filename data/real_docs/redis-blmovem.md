> [!NOTE]
> This command's behavior varies in clustered Redis environments. See the multi-key operations page for more information.

 BLMOVEM is the blocking variant of LMOVEM .
When source holds enough elements to satisfy the request, this command behaves
exactly like LMOVEM . Otherwise, Redis blocks the connection until
another client pushes the required elements to source or until timeout is
reached.

## Required arguments

source

The key of the source list.

destination

The key of the destination list.

LEFT | RIGHT

The end of source to pop elements from: LEFT (head) or RIGHT (tail).

LEFT | RIGHT

The end of destination to push elements to: LEFT (head) or RIGHT (tail).

timeout

The maximum time to block, in seconds. A timeout of 0 blocks indefinitely.

## Optional arguments

The how-many block controls how many elements are moved and in what order.
When you include it, you must provide both a selector ( COUNT or EXACTLY )
and an ordering ( OBO or BULK ).

COUNT count | EXACTLY exactly

The number of elements to move:

- COUNT count moves up to count elements. If source holds fewer than
 count elements, all of them are moved. This matches the count semantics of
 LPOP and LMPOP .
- EXACTLY exactly moves exactly exactly elements. If source holds fewer
 than exactly elements, the command blocks (see Blocking behavior).

OBO | BULK

The order in which elements are pushed onto destination :

- OBO (one by one) moves elements individually: each element is popped from
 source and pushed to destination before the next one is moved.
- BULK moves all of the elements at once, preserving their relative order.

See the Element ordering section of the LMOVEM documentation for details.

## Details

### Blocking behavior

Whether BLMOVEM blocks depends on the selector:

- With COUNT , the command blocks only while source is empty. As soon as at
 least one element is available it unblocks, moves up to count elements, and
 returns them.
- With EXACTLY , the command blocks while source holds fewer than the
 requested number of elements. It unblocks only once source grows to at least
 that length, then moves exactly that many elements atomically.

A timeout of 0 blocks indefinitely. When used inside a
 MULTI / EXEC block or a Lua script, BLMOVEM does not block; it
behaves like LMOVEM and, when the request cannot be satisfied,
returns nil immediately.

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

One of the following:
* Array reply: the moved elements, in destination order.
* Nil reply: the operation timed out.

-tab-sep-

One of the following:
* Array reply: the moved elements, in destination order.
* Null reply: the operation timed out.

## See also

 BLMOVE | LMOVEM | BLMPOP | BRPOPLPUSH 

## Related topics

- Redis lists