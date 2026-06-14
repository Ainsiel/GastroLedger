# CLI Release Plan

```text
package_name = <package>
version = <version>
tag = cli-v<version>
dist_tag = <latest|next>
source = <owner/repo>
source_commit = <sha>
publish = not_executed
```

## Approval Gate

Creating or pushing `cli-v<version>` requires explicit human approval.

npm publish is performed only by GitHub Actions after an approved tag.
