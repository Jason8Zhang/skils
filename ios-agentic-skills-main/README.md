# ios-agentic-skills

A public collection of agentic iOS/watchOS audit skills and playbooks. Use for CLI /IDE tools. Designed to be forked, adapted, and shared.

## Quick start

- Browse the skills index: [.agent/skills/README.md](.agent/skills/README.md)
- Use the template for new additions: [.agent/skills/SKILL_TEMPLATE.md](.agent/skills/SKILL_TEMPLATE.md)
- Validate required tools:
  - bash .agent/skills/scripts/setup_skills_tools.sh

## What’s inside

- .agent/skills/ — Skill playbooks and audits

## Origins: Battle-Tested on Haptix

I created this library while building **[Haptix](https://gethaptix.com)**.

I spent countless hours on every PR trying to finagle Localization, Performance tuning, or Unit testing. I would do it perfectly on one feature, forget to do it on the next, and then forget the entire process a week later.

Now, I just use `/accessibility` (or `/privacy`, `/localize`, etc.) and my agent handles the audit. These skills turn consistent quality from a memory game into a repeatable process.

## Guidance

- Always follow Apple’s Human Interface Guidelines (HIG).
- **Pro Tip:** Apple's documentation can sometimes be dense. I found [sosumi.ai](https://sosumi.ai) to be a tremendous help. It uses an MCP server to make the documentation much easier to query and understand directly within your editor.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

This repository provides general guidance and is not legal advice.
