The local and tar exporters output the root filesystem of the build result
into a local directory. They're useful for producing artifacts that aren't
container images.

- local exports files and directories.
- tar exports the same, but bundles the export into a tarball.

## Synopsis

Build a container image using the local exporter:

[code example]

The following table describes the available parameters:

| Parameter | Type | Default | Description |
| ---------------- | ------- | ------- | --------------------------------------------------------------------------------- |
| dest | String | | Path to copy files to |
| platform-split | Boolean | true | local exporter only. Split multi-platform outputs into platform subdirectories. |

## Multi-platform builds with local exporter

The platform-split parameter controls how multi-platform build outputs are
organized.

Consider this Dockerfile that creates platform-specific files:

[code example]

### Split by platform (default)

By default, the local exporter creates a separate subdirectory for each
platform:

[code example]

This produces the following directory structure:

[code example]

### Merge all platforms

To merge files from all platforms into the same directory, set
 platform-split=false :

[code example]

This produces a flat directory structure:

[code example]

Files from all platforms merge into a single directory. If multiple platforms
produce files with identical names, the export fails with an error.

### Single-platform builds

Single-platform builds export directly to the destination directory without
creating a platform subdirectory:

[code example]

This produces:

[code example]

To include the platform subdirectory even for single-platform builds, explicitly
set platform-split=true :

[code example]

This produces:

[code example]

## Further reading

For more information on the local or tar exporters, see the
BuildKit README.