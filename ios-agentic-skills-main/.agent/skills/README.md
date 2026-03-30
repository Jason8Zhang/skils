# Skills Index

- **[accessibility](accessibility/SKILL.md)** - SwiftUI accessibility audit against Apple HIG.
- **[crash-safety](crash-safety/SKILL.md)** - Audit for crash risks like force unwraps and array indexing.
- **[data-modeling-and-sync](data-modeling-and-sync/SKILL.md)** - Audit SwiftData/CoreData modeling and iCloud sync logic.
- **[error-messaging-and-empty-states](error-messaging-and-empty-states/SKILL.md)** - Audit user-facing error messages and empty state UX.
- **[haptics-design](haptics-design/SKILL.md)** - Design and audit haptic patterns for clarity and comfort.
- **[marketing-copy](marketing-copy/SKILL.md)** - Guidelines for high-impact marketing copywriting.
- **[localize](localize/SKILL.md)** - Comprehensive localization audit for strings and resources.
- **[performance](performance/SKILL.md)** - Audit for performance hotspots (layout, animation, battery).
- **[privacy](privacy/SKILL.md)** - Audit for App Store privacy compliance and permissions.
- **[testing-strategy](testing-strategy/SKILL.md)** - Evaluate unit and UI testing coverage and patterns.
- **[visual-design-and-contrast](visual-design-and-contrast/SKILL.md)** - Audit visual hierarchy, layout consistency, and dark mode.
- **[watch-battery-optimization](watch-battery-optimization/SKILL.md)** - Audit watchOS battery usage and AOD behavior.


---

## Project-Agnostic Notes (How to adapt these skills)

- Replace app-specific paths with your app’s root folders.
	- Example: `MyApp/Views/` → `YourApp/Views/`
- For watchOS apps, update the `WATCH_DIR` variable to your watch target folder.
	- Example: `MyApp Watch App` → `YourApp Watch App`
- If you don’t use AppIntents, skip those checks.
- If you use UIKit, adapt SwiftUI-specific checks to UIKit equivalents.

---

## Checks by Phase

| Phase | Recommended Skills |
|------|---------------------|
| Feature development | accessibility, crash-safety, localize, testing-strategy |
| PR review | performance, privacy, error-messaging-and-empty-states |
| Pre-release | visual-design-and-contrast, watch-battery-optimization, data-modeling-and-sync |

---

## Example Audit Output (Expected Format)

| Category | Issues | Status |
|----------|--------|--------|
| VoiceOver labels | 3 | ❌ |
| Reduce Motion | 0 | ✅ |
| Dynamic Type | 2 | ❌ |

---

## Tools Required

Most skills use:
- `rg` (ripgrep)
- `python3`
- Xcode (Accessibility Inspector, Instruments)

Run the helper script to validate/install tools:

```bash
bash .agent/skills/scripts/setup_skills_tools.sh
```

---

## CI Recommendation

Add a lightweight CI step that runs localization checks and fails on missing or stale keys:

```bash
python3 scripts/check_localization_status.py YourApp/Localizable.xcstrings
python3 scripts/check_localization_status.py YourApp/AppIntents/AppShortcuts.xcstrings
python3 scripts/check_localization_status.py "YourApp Watch App Watch App/Localizable.xcstrings"
```

---

## Template

Use the template below when adding a new skill:
- [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md)
