# Dockerfile Authoring Skill

## Purpose

Create or review Dockerfiles that are reproducible, secure, small enough and efficient to build.

## Procedure

1. Confirm service path, runtime, build commands and deployment target.
2. Inspect existing Dockerfiles and `.dockerignore`.
3. Separate dependency restore, build, test and runtime concerns.
4. Design multi-stage builds when they reduce runtime contents or improve repeatability.
5. Order copy/install steps for useful cache reuse.
6. Remove build tools and source files from the final image unless required.
7. Run as a non-root user where the application supports it.
8. Define runtime command, signals, ports and writable paths explicitly.
9. Validate build, startup, shutdown and image contents using approved commands.

## Security And Reproducibility

- Use approved and pinned base image versions; do not use `latest`.
- Never bake secrets, tokens or real environment files into layers.
- Keep package-manager lockfiles and deterministic install modes.
- Use `.dockerignore` to exclude VCS, dependencies, artifacts and secrets.
- Prefer BuildKit secret/cache mounts only when supported and approved.
- Minimize installed OS packages and clean package metadata in the same layer.
- Make architecture/platform requirements explicit when relevant.

## Stack Notes

- Next.js: choose standalone/runtime output only if project configuration supports it.
- Spring Boot: copy the built artifact into a minimal runtime stage; preserve JVM signal handling.
- Do not run a database inside an application image.

## Forbidden

- Gridwork `init` does not create Dockerfiles.
- Do not write infra files without an approved work order and confirmed path.
- Do not add curl-based healthchecks merely to install curl.
- Do not optimize image size at the cost of debuggability or correctness without evidence.
