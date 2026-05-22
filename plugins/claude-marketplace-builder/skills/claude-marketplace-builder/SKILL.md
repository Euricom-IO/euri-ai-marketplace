---
name: claude-marketplace-builder
description: "Scaffold and maintain Claude Code plugin marketplaces. Trigger when the user asks to (1) create a new Claude marketplace or plugin catalog, (2) add a plugin to an existing marketplace.json, (3) convert an existing skill folder into a plugin, (4) validate a marketplace, or mentions 'marketplace.json', 'plugin.json', '/plugin install', '/plugin marketplace add'. Distinguish from create-skill: that creates a single SKILL.md; this creates the marketplace + plugin envelope around it."
license: MIT
---

# Claude marketplace builder

## What this skill does

Two responsibilities:

1. **Bootstrap a new marketplace** in a fresh or existing repo: create the
   `.claude-plugin/marketplace.json` catalog and the first
   `plugins/<name>/.claude-plugin/plugin.json` manifest, in the exact
   directory shape `/plugin marketplace add` expects.
2. **Extend an existing marketplace** by adding a new plugin entry to
   `marketplace.json` and scaffolding the matching `plugins/<name>/` tree
   with its `plugin.json` and the right skill / command / agent / hook
   subdirectories.

It does **not** write the actual skill content — that's [[create-skill]]'s
job. Use this skill to package one or more SKILL.md files into a
distributable marketplace.

## When NOT to trigger

- The user is editing the body of an existing SKILL.md, agent, or
  command file. Defer to `create-skill` or a direct edit.
- The user wants a slash command for personal use only, in
  `~/.claude/commands/` — no marketplace needed.
- The user asks about installing or using someone else's marketplace
  (`/plugin marketplace add owner/repo`). That's a one-command shell
  operation; no scaffolding required.

## Workflows

### A. Bootstrap a new marketplace

Use when the repo has no `.claude-plugin/` directory yet.

1. **Pick a marketplace name** with the user. Constraints:
   - kebab-case, no spaces
   - reserved names are blocked (see [[marketplace-schema]] - "Reserved
     names" note)
   - public-facing: users see it in `/plugin install <plugin>@<name>`
2. **Create the directory skeleton**:
   ```
   .claude-plugin/marketplace.json
   plugins/<first-plugin>/.claude-plugin/plugin.json
   plugins/<first-plugin>/skills/<skill-name>/SKILL.md   (if a skill)
   plugins/<first-plugin>/commands/<command-name>.md     (if a command)
   plugins/<first-plugin>/agents/<agent-name>.md         (if an agent)
   ```
3. **Write `marketplace.json`** using the minimal schema from
   [[marketplace-schema]]. Required: `name`, `owner.name`, `plugins[]`.
   Default to omitting `version` so each commit acts as a release.
4. **Write `plugin.json`** for the first plugin per
   [[plugin-schema]]. Required: `name`. Add `description` and
   `author` even though they're optional - they show up in the
   `/plugin` UI.
5. **Validate** (see workflow D below).

### B. Add a plugin to an existing marketplace

Use when `.claude-plugin/marketplace.json` already exists.

1. **Read the existing `marketplace.json`** and confirm the new plugin
   name does not clash with any entry in `plugins[]`.
2. **Scaffold the plugin tree** under `plugins/<new-name>/` following
   the same shape as workflow A step 2.
3. **Append a new entry to `plugins[]`** in `marketplace.json` with
   the right `source` field (see [[source-types]] to choose
   relative / github / url / git-subdir / npm).
4. **Write the plugin's `plugin.json`**.
5. **Validate**.

### C. Convert an existing skill folder into a plugin

When the user points at a directory that already contains a
`SKILL.md` (and maybe `scripts/`, `references/`, `assets/`) and wants
to publish it through a marketplace:

1. Decide whether this slots into an existing marketplace (workflow B)
   or warrants a new one (workflow A).
2. Move or copy the source folder into
   `plugins/<plugin-name>/skills/<skill-name>/`. The skill name comes
   from the existing SKILL.md frontmatter; the plugin name often
   matches but doesn't have to.
3. Write the `plugin.json` envelope around it.
4. Update or create `marketplace.json`.
5. **Check for environment-specific paths.** Skills written for
   Claude.ai often reference `/mnt/skills/...` or
   `/mnt/user-data/`; those don't exist in Claude Code. For
   Claude Code plugins, prefer `${CLAUDE_PLUGIN_ROOT}` or paths
   relative to the skill directory. Flag any such references to the
   user before publishing.
6. Validate.

### D. Validate

```bash
claude plugin validate .                          # checks marketplace.json
claude plugin validate ./plugins/<plugin-name>    # checks plugin.json + SKILL.md frontmatter
```

Run both. Marketplace-level validation catches duplicate plugin names,
`..` traversal in source paths, and version mismatches. Plugin-level
validation parses SKILL.md / agent / command YAML frontmatter and
`hooks/hooks.json`.

Common errors and fixes are listed in the
[official troubleshooting docs](https://code.claude.com/docs/en/plugin-marketplaces#troubleshooting).

## Testing locally before publishing

```
/plugin marketplace add <absolute-path-to-repo>
/plugin install <plugin-name>@<marketplace-name>
```

For relative-path plugin sources, the user must add the marketplace
via a Git URL or local directory - **not** via a direct URL to the
`marketplace.json` file. See [[source-types]] for why.

## References

- [[marketplace-schema]] - fields of `.claude-plugin/marketplace.json`
- [[plugin-schema]] - fields of `plugins/<name>/.claude-plugin/plugin.json`
- [[source-types]] - the five plugin source types and when to use each

Authoritative spec: https://code.claude.com/docs/en/plugin-marketplaces
