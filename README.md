# Euricom Plugins Directory

A curated directory of high-quality plugins for Claude Code.

> **⚠️ Important:** Make sure you trust a plugin before installing, updating, or using it. Anthropic does not control what MCP servers, files, or other software are included in plugins and cannot verify that they will work as intended or that they won't change. See each plugin's homepage for more information.

## Structure

- **`/plugins`** - Internal plugins developed and maintained by Euricom
- **`/external_plugins`** - Third-party plugins from partners and the community

## Installation

Plugins can be installed directly from this marketplace via Claude Code's plugin system.

To install, run 

```
/plugin marketplace add git@github.com:euricom-io/euri-ai-marketplace.git
/plugin install {plugin-name}@euricom-plugins-directory
```

or browse for the plugin in `/plugin > Discover`

## Contributing

### Plugins

Plugins are developed by Euricom team members. See `/plugins/example-plugin` for a reference implementation.

**Naming convention:** internal plugins and their skills are prefixed with `euricom-` (e.g. `euricom-word-template`, `euricom-accessibility-testing`). Apply the prefix to the plugin directory, the `name` in `plugin.json`, the skill directory, and the `name` in the SKILL.md frontmatter. Third-party plugins under `/external_plugins` keep their upstream name.

### External Plugins

Third-party partners are hand picked for inclusion in the marketplace. External plugins must meet quality and security standards for approval.

## Plugin Structure

Each plugin follows a standard structure:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # Plugin metadata (required)
├── .mcp.json            # MCP server configuration (optional)
├── commands/            # Slash commands (optional)
├── agents/              # Agent definitions (optional)
├── skills/              # Skill definitions (optional)
└── README.md            # Documentation
```

## Documentation

For more information on developing Claude Code plugins, see the [official documentation](https://code.claude.com/docs/en/plugins).