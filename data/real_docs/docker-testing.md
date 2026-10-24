The docker buildx policy test 
command runs unit tests for build policies using OPA's standard test
framework.

[code example]

This validates policy logic with mocked inputs.

For testing against real sources (actual image metadata, Git repositories), use
 docker buildx policy eval 
instead. You can use the eval --print option to resolve input for a specific
source for writing a test case.

## Basic example

Start with a simple policy that only allows alpine images:

[code example]

Create a test file with the *_test.rego suffix. Test functions must start
with test_ :

[code example]

Run the tests:

[code example]

 PASS indicates that the tests defined in Dockerfile_test.rego executed
successfully and all assertions were satisfied.

## Command options

Filter tests by name with --run :

[code example]

Test policies with non-default filenames using --filename :

[code example]

This loads app.Dockerfile.rego and runs *_test.rego files against it.

## Test output

Passed tests show the allow status and any deny messages:

[code example]

Failed tests show input, decision output, and missing fields:

[code example]

## Test deny messages

To test custom error messages, capture the full decision result and assert on
the deny_msg field.

For a policy with deny messages:

[code example]

Test the deny message:

[code example]

## Test patterns

 Test environment-specific rules: 

[code example]

 Test multiple registries: 

[code example]

For available input fields, see the Input reference.

## Organize test files

The test runner discovers all *_test.rego files recursively:

[code example]

Run all tests:

[code example]

Or test specific files:

[code example]