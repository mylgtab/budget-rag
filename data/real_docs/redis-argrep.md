Searches array elements in a range using textual predicates and returns the indices of the matching elements. Empty slots in the range are skipped.

## Required arguments

key

The name of the key that holds the array.

start

The zero-based integer index at which to begin searching. The special value - denotes the first index of the array. If start is greater than end , matches are returned in reverse index order.

end

The zero-based integer index at which to stop searching (inclusive). The special value + denotes the last index of the array.

predicate

One or more textual predicates to evaluate against each non-empty element in the range. Each predicate is one of:

- EXACT string — Matches elements whose value is exactly equal to string .
- MATCH string — Matches elements whose value contains string as a substring.
- GLOB pattern — Matches elements whose value matches the glob-style pattern (with * , ? , and [...] wildcards), the same syntax used by KEYS and SCAN MATCH .
- RE pattern — Matches elements whose value matches the regular expression pattern .

When more than one predicate is supplied, use the AND or OR option to control how they are combined. The default is OR .

## Optional arguments

options

Zero or more of the following modifiers:

- AND — Combine multiple predicates with logical AND. An element matches only if every predicate matches.
- OR — Combine multiple predicates with logical OR. An element matches if any predicate matches. This is the default.
- LIMIT limit — Stop after limit matches have been collected. limit must be a positive integer. When omitted, all matches in the range are returned.
- WITHVALUES — In addition to each matching index, return the matching value. The reply becomes an array of index-value pairs, each a two-element array.
- NOCASE — Perform case-insensitive comparisons for EXACT , MATCH , GLOB , and RE .

## Examples

redis> ARMSET log 0 "boot: ok" 1 "warn: disk" 2 "ERROR: cpu" 3 "info: ready" 4 "error: net"
(integer) 5
redis> ARGREP log - + MATCH "error" NOCASE
1) (integer) 2
2) (integer) 4
redis> ARGREP log - + MATCH "error" NOCASE WITHVALUES
1) 1) (integer) 2
 2) "ERROR: cpu"
2) 1) (integer) 4
 2) "error: net"
redis> ARGREP log 0 4 GLOB "warn:*" OR GLOB "error:*"
1) (integer) 1
2) (integer) 4
redis> ARGREP log 0 4 RE "^[A-Za-z]+: (cpu|net)$" NOCASE WITHVALUES
1) 1) (integer) 2
 2) "ERROR: cpu"
2) 1) (integer) 4
 2) "error: net"
redis> ARGREP log 0 4 EXACT "info: ready"
1) (integer) 3
redis> ARGREP log - + MATCH "error" NOCASE LIMIT 1
1) (integer) 2

## Redis Software and Redis Cloud compatibility

| RedisSoftware | RedisCloud | Notes |
|:----------------------|:-----------------|:------|
| &#x274c; Standard&#x274c; Active-Active | &#x274c; Standard&#x274c; Active-Active | |

## Return information

Array reply: Indices of the matching elements, in the same order in which the range is traversed (ascending when start end ). When WITHVALUES is given, an array of index-value pairs, each a two-element array: [[idx1, val1], [idx2, val2], ...] . An empty array is returned when the key does not exist or no element matches.

-tab-sep-

Array reply: Indices of the matching elements, in the same order in which the range is traversed (ascending when start end ). When WITHVALUES is given, an array of index-value pairs, each a two-element array: [[idx1, val1], [idx2, val2], ...] . An empty array is returned when the key does not exist or no element matches.