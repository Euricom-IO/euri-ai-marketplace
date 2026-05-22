# `.claude-plugin/marketplace.json` schema

The catalog file at the marketplace root. Tells Claude Code which
plugins exist and where to fetch each one.

## Minimal example

```json
{
  "name": "my-plugins",
  "owner": { "name": "Your Name" },
  "plugins": [
    {
      "name": "quality-review-plugin",
      "source": "./plugins/quality-review-plugin",
      "description": "Adds a quality-review skill for quick code reviews"
    }
  ]
}
```

## Required fields

| Field     | Type   | Notes                                                                                                                     |
| --------- | ------ | ------------------------------------------------------------------------------------------------------------------------- |
| `name`    | string | kebab-case, no spaces. Public - users see it as `/plugin install <plugin>@<name>`. Reserved names blocked (see below).    |
| `owner`   | object | At minimum `owner.name`. `owner.email` is optional.                                                                       |
| `plugins` | array  | Each entry needs at least `name` and `source`. See [[plugin-schema]] for the per-plugin fields.                           |

## Reserved marketplace names

The following names are reserved for Anthropic and will be rejected:

`claude-code-marketplace`, `claude-code-plugins`,
`claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`,
`agent-skills`, `anthropic-agent-skills`, `knowledge-work-plugins`,
`life-sciences`, `claude-for-legal`, `claude-for-financial-services`,
`financial-services-plugins`.

Also blocked: names that impersonate official marketplaces, e.g.
`official-claude-plugins`, `anthropic-tools-v2`.

## Optional top-level fields

| Field                                  | Type    | Notes                                                                                                                                                            |
| -------------------------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `$schema`                              | string  | JSON Schema URL for editor autocomplete. Ignored by Claude Code at load time.                                                                                    |
| `description`                          | string  | Short marketplace description. Surfaces in the `/plugin` UI.                                                                                                     |
| `version`                              | string  | Marketplace manifest version.                                                                                                                                    |
| `metadata.pluginRoot`                  | string  | Base dir prepended to relative plugin sources. With `"./plugins"` you can write `"source": "formatter"` instead of `"source": "./plugins/formatter"`.            |
| `allowCrossMarketplaceDependenciesOn`  | array   | Other marketplaces this one's plugins may depend on. Anything not listed is blocked at install.                                                                  |

`description` and `version` are also accepted under `metadata` for
backward compatibility - but prefer the top-level forms.

## Version resolution (important)

Claude Code resolves the version of each plugin from the first of these
that is set:

1. `version` in the plugin's `plugin.json`
2. `version` in the plugin's marketplace entry
3. The git commit SHA of the plugin's source

For git-hosted marketplaces, **omit `version` entirely** and every
commit counts as a new release - the simplest setup for actively
developed plugins.

If you pin `version: "1.0.0"` and push new commits without changing the
string, existing users see no update because Claude Code matches by
version, not commit. **Bump on every release** if you pin.

Don't set `version` in both `plugin.json` and the marketplace entry -
the `plugin.json` value wins silently, which can mask a marketplace
override.
