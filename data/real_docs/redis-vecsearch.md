Redis Search
lets you index vector fields in hash
or JSON objects (see the
Vectors 
reference page for more information).
Among other things, vector fields can store *text embeddings*, which are AI-generated vector
representations of the semantic information in pieces of text. The
vector distance
between two embeddings indicates how similar they are semantically. By comparing the
similarity of an embedding generated from some query text with embeddings stored in hash
or JSON fields, Redis can retrieve documents that closely match the query in terms
of their meaning.

The example below uses the HuggingFace model
 all-MiniLM-L6-v2 
to generate the vector embeddings to store and index with Redis Search.
The code is first demonstrated for hash documents with a
separate section to explain the
differences with JSON documents.

> [!NOTE]
> From v3.0.0 onwards,
> Predis uses query dialect 2 by default.
> Redis Search methods such as ftSearch() 
> will explicitly request this dialect, overriding the default set for the server.
> See
> Query dialects
> for more information.

## Initialize

You can use the TransformersPHP
library to create the vector embeddings. Install the library with the following
command:

[code example]

## Import dependencies

Import the following classes and function in your source file:

[code example]

## Create the index

Connect to Redis and delete any index previously created with the
name vector_idx. (The
 ftdropindex() 
call throws an exception if the index doesn't already exist, which is
why you need the try...catch block.)

[code example]

Next, create the index.
The schema in the example below includes three fields: the text content to index, a
tag
field to represent the "genre" of the text, and the embedding vector generated from
the original text content. The embedding field specifies
HNSW 
indexing, the
L2
vector distance metric, Float32 values to represent the vector's components,
and 384 dimensions, as required by the all-MiniLM-L6-v2 embedding model.

The CreateArguments parameter to ftcreate() 
specifies hash objects for storage and a prefix doc: that identifies the hash objects
to index.

[code example]

## Add data

You can now supply the data objects, which will be indexed automatically
when you add them with hmset(), as long as
you use the doc: prefix specified in the index definition.

Use the $embed() function as shown below to create the embedding that
represents the content field.

To add an embedding as a field of a hash object, you must encode the
vector array as a binary string. The built-in
 pack() function is a convenient
way to do this in PHP, using the g* format specifier to denote a packed
array of float values. Note that if you are using
JSON
objects to store your documents instead of hashes, then you should store
the float array directly without first converting it to a binary
string (see Differences with JSON documents
below).

[code example]

### Bulk import with HIMPORT

From Redis Open Source 8.10, you can also add the documents with the
 HIMPORT command family. This creates the same
hashes as hmset(), but lets Redis store them as
compact hashes, which use
less memory when many keys share the same field names. Redis Search indexes
these hashes in the same way.

Declare the field names once by calling himport() with
 PREPARE, then create each
document by calling it with SET, passing only
its values, in the same order as the field names. Use a
pipeline to send all the
imports in one round trip:

[code example]

 HIMPORT SET replaces any existing key, so running this code after the
 hmset() calls leaves you with the same three documents.

> [!NOTE]
> HIMPORT requires Predis v3.6.0 or later, and Predis marks its
> support as experimental, so the API might change. Redis Cloud and
> Redis Software don't support HIMPORT.

## Run a query

After you have created the index and added the data, you are ready to run a query.
To do this, you must create another embedding vector from your chosen query
text. Redis calculates the vector distance between the query vector and each
embedding vector in the index as it runs the query. You can request the results to be
sorted to rank them in order of ascending distance.

The code below creates the query embedding using the $embed() function, as with
the indexing, and passes it as a parameter when the query executes (see
Vector search
for more information about using query parameters with embeddings).
The query is a
K nearest neighbors (KNN)
search that sorts the results in order of vector distance from the query vector.

The results are returned as an array with the number of results in the
first element. The remaining elements are alternating pairs with the
key of the returned document (for example, doc:0 ) first, followed by an array containing
the fields you requested (again as alternating key-value pairs).

[code example]

Assuming you have added the code from the steps above to your source file,
it is now ready to run, but note that it may take a while to complete when
you run it for the first time (which happens because the tokenizer must download the
 all-MiniLM-L6-v2 model data before it can
generate the embeddings). When you run the code, it outputs the following result text:

[code example]

The exact distances may differ slightly on your system.

Note that the results are ordered according to the value of the vector_distance 
field, with the lowest distance indicating the greatest similarity to the query.
As you would expect, the text *"That is a very happy person"* (from the doc:0 
document)
is the result judged to be most similar in meaning to the query text
*"That is a happy person"*.

## Differences with JSON documents

Indexing JSON documents is similar to hash indexing, but there are some
important differences. JSON allows much richer data modeling with nested fields, so
you must supply a path in the schema
to identify each field you want to index. However, you can declare a short alias for each
of these paths to avoid typing it in full for
every query. Also, you must specify JSON with the on() option when you create the index.

The code below shows these differences, but the index is otherwise very similar to
the one created previously for hashes:

[code example]

Use jsonset() to add the data
instead of hmset(). The arrays
that specify the fields have roughly the same structure as the ones used for
 hmset() but you should use the standard library function
 json_encode() 
to generate a JSON string representation of the array.

An important difference with JSON indexing is that the vectors are
specified using arrays instead of binary strings. Add the
embedding as an array field without using the pack() function as you
would with a hash.

[code example]

The query is almost identical to the one for the hash documents. This
demonstrates how the right choice of aliases for the JSON paths can
save you having to write complex queries. An important thing to notice
is that the vector parameter for the query is still specified as a
binary string (using the pack() function), even though the data for
the embedding field of the JSON was specified as an array.

[code example]

Apart from the jdoc: prefixes for the keys, the result from the JSON
query is the same as for hash:

[code example]

## Learn more

See
Vector search
for more information about the indexing options, distance metrics, and query format
for vectors.