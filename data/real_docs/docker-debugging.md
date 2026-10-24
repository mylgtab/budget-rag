When policies don't work as expected, use the tools available to inspect policy
evaluation and understand what's happening. This guide covers the debugging
techniques and common gotchas.

## Quick reference

Essential debugging commands:

[code example]

## Policy output with --progress=plain 

To see policy evaluation during builds, use --progress=plain :

[code example]

This shows all policy checks, decisions, and print() output. Without
 --progress=plain , policy evaluation is silent unless there's an error.

[code example]

If a policy denies a source, you'll see:

[code example]

## Debug logging

For detailed debugging, add --policy log-level=debug to see the full input
JSON, unresolved fields, and policy responses:

[code example]

This shows significantly more information than the default level, including the
complete input structure for each source without needing print() statements
in your policy.

Complete input JSON:

[code example]

Unresolved fields:

[code example]

Policy response:

[code example]

This detailed output is invaluable for understanding exactly what data your
policy receives and which fields are not yet resolved. Use debug logging when
developing policies to avoid needing extensive print() statements.

## Conditional debugging with print()

While --policy log-level=debug shows all input data automatically, the
 print() function is useful for debugging specific rule logic and conditional
flows:

[code example]

Use print() to debug conditional logic within rules or track which rules are
evaluating. For general input inspection during development, use --policy
log-level=debug instead - it requires no policy modifications.

> [!NOTE]
> Print statements only execute when their containing rule evaluates. A rule
> like allow if { input.image; print(...) } only prints for image inputs,
> not for Git repos, HTTP downloads, or local files.

## Common issues

### Full repository path or repository name

Symptom: Policy checking repository names doesn't match as expected.

Cause: Docker Hub images use input.image.repo for the short name
( "alpine" ) but input.image.fullRepo includes the full path
( "docker.io/library/alpine" ).

Solution:

[code example]

### Policy evaluation happens multiple times

Symptom: Build output shows the same source evaluated multiple times.

Cause: BuildKit may evaluate policies at different stages (reference
resolution, actual pull) or for different platforms.

This is normal behavior. Policies should be idempotent (produce same result
each time for the same input).

### Fields missing with policy eval --print 

Symptom: docker buildx policy eval --print doesn't show expected fields
like hasProvenance , labels , or checksum .

Cause: --print shows only reference information by default, without
fetching from registries.

Solution: Use --fields to fetch specific metadata fields:

[code example]

See Using build policies for
details.

## Next steps

- See complete field reference: Input reference
- Review example policies: Examples
- Learn policy usage patterns: Using build policies