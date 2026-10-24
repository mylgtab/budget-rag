The image exporter outputs the build result into a container image format. The
 registry exporter is identical, but it automatically pushes the result by
setting push=true .

## Synopsis

Build a container image using the image and registry exporters:

[code example]

The following table describes the available parameters that you can pass to
 --output for type=image :

| Parameter | Type | Default | Description |
| ---------------------- | -------------------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| name | String | | Image name. To specify multiple names, use a comma-separated list. |
| push | true , false | false | Push after creating the image. |
| push-by-digest | true , false | false | Push image without name. |
| registry.insecure | true , false | false | Allow pushing to insecure registry. |
| dangling-name-prefix | | | Name image with prefix@ , used for anonymous images |
| name-canonical | true , false | | Add additional canonical name name@ |
| compression | uncompressed , gzip , estargz , zstd | gzip | Compression type, see [compression][1] |
| compression-level | 0..22 | | Compression level, see [compression][1] |
| force-compression | true , false | false | Forcefully apply compression, see [compression][1] |
| rewrite-timestamp | true , false | false | Rewrite the file timestamps to the SOURCE_DATE_EPOCH value. See [build reproducibility][4] for how to specify the SOURCE_DATE_EPOCH value. |
| oci-mediatypes | true , false | false | Use OCI media types in exporter manifests, see [OCI Media types][2] |
| oci-artifact | true , false | false | Attestations are formatted as OCI artifacts, see [OCI Media types][2] |
| unpack | true , false | false | Unpack image after creation (for use with containerd) |
| store | true , false | true | Store the result images to the worker's (for example, containerd) image store, and ensures that the image has all blobs in the content store. Ignored if the worker doesn't have image store (when using OCI workers, for example). |
| annotation. | String | | Attach an annotation with the respective key and value to the built image,see [annotations][3] |

[1]: _index.md#compression
[2]: _index.md#oci-media-types
[3]: #annotations
[4]: https://github.com/moby/buildkit/blob/master/docs/build-repro.md
[5]: /manuals/build/metadata/attestations/_index.md#attestations-as-oci-artifacts

The name parameter is a CSV value inside the --output value. To specify
multiple image names, quote the complete name field:

[code example]

To assign multiple names with CLI flags instead, repeat the
 --tag flag.

## Annotations

These exporters support adding OCI annotation using annotation parameter,
followed by the annotation name using dot notation. The following example sets
the org.opencontainers.image.title annotation:

[code example]

For more information about annotations, see
BuildKit documentation.

## Further reading

For more information on the image or registry exporters, see the
BuildKit README.