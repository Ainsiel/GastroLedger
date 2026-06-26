# Docker Compose Guidance

Docker Compose is recommended for local development when the project uses PostgreSQL.

`gridwork init` does not generate Compose files. An approved `repository-bootstrap` plan or implementation work order may create or modify a confirmed Compose path.

Review existing compose files for:

- PostgreSQL service healthchecks;
- environment examples without secrets;
- migration flow;
- network and port clarity;
- dev/prod separation.
- pinned images;
- minimal exposed ports;
- explicit profiles and volume lifecycle;
- reproducible build contexts;
- startup, restart and shutdown behavior.
