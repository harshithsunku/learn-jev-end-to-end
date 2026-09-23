# Deploys and rollbacks

## Deploying
Every push to the main branch creates an immutable release. Releases are rolled out gradually: 5% of traffic, then 25%, then 100%.

## Rolling back
To roll back, open Deploys, select the last healthy release, and click Promote. You can also run `acme deploy rollback --to <release-id>` from the CLI. Rollbacks take effect in under a minute because releases are immutable.

## Deploy freezes
Organization owners can set a deploy freeze to block releases during critical periods.
