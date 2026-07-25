---
name: Bug report
about: Report a problem with a template, workflow, or guide
title: "[Bug]: "
labels: bug, triage
assignees: ""
---

**Describe the bug**
A clear description of what failed or behaved unexpectedly.

**Affected cloud/provider**
- [ ] AWS
- [ ] Azure
- [ ] GCP
- [ ] OCI
- [ ] GitHub workflow
- [ ] Documentation

**Affected file or template**
For example: `gcp/codebuild-prowler-gcp.yaml`.

**To reproduce**
Steps or command used. Do not include credentials, service account keys, account IDs that should remain private, or secrets.

```bash
# command or sanitized excerpt
```

**Expected behavior**
What you expected to happen.

**Observed behavior**
Error output, CloudFormation event, CodeBuild phase failure, or relevant log excerpt. Redact sensitive values.

**Environment**
- Region:
- Prowler version:
- Deployment method: CloudFormation console, AWS CLI, CloudShell, other
- Template parameters changed from defaults:

**Additional context**
Any other context that helps narrow the issue.
