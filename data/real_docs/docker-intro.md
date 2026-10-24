Build policies let you validate the inputs to your Docker builds before they
run. This tutorial walks you through creating your first policy, teaching the
Rego basics you need along the way.

## What you'll learn

By the end of this tutorial, you'll understand:

- How to create and organize policy files
- Basic Rego syntax and patterns
- How to write policies that validate URLs, checksums, and images
- How policies evaluate during builds

## Prerequisites

- Buildx version 0.31 or later
- Basic familiarity with Dockerfiles and building images

## How policies work

When you build an image, Buildx resolves all the inputs your
Dockerfile references: base images from FROM instructions, files
from ADD or COPY or build contexts, and Git repositories. Before
running the build, Buildx evaluates your policies against these
inputs. If any input violates a policy, the build fails before any
instructions execute.

Policies are written in Rego, a declarative language designed for expressing
rules and constraints. You don't need to know Rego to get started - this
tutorial teaches you what you need.

## Create your first policy

Create a new directory for this tutorial and add a Dockerfile:

[code example]

Create a Dockerfile that downloads a file with ADD :

[code example]

Now create a policy file. Policies use the .rego extension and live alongside
your Dockerfile. Create Dockerfile.rego :

[code example]

Save this file as Dockerfile.rego in the same directory as your Dockerfile.

Let's break down what this policy does:

- package docker - All build policies must start with this package declaration
- default allow := false - This example uses a deny-by-default rule: if inputs do not match an allow rule, the policy check fails
- allow if input.local - The first rule allows any local files (your build context)
- allow if { input.http.host == "example.com" } - The second rule allows HTTP downloads from example.com 
- decision := {"allow": allow} - The final decision object tells Buildx whether to allow or deny the input

This policy says: "Only allow local files and HTTP downloads from
 example.com ". Rego evaluates all the policy rules to figure out the return
value for the decision variable, for each build input. The evaluations happen
in parallel and on-demand; the order of the policy rules has no significance.

### About input.local 

You'll see allow if input.local in nearly every policy. This rule allows
local file access, which includes your build context (typically, the . 
directory) and importantly, the Dockerfile itself. Without this rule, Buildx
can't read your Dockerfile to start the build.

Even builds that don't reference any files from the build context often need
 input.local because the Dockerfile is a local file. The policy evaluates
before the build starts, and denying local access means denying access to the
Dockerfile.

In rare cases, you might want stricter local file policies - for example, in CI
builds where the build context uses a Git URL as a context directly. In these
cases, you may want to deny local sources to prevent untracked files or changes
from making their way into your build.

## Automatic policy loading

Buildx automatically loads policies that match your Dockerfile name. When you
build with Dockerfile , Buildx looks for Dockerfile.rego in the same
directory. For a file named app.Dockerfile , it looks for
 app.Dockerfile.rego .

This automatic loading means you don't need any command-line flags in most
cases - create the policy file and build.

The policy file must be in the same directory as the Dockerfile. If Buildx
can't find a matching policy, the build proceeds without policy evaluation
(unless you use --policy strict=true ).

For more control over policy loading, see the Usage guide.

## Run a build with your policy

Build the image with policy evaluation enabled:

[code example]

The build succeeds because the URL in your Dockerfile matches the policy. Now
try changing the URL in your Dockerfile to something else:

[code example]

Build again:

[code example]

This time the build fails with a policy violation. The api.github.com 
hostname doesn't match the rule in your policy, so Buildx rejects it before
running any build steps.

## Debugging policy failures

If your build fails with a policy violation, use --progress=plain to see
exactly what went wrong:

[code example]

This shows all policy checks, the input data for each source, and allow/deny
decisions. For complete debugging guidance, see Debugging.

## Add helpful error messages

When a policy denies an input, users see a generic error message. You can
provide custom messages that explain why the build was denied:

[code example]

Now when a build is denied, users see your custom message explaining what went
wrong:

[code example]

The deny_msg rule uses contains to add messages to a set. You can add
multiple deny messages for different failure conditions to help users understand
exactly what needs to change.

## Understand Rego rules

Rego policies are built from rules. A rule defines when something is allowed.
The basic pattern is:

[code example]

All conditions must be true for the rule to match. Think of it as an AND
operation - the URL must match AND the checksum must match AND any other
conditions you specify.

You can have multiple allow rules in one policy. If any rule matches, the
input is allowed:

[code example]

This works like OR - the input can match the first rule OR the second rule.

## Access input fields

The input object gives you access to information about build inputs. The
structure depends on the input type:

- input.http - Files downloaded with ADD https://... 
- input.image - Container images from FROM or COPY --from 
- input.git - Git repositories from ADD git://... or build context
- input.local - Local file context

Refer to the Input reference for all available input fields.

For HTTP downloads, you can access:

| Key | Description | Example |
| ------------------- | ---------------------------------- | -------------------------------- |
| input.http.url | The full URL | https://example.com/index.html |
| input.http.schema | The protocol (HTTP/HTTPS) | https |
| input.http.host | The hostname | example.com |
| input.http.path | The URL path, including parameters | /index.html |

Update your policy to require HTTPS:

[code example]

Now the policy requires both the hostname to be example.com and the protocol
to be HTTPS. HTTP URLs (without TLS) would fail the policy check.

## Pattern matching and strings

Rego provides [built-in functions] for pattern matching. Use startswith() to
match URL prefixes:

[built-in functions]: https://www.openpolicyagent.org/docs/policy-language#built-in-functions

[code example]

This allows any URL that starts with https://example.com/ .

Use regex.match() for complex patterns:

[code example]

This matches URLs that:

- Start with https://example.com/ 
- End with .json 
- Have at least one character between the domain and extension

## Policy file location

Policy files live adjacent to the Dockerfile they validate, using the naming
pattern .rego :

[code example]

When you build, Buildx automatically loads the corresponding policy file:

[code example]

## Next steps

You now understand how to write basic build policies for HTTP resources. To
continue learning:

- Apply and test policies: Using build policies
- Learn Image validation to validate container images
 from FROM instructions
- Learn Git validation to validate Git repositories used
 in builds
- See Example policies for copy-paste-ready policies covering
 common scenarios
- Write unit tests for your policies: Test build policies
- Debug policy failures: Debugging
- Read the Input reference for all available input fields
- Check the Built-in functions for signature verification,
 attestations, and other security checks