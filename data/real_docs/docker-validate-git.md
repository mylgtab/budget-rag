Git repositories often appear in Docker builds as source code inputs. The ADD 
instruction can clone repositories, and build contexts can reference Git URLs.
Validating these inputs ensures you're building from trusted sources with
verified versions.

This guide teaches you to write policies that validate Git inputs, from basic
version pinning to verifying signed commits and tags.

## Prerequisites

You should understand the policy basics from the Introduction:
creating policy files, basic Rego syntax, and how policies evaluate during
builds.

## What are Git inputs?

Git inputs come from ADD instructions that reference Git repositories:

[code example]

The build context can also be a Git repository when you build with:

[code example]

Each Git reference triggers a policy evaluation. Your policy can inspect
repository URLs, validate versions, check commit metadata, and verify
signatures.

## Match specific repositories

The simplest Git policy restricts which repositories can be used:

[code example]

This policy:

- Denies all inputs by default
- Allows local build context
- Allows only the BuildKit repository from GitHub

The host field contains the Git server hostname, and remote contains the
full repository URL. Test it:

[code example]

[code example]

The build succeeds. Try a different repository and it fails.

You can match multiple repositories with additional rules:

[code example]

## Pin to specific versions

Tags and branches can change over time. Pin to specific versions to ensure
reproducible builds:

[code example]

The tagName field contains the tag name when the Git reference points to a
tag. Use branch for branches:

[code example]

Or use ref for any type of reference (branch, tag, or commit SHA):

[code example]

## Use version allowlists

For repositories you trust but want to control versions, maintain an allowlist:

[code example]

This policy:

- Defines an allowlist of approved versions with metadata
- Uses a helper rule ( is_buildkit ) for readability
- Allows all non-BuildKit inputs
- For BuildKit, checks the tag name, whether it's an annotated tag, and the commit SHA against the allowlist

The helper rule makes complex policies more maintainable. You can expand the
allowlist as new versions are approved:

[code example]

## Validate with regex patterns

Use pattern matching for semantic versioning:

[code example]

This allows any BuildKit tag matching the pattern vX.Y.Z where X, Y, and Z
are numbers. The regex ensures you're using release versions, not pre-release
tags like v0.26.0-rc1 .

Match major versions:

[code example]

## Inspect commit metadata

The commit object provides detailed information about commits:

[code example]

The commit object includes:

- author.name : Author's name
- author.email : Author's email
- author.when : When the commit was authored
- committer.name : Committer's name
- committer.email : Committer's email
- committer.when : When the commit was committed
- message : Commit message

Validate commit messages:

[code example]

Pin to specific commit SHA:

[code example]

## Require signed commits

GPG-signed commits prove authenticity. Check for commit signatures:

[code example]

The pgpSignature field is null for unsigned commits. For signed commits, it
contains signature details.

SSH signatures work similarly:

[code example]

## Require signed tags

Annotated tags can be signed, providing a cryptographic guarantee of the
release:

[code example]

The tag object is only available for annotated tags. It includes:

- tagger.name : Who created the tag
- tagger.email : Tagger's email
- tagger.when : When the tag was created
- message : Tag message
- pgpSignature : GPP signature (if signed)
- sshSignature : SSH signature (if signed)

Lightweight tags don't have a tag object, so this policy effectively requires
annotated, signed tags.

## Verify signatures with public keys

Use the verify_git_signature() function to cryptographically verify Git
signatures against trusted public keys:

[code example]

This verifies that Git tags are signed by keys in the keys.asc public
key file. To set this up:

1. Export maintainer public keys:
 [code example]
2. Place keys.asc alongside your policy file

The function verifies PGP signatures on commits or tags. See Built-in
functions for more details.

## Apply conditional rules

Use different rules for different contexts. Allow unsigned refs during
development but require signing for production:

[code example]

This policy:

- Defines helper rules for readability
- Requires signed version tags from maintainers
- Allows unsigned refs (branches, commits) unless building the release target
- Uses input.env.target to detect the build target

Build a development target without signatures:

[code example]

Build the release target, and signing is enforced:

[code example]

## Next steps

You now understand how to validate Git repositories in build policies. To
continue learning:

- Browse Example policies for complete policy patterns
- Read Built-in functions for Git signature verification
 functions
- Check the Input reference for all available Git fields