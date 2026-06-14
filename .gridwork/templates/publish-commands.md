# Publish Commands

These commands are prepared only. They must not be executed without explicit human approval.

```bash
git tag factory-v<version>
git push origin factory-v<version>
gh release create factory-v<version> gridwork-factory-v<version>.zip gridwork-factory-v<version>.manifest.json gridwork-factory-v<version>.sha256 gridwork-factory-v<version>.release-notes.md --repo <owner/repo> --notes-file gridwork-factory-v<version>.release-notes.md
gh release view factory-v<version> --repo <owner/repo>
```
