The redisCommand() and redisCommandArgv() functions return
a pointer to a redisReply object when you issue a command (see
Issue commands
for more information). This type supports all
reply formats defined in the
RESP2 and RESP3
protocols, so its content varies greatly between calls.

A simple example is the status response returned by the SET 
command. The code below shows how to get this from the redisReply 
object:

[code example]

A null reply indicates an error, so you should always check for this.
If an error does occur, then the redisContext object will have a
non-zero error number in its integer err field and a textual
description of the error in its errstr field.

For SET, a successful call will simply return an "OK" string that you
can access with the reply->str field. The code in the example prints
this to the console, but you should check for the specific value to ensure
the command executed correctly.

The redisCommand() call allocates memory for the reply, so you should
always free it using freeReplyObject() when you have finished using
the reply. If you want to reuse the reply variable then it is wise to
set it to NULL after you free it, so that you don't accidentally use
the stale pointer later.

## Reply formats

The Redis
 RESP 
protocols support several different reply formats for commands.

You can find the reply format for a command at the end of its
reference page in the RESP2/RESP3 Reply section (for example, the
 INCRBY page shows that the
command has an integer result). You can also determine the format
using the type field of the reply object. This contains a
different integer value for each type. The hiredis.h header file
defines constants for all of these integer values (for example REDIS_REPLY_STRING ).

The redisReply struct has several fields to contain different
types of replies, with different fields being set depending on
the value of the type field. The table below shows the type
constants, the corresponding reply type, and the fields you can
use to access the reply value:

| Constant | Type | Relevant fields of redisReply | RESP protocol |

| REDIS_REPLY_STATUS | Simple string | reply->str: the string value ( char* ) reply->len: the string length ( size_t ) | 2, 3 |
| REDIS_REPLY_ERROR | Simple error | reply->str: the string value ( char* ) reply->len: the string length ( size_t ) | 2, 3 |
| REDIS_REPLY_INTEGER | Integer | reply->integer: the integer value ( long long )| 2, 3 |
| REDIS_REPLY_NIL | Null | No data | 2, 3 |
| REDIS_REPLY_STRING | Bulk string | reply->str: the string value ( char* ) reply->len: the string length ( size_t ) | 2, 3 |
| REDIS_REPLY_ARRAY | Array | reply->elements: number of elements ( size_t ) reply->element: array elements ( redisReply ) | 2, 3 |
| REDIS_REPLY_DOUBLE | Double | reply->str: double value as string ( char* ) reply->len: the string length ( size_t ) | 3 |
| REDIS_REPLY_BOOL | Boolean | reply->integer: the boolean value, 0 or 1 ( long long ) | 3 |
| REDIS_REPLY_MAP | Map | reply->elements: number of elements ( size_t ) reply->element: array elements ( redisReply ) | 3 |
| REDIS_REPLY_SET | Set | reply->elements: number of elements ( size_t ) reply->element: array elements ( redisReply ) | 3 |
| REDIS_REPLY_PUSH | Push | reply->elements: number of elements ( size_t ) reply->element: array elements ( redisReply ) | 3 |
| REDIS_REPLY_BIGNUM | Big number | reply->str: number value as string ( char* ) reply->len: the string length ( size_t ) | 3 |
| REDIS_REPLY_VERB | Verbatim string | reply->str: the string value ( char* ) reply->len: the string length ( size_t ) reply->vtype: content type ( char[3] ) | 3 |

## Reply format processing examples

The sections below explain how to process specific reply types in
more detail.

### Integers

The REDIS_REPLY_INTEGER and REDIS_REPLY_BOOL reply types both
contain values in reply->integer. However, REDIS_REPLY_BOOL is
rarely used. Even when the command essentially returns a boolean value,
the reply is usually reported as an integer. 

[code example]

### Strings

The REDIS_REPLY_STATUS, REDIS_REPLY_ERROR, REDIS_REPLY_STRING,
 REDIS_REPLY_DOUBLE, REDIS_REPLY_BIGNUM, and REDIS_REPLY_VERB 
are all returned as strings, with the main difference lying in how
you interpret them. For all these types, the string value is
returned in reply->str and the length of the string is in
 reply->len. The example below shows some of the possibilities.

[code example]

### Arrays and maps

Arrays (reply type REDIS_REPLY_ARRAY ) and maps (reply type REDIS_REPLY_MAP )
are returned by commands that retrieve several values at the
same time. For both types, the number of elements in the reply is contained in
 reply->elements and the pointer to the array itself is reply->element.
Each item in the array is of type redisReply. The array elements
are typically simple types rather than arrays or maps.

The example below shows how to get the items from a
list:

[code example]

A map is essentially the same as an array but it has the extra
guarantee that the items will be listed in key-value pairs.
The example below shows how to get all the fields from a
hash using
 HGETALL:

[code example]

## Handling errors

When a command executes successfully, the err field of the context
object will be set to zero. If a command fails, it will return either
 NULL or REDIS_ERR, depending on which function and command you used. When
this happens, context->err will contain an error code

- REDIS_ERR_IO: There was an I/O error while creating the connection,
 or while trying to write or read data. Whenever context->err contains
 REDIS_ERR_IO, you can use the features of the standard library file
 errno.h to find out more
 information about the error.
- REDIS_ERR_EOF: The server closed the connection which resulted in an empty read.
- REDIS_ERR_PROTOCOL: There was an error while parsing the
 RESP protocol.
- REDIS_ERR_OTHER: Any other error. Currently, it is only used when the connection
 hostname can't be resolved.

The context object also has an errstr field that contains a descriptive error message.