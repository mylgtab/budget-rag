Bake files in the HCL format support expression evaluation, which lets you
perform arithmetic operations, conditionally set values, and more.

## Arithmetic operations

You can perform arithmetic operations in expressions. The following example
shows how to multiply two numbers.

[code example]

Printing the Bake file with the --print flag shows the evaluated value for
the answer build argument.

[code example]

[code example]

## Ternary operators

You can use ternary operators to conditionally register a value.

The following example adds a tag only when a variable is not empty, using the
built-in notequal function.

[code example]

In this case, TAG is an empty string, so the resulting build configuration
only contains the hard-coded my-image:latest tag.

[code example]

[code example]

## Expressions with variables

You can use expressions with variables to conditionally set
values, or to perform arithmetic operations.

The following example uses expressions to set values based on the value of
variables. The v1 build argument is set to "higher" if the variable FOO is
greater than 5, otherwise it is set to "lower". The v2 build argument is set
to "yes" if the IS_FOO variable is true, otherwise it is set to "no".

[code example]

Printing the Bake file with the --print flag shows the evaluated values for
the v1 and v2 build arguments.

[code example]

[code example]