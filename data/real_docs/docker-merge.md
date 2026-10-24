These rules are outlined below. 

## Mapping

A YAML mapping gets merged by adding missing entries and merging the conflicting ones.

Merging the following example YAML trees:

[code example]

[code example]

Results in a Compose application model equivalent to the YAML tree:

[code example]

## Sequence

A YAML sequence is merged by appending values from the overriding Compose file to the previous one.

Merging the following example YAML trees:

[code example]

[code example]

Results in a Compose application model equivalent to the YAML tree:

[code example]

## Exceptions

### Shell commands

When merging Compose files that use the services attributes command, entrypoint and healthcheck: test , the value is overridden by the latest Compose file, and not appended.

Merging the following example YAML trees:

[code example]

[code example]

Results in a Compose application model equivalent to the YAML tree:

[code example]

### Unique resources

Applies to the ports, volumes, secrets and configs services attributes.
While these types are modeled in a Compose file as a sequence, they have special uniqueness requirements:

| Attribute | Unique key |
|-------------|--------------------------|
| volumes | target |
| secrets | target |
| configs | target |
| ports | {ip, target, published, protocol} |

When merging Compose files, Compose appends new entries that do not violate a uniqueness constraint and merge entries that share a unique key.

Merging the following example YAML trees:

[code example]

[code example]

Results in a Compose application model equivalent to the YAML tree:

[code example]

### Reset value

In addition to the previously described mechanism, an override Compose file can also be used to remove elements from your application model.
For this purpose, the custom YAML tag !reset can be set to
override a value set by the overridden Compose file. A valid value for attribute must be provided,
but will be ignored and target attribute will be set with type's default value or null . 

For readability, it is recommended to explicitly set the attribute value to the null ( null ) or empty
array [] (with !reset null or !reset [] ) so that it is clear that resulting attribute will be
cleared.

A base compose.yaml file:

[code example]

And a compose.override.yaml file:

[code example]

Results in:

[code example]

### Replace value

While !reset can be used to remove a declaration from a Compose file using an override file, !override allows you
to fully replace an attribute, bypassing the standard merge rules. A typical example is to fully replace a resource definition, to rely on a distinct model but using the same name.

A base compose.yaml file:

[code example]

To remove the original port, but expose a new one, the following override file is used:

[code example]

This results in: 

[code example]

If !override had not been used, both 8080:80 and 8443:443 would be exposed as per the merging rules outlined above. 

## Additional resources

For more information on how merge can be used to create a composite Compose file, see Working with multiple Compose files