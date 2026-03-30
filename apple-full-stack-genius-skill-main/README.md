# Apple Full-Stack Genius

A Claude Code skill that turns Claude into a **senior Apple platform engineer + design director**. Build production-grade iOS/macOS/watchOS/tvOS/visionOS apps with Swift 6, SwiftUI, iOS 26 Liquid Glass design, and zero deprecated APIs.

## What It Does

- **Builds full apps** — scaffolds complete Xcode projects with SwiftUI, SwiftData, CloudKit sync, Swift 6 strict concurrency, and Liquid Glass design
- **Generates visual assets** — app icons (light/dark/tinted), splash screens, and logos via fal.ai FLUX.2 with Vapor backend proxy
- **Audits code to A+ grade** — catches deprecated patterns, dead code, accessibility gaps, and security issues using SwiftLint, SwiftFormat, and Periphery
- **On-device AI** — Foundation Models integration (iOS 26) for entity extraction, classification, summarization, and conversational assistants
- **Full-stack** — Vapor 4 backend with shared Codable models, StoreKit 2 payments, Passkeys auth, App Intents + Siri

## Benchmark Results

Tested against Claude without the skill across 3 real-world tasks:

| Test Case | With Skill | Without Skill | Improvement |
|-----------|-----------|--------------|-------------|
| App Scaffold (Habit Tracker) | **91%** | 30% | +61pp |
| Icon/Asset Generation | **100%** | 71% | +29pp |
| Code Audit (Deprecated Fixes) | **90%** | 40% | +50pp |
| **Average** | **94%** | **47%** | **+47pp** |

## Install

### Option 1 — One-line clone (recommended)

Open your terminal and run:

```bash
git clone https://github.com/Jonnycatx/apple-full-stack-genius-skill.git ~/.claude/skills/apple-full-stack-genius-skill
```

That's it. The skill is installed and Claude Code will pick it up automatically.

### Option 2 — Manual download

1. Download this repo as a ZIP (green **Code** button → **Download ZIP**)
2. Unzip it
3. Move the folder to your skills directory:

```bash
mv apple-full-stack-genius-skill-main ~/.claude/skills/apple-full-stack-genius-skill
```

### Verify it works

Start Claude Code in any project and ask it to build an iOS app. You should see it follow the skill's architecture patterns — four-tier structure, Swift 6 concurrency, Liquid Glass design, etc.

## What's Inside

```
apple-full-stack-genius-skill/
├── SKILL.md                          # Main skill file (the brain)
├── LICENSE                           # MIT
└── references/                       # Deep-dive guides loaded on demand
    ├── project-structure.md          # Xcode project scaffold + naming conventions
    ├── swiftui-patterns.md           # SwiftUI best practices + Liquid Glass
    ├── design-intelligence.md        # Design system + accessibility + HIG
    ├── code-audit.md                 # SwiftLint, Periphery, zero-warning protocol
    ├── backend-vapor.md              # Vapor 4 server setup + shared models
    ├── deployment.md                 # TestFlight, Xcode Cloud, App Store
    ├── foundation-models.md          # On-device AI with Apple Foundation Models
    ├── image-generation.md           # fal.ai FLUX.2 icon/splash/logo pipeline
    └── evolution-log.md              # Self-correcting knowledge base
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Swift 6 (strict concurrency) |
| UI | SwiftUI + Liquid Glass (iOS 26) |
| Data | SwiftData + CloudKit sync |
| Backend | Vapor 4 (Swift on server) |
| AI | Apple Foundation Models + Core ML |
| Image Gen | fal.ai FLUX.2 via Vapor proxy |
| Auth | Passkeys + Sign in with Apple |
| Payments | StoreKit 2 |
| CI/CD | Xcode Cloud + TestFlight |
| Quality | SwiftLint + SwiftFormat + Periphery |

## Author

Built by [@Jonnycatx](https://github.com/Jonnycatx)

MIT License
