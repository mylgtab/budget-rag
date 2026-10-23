This example shows how to create a
search index
for JSON documents and
run queries against the index. It then goes on to show the slight differences
in the equivalent code for hash
documents.

> [!NOTE]
> From v9.8.0 onwards,
> go-redis uses query dialect 2 by default.
> Redis Search methods such as FTSearch() 
> will explicitly request this dialect, overriding the default set for the server.
> See
> Query dialects
> for more information.

## Initialize

Make sure that you have Redis Open Source
or another Redis server available. Also install the
 go-redis client library if you
haven't already done so.

Add the following dependencies:

## Create data

Create some test data to add to your database. The example data shown
below is compatible with both JSON and hash objects.

## Add the index

Connect to your Redis database. The code below shows the most
basic connection but see
Connect to the server
to learn more about the available connection options.

&nbsp;

> [!NOTE]
> The connection options in the example specify
> RESP2 in the Protocol 
> field. We recommend that you use RESP2 for Redis Search operations in go-redis 
> because some of the response structures for the default RESP3 are currently
> incomplete and so you must handle the "raw" responses in your own code.
>
> If you do want to use RESP3, you should set the UnstableResp3 option when
> you connect:
>
> [code example]
>
> You must also access command results using the RawResult() and RawVal() methods
> rather than the usual Result() and Val():
>
> [code example]

Use the code below to create a search index. The FTCreateOptions parameter enables
indexing only for JSON objects where the key has a user: prefix.
The
schema
for the index has three fields for the user's name, age, and city.
The FieldName field of the FieldSchema struct specifies a
JSON path
that identifies which data field to index. Use the As struct field
to provide an alias for the JSON path expression. You can use
the alias in queries as a short and intuitive way to refer to the
expression, instead of typing it in full:

## Add the data

Add the three sets of user data to the database as
JSON objects.
If you use keys with the user: prefix then Redis will index the
objects automatically as you add them:

## Query the data

You can now use the index to search the JSON objects. The
query
below searches for objects that have the text "Paul" in any field
and have an age value in the range 30 to 40:

Specify query options to return only the city field:

You can also use the same query with the CountOnly option
enabled to get the number of documents found without
returning the documents themselves.

Use an
aggregation query
to count all users in each city, with the results sorted by city.

## Differences with hash documents

Indexing for hash documents is very similar to JSON indexing but you
need to specify some slightly different options.

When you create the schema for a hash index, you don't need to
add aliases for the fields, since you use the basic names to access
the fields anyway. Also, you must set OnHash to true in the FTCreateOptions 
object when you create the index. The code below shows these changes with
a new index called hash-idx:users, which is otherwise the same as
the idx:users index used for JSON documents in the previous examples.

You use HSet() to add the hash
documents instead of JSONSet(),
but the same flat userX maps work equally well with either
hash or JSON:

The query commands work the same here for hash as they do for JSON (but
the name of the hash index is different). The format of the result is
almost the same except that the fields are returned directly in the
 Document object map of the result (for JSON, the fields are all enclosed
in a string under the key "$"):

### Bulk import with HIMPORT

From Redis Open Source 8.10, you can also add the hash documents with the
 HIMPORT command family. This creates the same
hashes as HSet(), but lets Redis store them as
compact hashes, which use
less memory when many keys share the same field names. Redis Search indexes
these hashes in the same way.

Declare the field names once with
 HImportPrepare(), then create each
document with HImportSet(), passing only
its values, in the same order as the field names. Use a
pipeline to send all the
imports in one round trip:

 HImportSet() replaces any existing key, so running this code after the
 HSet() calls leaves you with the same three documents. The query returns
the same result.

> [!NOTE]
> HIMPORT requires go-redis v9.22.0 or later, and go-redis marks its
> support as experimental, so the API might change. Redis Cloud and
> Redis Software don't support HIMPORT.

## More information

See the Redis Search docs
for a full description of all query features with examples.