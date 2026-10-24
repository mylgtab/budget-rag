Annotations provide descriptive metadata for images. Use annotations to record
arbitrary information and attach it to your image, which helps consumers and
tools understand the origin, contents, and how to use the image.

Annotations are similar to, and in some sense overlap with, [labels]. Both
serve the same purpose: to attach metadata to a resource. As a general principle,
you can think of the difference between annotations and labels as follows:

- Annotations describe OCI image components, such as [manifests], [indexes],
 and [descriptors].
- Labels describe Docker resources, such as images, containers, networks, and
 volumes.

The OCI image [specification] defines the format of annotations, as well as a set
of pre-defined annotation keys. Adhering to the specified standards ensures
that metadata about images can be surfaced automatically and consistently, by
tools like Docker Scout.

Annotations are not to be confused with [attestations]:

- Attestations contain information about how an image was built and what it contains.
 An attestation is attached as a separate manifest on the image index.
 Attestations are not standardized by the Open Container Initiative.
- Annotations contain arbitrary metadata about an image.
 Annotations attach to the image [config] as labels,
 or on the image index or manifest as properties.

## Add annotations

You can add annotations to an image at build-time, or when creating the image
manifest or index.

> [!NOTE]
>
> The Docker Engine image store doesn't support loading images with
> annotations. To build with annotations, make sure to push the image directly
> to a registry, using the --push CLI flag or the
> registry exporter.

To specify annotations on the command line, use the --annotation flag for the
 docker build command:

[code example]

If you're using Bake, you can use the annotations 
attribute to specify annotations for a given target:

[code example]

For examples on how to add annotations to images built with GitHub Actions, see
Add image annotations with GitHub Actions

You can also add annotations to an image created using
 docker buildx imagetools create . This command only supports adding annotations to an index
or manifest descriptors, see
CLI reference.

## Inspect annotations

To view annotations on an image index , use the
 docker buildx imagetools inspect command. This shows you any annotations for
the index and descriptors
(references to manifests) that the index contains. The following example shows
an org.opencontainers.image.documentation annotation on a descriptor, and an
 org.opencontainers.image.authors annotation on the index.

[code example]

To inspect annotations on a manifest, use the
 docker buildx imagetools inspect command and specify @ ,
where is the digest
of the manifest:

[code example]

## Specify annotation level

By default, annotations are added to the image manifest. You can specify which
level (OCI image component) to attach the annotation to by prefixing the
annotation string with a special type declaration:

[code example]

The following types are supported:

- manifest : annotates manifests.
- index : annotates the root index.
- manifest-descriptor : annotates manifest descriptors in the index.
- index-descriptor : annotates the index descriptor in the image layout.

For example, to build an image with the annotation foo=bar attached to the
image index:

[code example]

Note that the build must produce the component that you specify, or else the
build will fail. For example, the following does not work, because the docker 
exporter does not produce an index:

[code example]

Likewise, the following example also does not work, because Buildx creates a
 docker output by default under some circumstances, such as when provenance
attestations are explicitly disabled:

[code example]

It is possible to specify types, separated by a comma, to add the annotation to
more than one level. The following example creates an image with the annotation
 foo=bar on both the image index and the image manifest:

[code example]

You can also specify a platform qualifier within square brackets in the type
prefix, to annotate only components matching specific OS and architectures. The
following example adds the foo=bar annotation only to the linux/amd64 
manifest:

[code example]

## Related information

Related articles:

- Add image annotations with GitHub Actions
- [Annotations OCI specification][specification]

Reference information:

- docker buildx build --annotation 
- Bake file reference: annotations 
- docker buildx imagetools create --annotation 

[specification]: https://github.com/opencontainers/image-spec/blob/main/annotations.md
[attestations]: /manuals/build/metadata/attestations/_index.md
[config]: https://github.com/opencontainers/image-spec/blob/main/config.md
[descriptors]: https://github.com/opencontainers/image-spec/blob/main/descriptor.md
[indexes]: https://github.com/opencontainers/image-spec/blob/main/image-index.md
[labels]: /manuals/engine/manage-resources/labels.md
[manifests]: https://github.com/opencontainers/image-spec/blob/main/manifest.md