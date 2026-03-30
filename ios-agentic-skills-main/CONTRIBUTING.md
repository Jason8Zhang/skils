# Contributing

Thanks for helping improve ios-agentic-skills!

## Ways to contribute

- Add a new skill using the template
- Improve an existing skill with clearer checks
- Fix typos or improve examples

## Adding a new skill

1. Copy the template: [.agent/skills/SKILL_TEMPLATE.md](.agent/skills/SKILL_TEMPLATE.md)
2. Create a new folder in .agent/skills/
3. Name your file SKILL.md
4. Keep sections consistent with the template

## Style guidelines

- Keep guidance concise and action‑oriented
- Prefer commands that work on macOS
- Include “When to use this skill” and “Output Format” sections

## Pull request checklist

- [ ] New skill uses the template structure
- [ ] Commands are scoped (skip Tests/UITests)
	- Example: `rg --type swift -g '!*Tests*' -g '!*UITests*' 'PATTERN' YourApp/`
- [ ] Output format table included
- [ ] Spelling and grammar reviewed
