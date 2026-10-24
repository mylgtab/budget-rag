A target in a Bake file represents a build invocation. It holds all the
information you would normally pass to a docker build command using flags.

[code example]

To build a target with Bake, pass name of the target to the bake command.

[code example]

You can build multiple targets at once by passing multiple target names to the
 bake command.

[code example]

## Default target

If you don't specify a target when running docker buildx bake , Bake will
build the target named default .

[code example]

To build this target, run docker buildx bake without any arguments:

[code example]

## Target properties

The properties you can set for a target closely resemble the CLI flags for
 docker build , with a few additional properties that are specific to Bake.

The dockerfile property specifies the path to the Dockerfile for a target.
If you also set a context , the dockerfile path resolves relative to that
context.

[code example]

For all the properties you can set for a target, see the Bake reference.

## Grouping targets

You can group targets together using the group block. This is useful when you
want to build multiple targets at once.

[code example]

To build all the targets in a group, pass the name of the group to the bake 
command.

[code example]

## Pattern matching for targets and groups

Bake supports shell-style wildcard patterns when specifying target or grouped targets.
This makes it easier to build multiple targets without listing each one explicitly.

Supported patterns:

- * matches any sequence of characters
- ? matches any single character
- [abc] matches any character in brackets

> [!NOTE]
>
> Always wrap wildcard patterns in quotes. Without quotes, your shell will expand the
> wildcard to match files in the current directory, causing errors.

Examples:

[code example]

You can also combine multiple patterns:

[code example]

## Additional resources

Refer to the following pages to learn more about Bake's features:

- Learn how to use variables in Bake to make your build
 configuration more flexible.
- Learn how you can use matrices to build multiple images with different
 configurations in Matrices.
- Head to the Bake file reference to learn about all
 the properties you can set in a Bake file, and its syntax.