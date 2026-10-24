You can build Bake files directly from a remote Git repository or HTTPS URL:

[code example]

This fetches the Bake definition from the specified remote location and
executes the groups or targets defined in that file. If the remote Bake
definition doesn't specify a build context, the context is automatically set to
the Git remote. For example, this case
uses https://github.com/docker/cli.git :

[code example]

## Use the local context with a remote definition

When building with a remote Bake definition, you may want to consume local
files relative to the directory where the Bake command is executed. You can
define contexts as relative to the command context using a cwd:// prefix.

[code example]

You can append a path to the cwd:// prefix if you want to use a specific
local directory as a context. Note that if you do specify a path, it must be
within the working directory where the command gets executed. If you use an
absolute path, or a relative path leading outside of the working directory,
Bake will throw an error.

### Local named contexts

You can also use the cwd:// prefix to define local directories in the Bake
execution context as named contexts.

The following example defines the docs context as ./src/docs/content ,
relative to the current working directory where Bake is run as a named context.

[code example]

By contrast, if you omit the cwd:// prefix, the path would be resolved
relative to the build context.

## Specify the Bake definition to use

When loading a Bake file from a remote Git repository, if the repository
contains more than one Bake file, you can specify which Bake definition to use
with the --file or -f flag:

[code example]

[code example]

## Combine local and remote Bake definitions

You can also combine remote definitions with local ones using the cwd:// 
prefix with -f .

Given the following local Bake definition in the current working directory:

[code example]

The following example uses -f to specify two Bake definitions:

- -f bake.hcl : this definition is loaded relative to the Git URL.
- -f cwd://local.hcl : this definition is loaded relative to the current
 working directory where the Bake command is executed.

[code example]

[code example]

One case where combining local and remote Bake definitions becomes necessary is
when you're building with a remote Bake definition in GitHub Actions and want
to use the metadata-action to
generate tags, annotations, or labels. The metadata action generates a Bake
file available in the runner's local Bake execution context. To use both the
remote definition and the local "metadata-only" Bake file, specify both files
and use the cwd:// prefix for the metadata Bake file:

[code example]

## Remote definition in a private repository

If you want to use a remote definition that lives in a private repository,
you may need to specify credentials for Bake to use when fetching the definition.

If you can authenticate to the private repository using the default SSH_AUTH_SOCK ,
then you don't need to specify any additional authentication parameters for Bake.
Bake automatically uses your default agent socket.

For authentication using an HTTP token, or custom SSH agents,
use the following environment variables to configure Bake's authentication strategy:

- BUILDX_BAKE_GIT_AUTH_TOKEN 
- BUILDX_BAKE_GIT_AUTH_HEADER 
- BUILDX_BAKE_GIT_SSH