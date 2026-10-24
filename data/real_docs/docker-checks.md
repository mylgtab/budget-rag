Build checks are a feature introduced in Dockerfile 1.8. It lets you validate
your build configuration and conduct a series of checks prior to executing your
build. Think of it as an advanced form of linting for your Dockerfile and build
options, or a dry-run mode for builds.

You can find the list of checks available, and a description of each, in the
Build checks reference.

## How build checks work

Typically, when you run a build, Docker executes the build steps in your
Dockerfile and build options as specified. With build checks, rather than
executing the build steps, Docker checks the Dockerfile and options you provide
and reports any issues it detects.

Build checks are useful for:

- Validating your Dockerfile and build options before running a build.
- Ensuring that your Dockerfile and build options are up-to-date with the
 latest best practices.
- Identifying potential issues or anti-patterns in your Dockerfile and build
 options.

> [!TIP]
>
> To improve linting, code navigation, and vulnerability scanning of your Dockerfiles in Visual Studio Code
> see the Docker DX extension.

## Build with checks

Build checks are supported in:

- Buildx version 0.15.0 and later
- docker/build-push-action version 6.6.0 and later
- docker/bake-action version 5.6.0 and later

Invoking a build runs the checks by default, and displays any violations in the
build output. For example, the following command both builds the image and runs
the checks:

[code example]

In this example, the build ran successfully, but a
JSONArgsRecommended warning
was reported, because CMD instructions should use JSON array syntax.

With the GitHub Actions, the checks display in the diff view of pull requests.

[code example]

### More verbose output

Check warnings for a regular docker build display a concise message
containing the rule name, the message, and the line number of where in the
Dockerfile the issue originated. If you want to see more detailed information
about the checks, you can use the --debug flag. For example:

[code example]

With the --debug flag, the output includes a link to the documentation for
the check, and a snippet of the Dockerfile where the issue was found.

## Check a build without building

To run build checks without actually building, you can use the docker build 
command as you typically would, but with the addition of the --check flag.
Here's an example:

[code example]

Instead of executing the build steps, this command only runs the checks and
reports any issues it finds. If there are any issues, they will be reported in
the output. For example:

[code example]

This output with --check shows the verbose message
for the check.

Unlike a regular build, if any violations are reported when using the --check 
flag, the command exits with a non-zero status code.

## Fail build on check violations

Check violations for builds are reported as warnings, with exit code 0, by
default. You can configure Docker to fail the build when violations are
reported, using a check=error=true directive in your Dockerfile. This will
cause the build to error out when after the build checks are run, before the
actual build gets executed.

[code example]

Without the # check=error=true directive, this build would complete with an
exit code of 0. However, with the directive, build check violation results in
non-zero exit code:

[code example]

You can also set the error directive on the CLI by passing the
 BUILDKIT_DOCKERFILE_CHECK build argument:

[code example]

## Skip checks

By default, all checks are run when you build an image. If you want to skip
specific checks, you can use the check=skip directive in your Dockerfile.
The skip parameter takes a CSV string of the check IDs you want to skip.
For example:

[code example]

Building this Dockerfile results in no check violations.

You can also skip checks by passing the BUILDKIT_DOCKERFILE_CHECK build
argument with a CSV string of check IDs you want to skip. For example:

[code example]

To skip all checks, use the skip=all parameter:

[code example]

## Combine error and skip parameters for check directives

To both skip specific checks and error on check violations, pass both the
 skip and error parameters separated by a semi-colon ( ; ) to the check 
directive in your Dockerfile or in a build argument. For example:

[code example]

[code example]

## Experimental checks

Before checks are promoted to stable, they may be available as experimental
checks. Experimental checks are disabled by default. To see the list of
experimental checks available, refer to the Build checks reference.

To enable all experimental checks, set the BUILDKIT_DOCKERFILE_CHECK build
argument to experimental=all :

[code example]

You can also enable experimental checks in your Dockerfile using the check 
directive:

[code example]

To selectively enable experimental checks, you can pass a CSV string of the
check IDs you want to enable, either to the check directive in your Dockerfile
or as a build argument. For example:

[code example]

Note that the experimental directive takes precedence over the skip 
directive, meaning that experimental checks will run regardless of the skip 
directive you have set. For example, if you set skip=all and enable
experimental checks, the experimental checks will still run:

[code example]

## Further reading

For more information about using build checks, see:

- Build checks reference
- Validating build configuration with GitHub Actions