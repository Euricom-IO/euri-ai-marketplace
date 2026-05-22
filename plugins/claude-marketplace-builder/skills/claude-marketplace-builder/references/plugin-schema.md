# `plugins/<name>/.claude-plugin/plugin.json` schema

The per-plugin manifest. Lives inside each plugin directory.

## Minimal example

```json
{
  "name": "quality-review-plugin",
  "description": "Adds a quality-review skill for quick code reviews",
  "version": "1.0.0"
}
```

## Plugin entry fields (in `marketplace.json` AND/OR `plugin.json`)

These fields can appear in either file. The marketplace entry can
augment what `plugin.json` declares (when `strict: true`, the default)
or be the sole authority (when `strict: false`).

### Required

| Field    | Type            | Notes                                                                                                                    |
| -------- | --------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `name`   | string          | kebab-case, no spaces. Public. Used in `/plugin install <name>@<marketplace>` and as the namespace for slash commands.   |
| `source` | string \| object | **Marketplace entry only.** Where to fetch the plugin from. See [[source-types]].                                       |

### Standard metadata (optional)

| Field         | Type   | Notes                                                                                                                                                              |
| ------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `displayName` | string | Human-readable name for UI (v2.1.143+). May contain spaces and any casing. Not used for lookup.                                                                    |
| `description` | string | Short plugin description. Shows up in the `/plugin` UI.                                                                                                            |
| `version`     | string | Pins the plugin to this string. Users only see updates when the value changes. Omit to use commit SHA. See [[marketplace-schema]] - "Version resolution".          |
| `author`      | object | `{ "name": "...", "email": "..." }`. `name` required if `author` is set.                                                                                           |
| `homepage`    | string | Docs URL.                                                                                                                                                          |
| `repository`  | string | Source code URL.                                                                                                                                                   |
| `license`     | string | SPDX identifier (e.g. `MIT`, `Apache-2.0`, `Proprietary`).                                                                                                         |
| `keywords`    | array  | Discovery tags.                                                                                                                                                    |
| `category`    | string | Organization category, e.g. `productivity`, `developer-tools`.                                                                                                     |
| `tags`        | array  | Searchability tags.                                                                                                                                                |
| `strict`      | bool   | **Marketplace entry only.** Default `true`. See "Strict mode" below.                                                                                               |

### Component configuration (optional)

When a component lives somewhere other than the default location, point
at it here. Paths are relative to the plugin root.

| Field        | Type             | Default location                       |
| ------------ | ---------------- | -------------------------------------- |
| `skills`     | string \| array  | `skills/<name>/SKILL.md`               |
| `commands`   | string \| array  | `commands/*.md`                        |
| `agents`     | string \| array  | `agents/*.md`                          |
| `hooks`      | string \| object | `hooks/hooks.json` or inline           |
| `mcpServers` | string \| object | `.mcp.json` or inline                  |
| `lspServers` | string \| object | inline                                 |

In hook commands and MCP server configs, reference plugin files with
the `${CLAUDE_PLUGIN_ROOT}` variable - plugins are copied to
`~/.claude/plugins/cache/...` on install, so absolute or relative
paths from the dev tree do not work at runtime.

For data that should survive plugin updates, use
`${CLAUDE_PLUGIN_DATA}` instead.

## Strict mode

The `strict` field (marketplace entry only) controls whether
`plugin.json` is the authority for component definitions.

| Value         | Behavior                                                                                                                                                          |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `true` (def.) | `plugin.json` is authoritative. The marketplace entry can add extra components; both sources merge.                                                               |
| `false`       | The marketplace entry is the entire definition. If `plugin.json` also declares components, the plugin fails to load (conflict).                                   |

Use `strict: false` when the marketplace operator wants to curate or
restructure components differently from what the plugin author shipped.

## Standard skill / command / agent locations

| Component | File pattern                                  | Frontmatter required                                                                                                    |
| --------- | --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Skill     | `skills/<name>/SKILL.md`                      | `name`, `description`. `disable-model-invocation: true` to disable auto-trigger.                                        |
| Command   | `commands/<name>.md`                          | Optional `description`, `argument-hint`, `allowed-tools`. Invoked as `/<plugin>:<command>`.                             |
| Agent     | `agents/<name>.md`                            | `name`, `description`. Optional `tools`, `model`.                                                                       |
| Hooks     | `hooks/hooks.json` or inline in `plugin.json` | JSON shape: `{ "PreToolUse": [...], "PostToolUse": [...] }`.                                                            |

Stick to the defaults unless you have a reason to override. The custom
`skills`/`commands`/`agents` fields exist for cases where the plugin is
adapted from a non-standard source tree.
