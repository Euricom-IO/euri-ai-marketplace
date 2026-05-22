# Plugin `source` types

Five ways to point a marketplace entry at a plugin. Pick one per entry.

## 1. Relative path (same repo)

```json
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin"
}
```

- **Must start with `./`**. No `../` (path traversal is rejected).
- Resolved relative to the **marketplace root** (the directory
  containing `.claude-plugin/`), not the `.claude-plugin/` directory
  itself.
- **Only works when users add the marketplace via Git or a local
  path.** If users add via a remote URL pointing at
  `marketplace.json`, relative paths break - the server only serves
  the JSON, not the plugin files.

Use this for plugins co-located with the marketplace in the same repo.
Simplest and most common.

## 2. `github`

```json
{
  "name": "github-plugin",
  "source": {
    "source": "github",
    "repo": "owner/plugin-repo"
  }
}
```

Optional pins:

| Field | Notes                                               |
| ----- | --------------------------------------------------- |
| `ref` | Branch or tag. Defaults to the repo's default branch. |
| `sha` | Full 40-char commit SHA. Pins exactly.                |

Use when the plugin lives in its own GitHub repo, separate from the
marketplace.

## 3. `url` (any git host)

```json
{
  "name": "git-plugin",
  "source": {
    "source": "url",
    "url": "https://gitlab.com/team/plugin.git"
  }
}
```

- Full git URL (`https://` or `git@`). `.git` suffix optional - so
  Azure DevOps and AWS CodeCommit URLs without `.git` work.
- `ref` and `sha` supported as in `github`.

Use for GitLab, Bitbucket, self-hosted Gitea, etc.

## 4. `git-subdir` (plugin inside a monorepo)

```json
{
  "name": "my-plugin",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/acme-corp/monorepo.git",
    "path": "tools/claude-plugin"
  }
}
```

- Sparse, partial clone - only the subdirectory is fetched. Cheap for
  large monorepos.
- `url` accepts GitHub shorthand (`owner/repo`) and SSH URLs.
- `ref` and `sha` supported.

Use when the plugin lives at a known path inside someone else's
monorepo.

## 5. `npm`

```json
{
  "name": "my-npm-plugin",
  "source": {
    "source": "npm",
    "package": "@acme/claude-plugin",
    "version": "^2.0.0",
    "registry": "https://npm.example.com"
  }
}
```

| Field      | Notes                                                                |
| ---------- | -------------------------------------------------------------------- |
| `package`  | Required. Package name or scoped (`@org/plugin`).                    |
| `version`  | Optional. Version or range (`2.1.0`, `^2.0.0`, `~1.5.0`).            |
| `registry` | Optional. Custom registry URL. Defaults to the system npm registry.  |

Use when distributing through npm - useful for cross-team or external
distribution where Git access is awkward.

## Choosing a source

| Situation                                                    | Use            |
| ------------------------------------------------------------ | -------------- |
| Plugin lives in this same repo, next to `marketplace.json`   | Relative path  |
| Plugin is its own GitHub repo                                | `github`       |
| Plugin lives on GitLab / Bitbucket / self-hosted Git         | `url`          |
| Plugin is one of many in a shared monorepo                   | `git-subdir`   |
| Plugin is published to npm (public or private registry)      | `npm`          |

## Marketplace source vs plugin source

These are distinct concepts and easy to confuse:

- **Marketplace source** - where the user adds the marketplace from
  (`/plugin marketplace add owner/repo` or a path). Supports `ref` but
  not `sha`.
- **Plugin source** - where each individual plugin in the marketplace
  is fetched from (the `source` field above). Supports both `ref` and
  `sha`.

A marketplace at `acme-corp/plugin-catalog` can list a plugin at
`acme-corp/code-formatter`. They are independent repos, pinned
independently.
