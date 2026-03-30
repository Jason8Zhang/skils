# Evolution Log — Self-Updating Knowledge Base

This document tracks mistakes made, deprecated patterns discovered, and corrected rules. It is a living document — updated at the end of every session where a correction or improvement was discovered.

---

## Deprecated Patterns Registry

These patterns are BANNED. If you write any of these, you have introduced a bug or technical debt.

| Pattern | Replace With | Reason |
|---|---|---|
| `ObservableObject` + `@Published` | `@Observable` macro | Deprecated iOS 17+, higher overhead |
| `@StateObject var vm = VM()` | `@State var vm = VM()` with `@Observable` | Only needed with ObservableObject |
| `NavigationView { }` | `NavigationStack { }` | Deprecated iOS 16+ |
| `.animation(anim)` without `value:` | `.animation(anim, value: state)` | Unpredictable behavior |
| `DispatchQueue.main.async { }` | `await MainActor.run { }` | Swift 6 concurrency |
| `try!` in production | `try` with `do/catch` | Crash risk |
| `swiftLanguageVersion(.v6)` | `.swiftLanguageMode(.v6)` | API renamed |
| `UIWebView` | `WKWebView` | Removed from SDK |
| `.fullScreenCover` without `isPresented` binding cleanup | Always clean up bindings on dismiss | Memory leak |
| Hardcoded color literals `Color(red:green:blue:)` | Semantic colors or asset catalog | Breaks dark mode |
| `Text(verbatim: "string")` for UI text | `Text("localization.key")` | Not localizable |
| Fixed font size `.font(.system(size: 17))` | Semantic `.font(.body)` | Breaks Dynamic Type |
| Force-unwrap image loads `UIImage(named: "x")!` | Optional check + fallback | Crash if asset missing |
| `@objc` on Swift 6 actor-isolated methods | Restructure to non-isolated | Actor isolation violation |
| `DispatchGroup` for async coordination | `async let` or `TaskGroup` | Swift 6 concurrency |

---

## Corrected Rules Log

### Session: Initial Setup (2026-03-10)

**Bug Found:** SKILL.md line 124 — `ObservableObject` used in Swift 6 concurrency example
- **What was wrong:** `@MainActor final class HabitStore: ObservableObject { @Published ... }`
- **Correct pattern:** `@MainActor @Observable final class HabitStore { var habits: [Habit] = [] }`
- **Rule added:** All `ObservableObject` usages → `@Observable` macro. No exceptions unless interfacing with UIKit.

**Bug Found:** `references/project-structure.md` — `swiftLanguageVersion(.v6)` used
- **What was wrong:** `.package(name: ..., swiftLanguageVersion: .v6)` in Package.swift
- **Correct pattern:** `.swiftLanguageMode(.v6)` in build settings or package manifest
- **Rule added:** Always use `.swiftLanguageMode(.v6)` not `swiftLanguageVersion`

---

## A+ Grade Criteria — Evolved Rules

These rules have been refined based on real-world quality issues:

### Concurrency Rules (Strict)
1. Every class/struct that touches UI must be `@MainActor`
2. Every class that does I/O (network, disk, CoreData) must be an `actor`
3. Never call `await` on a UI update from a non-`@MainActor` context without `await MainActor.run {}`
4. All `Sendable` conformances must be explicit — never assume
5. `Task.detached` only when you explicitly don't want inherited actor context

### Design Rules (Strict)
1. Every screen tested in dark mode AND light mode
2. Every animated element checked with `accessibilityReduceMotion`
3. Every interactive element has minimum 44×44pt tap target
4. Every interactive element has `accessibilityLabel`
5. No hardcoded colors — all semantic or asset catalog with light/dark variants

### Code Quality Rules (Strict)  
1. Zero compiler warnings in Release build
2. Zero SwiftLint violations on strict ruleset
3. Zero Periphery findings (unused code)
4. Zero force-unwraps (`!`) except `ModelContainer` initialization
5. All user-facing strings in String Catalog (localizable)

### Image Generation Rules
1. Always route generation through Vapor backend (never expose API keys in iOS)
2. FLUX.2 [pro] for final production quality; FLUX.1 [schnell] for previews
3. App icons: always generate light + dark + tinted variants
4. Never use copyrighted/trademarked elements in AI-generated assets

---

## End-of-Session Retrospective Protocol

At the end of any coding session, run through these questions and update this file:

```
1. Were any Swift compiler warnings generated? → Fix + add to deprecated patterns
2. Were any SwiftLint violations flagged? → Fix + document rule
3. Did the user correct any generated code? → What was wrong? Add to log
4. Were any Apple APIs used that are deprecated? → Document + find replacement  
5. Were any performance issues identified? → Document root cause + fix
6. Were any security issues found? → Document + fix + add to security checklist
7. Were any accessibility gaps found? → Document + fix
8. Were any dead code findings from Periphery? → Document type of dead code
9. Were any better approaches discovered mid-session? → Document the better way
10. Any new iOS 26 APIs used that should be added to the stack? → Add to SKILL.md
```

---

## Platform Version Notes (Current: iOS 26)

### iOS 26 — Current Minimum Target
```swift
// Package.swift
platforms: [
    .iOS(.v26),
    .macOS(.v26),     // macOS Tahoe
    .watchOS(.v26),
    .tvOS(.v26),
    .visionOS(.v3)    // visionOS 3
]

// Xcode target settings:
// IPHONEOS_DEPLOYMENT_TARGET = 26.0
// MACOSX_DEPLOYMENT_TARGET = 26.0

// Minimum hardware:
// iPhone 11 (A13 Bionic) — minimum iOS 26 device
// iPhone 15 Pro — required for Apple Intelligence / Foundation Models
// Drop: iPhone XS, XR (no longer supported by iOS 26)
```

### Key iOS 26 APIs — Always Use
- `Foundation Models` — on-device LLM (replaces custom CoreML text models for most cases)
- `Liquid Glass` materials — `.regularMaterial`, `.ultraThinMaterial`, `glassBackgroundEffect()`
- `Live Translation API` — for multilingual apps
- `App Intents + Tool Calling` — for Siri / Apple Intelligence integration
- `Metal 4` — ML-augmented shaders, frame interpolation, denoising
- `Declared Age Range API` — for apps with age-appropriate content
- `Eye Scrolling API` — for accessibility

### iOS 26 APIs to Avoid / Be Careful With
- Foundation Models: NOT for math, code gen, factual world knowledge
- Liquid Glass on non-Apple platforms: visionOS uses `glassBackgroundEffect()` not `.regularMaterial`
- Metal 4 frame interpolation: profile first — can increase GPU load

---

## Research Sources

When doing platform research, always check these in order:
1. `developer.apple.com/documentation` — official API docs
2. `developer.apple.com/videos/wwdc2025` — WWDC 2025 session videos
3. `developer.apple.com/design/human-interface-guidelines` — HIG
4. `swift.org/evolution` — Swift Evolution proposals
5. `forums.developer.apple.com` — Apple's developer forums
6. `swiftbysundell.com`, `avanderlee.com`, `donnywals.com` — trusted community blogs
