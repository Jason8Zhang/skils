# Apple Full-Stack Genius — Project Structure

## Standard Xcode Project Scaffold

Every project follows this structure (monorepo with SPM packages):

```
MyApp/
├── MyApp.xcodeproj                     # or .xcworkspace if using CocoaPods (don't — use SPM)
├── MyApp/                              # Main app target
│   ├── App/
│   │   ├── MyApp.swift                 # @main entry point, ModelContainer setup
│   │   └── AppDelegate.swift           # Only if push notifications / UIKit lifecycle needed
│   ├── Features/                       # One folder per feature (vertical slices)
│   │   ├── Habits/
│   │   │   ├── HabitsView.swift
│   │   │   ├── HabitDetailView.swift
│   │   │   ├── HabitStore.swift        # @MainActor @Observable store
│   │   │   └── HabitComponents/        # Sub-views used only in this feature
│   │   │       ├── HabitRowView.swift
│   │   │       └── StreakBadgeView.swift
│   │   ├── Settings/
│   │   │   └── SettingsView.swift
│   │   └── Onboarding/
│   │       └── OnboardingFlow.swift
│   ├── Core/                           # Shared across features
│   │   ├── Models/                     # SwiftData @Model classes
│   │   │   ├── Habit.swift
│   │   │   └── HabitLog.swift
│   │   ├── Services/                   # Background actors: networking, AI, haptics
│   │   │   ├── CloudSyncService.swift
│   │   │   ├── HabitCoachService.swift  # Foundation Models / Core ML
│   │   │   └── HapticsService.swift
│   │   ├── Repositories/               # Data access layer (actor-isolated)
│   │   │   └── HabitRepository.swift
│   │   └── Extensions/                 # Swift stdlib / SwiftUI / Foundation extensions
│   │       ├── Color+Hex.swift
│   │       ├── Date+Formatting.swift
│   │       └── View+LiquidGlass.swift
│   ├── DesignSystem/                   # App-wide design tokens and components
│   │   ├── Tokens/
│   │   │   ├── Colors.swift            # Adaptive semantic colors
│   │   │   ├── Typography.swift        # Font scale
│   │   │   └── Spacing.swift           # 4pt grid constants
│   │   └── Components/
│   │       ├── LiquidGlassCard.swift
│   │       ├── PrimaryButton.swift
│   │       ├── StreakRing.swift         # Custom Metal-backed ring
│   │       └── HapticButton.swift
│   ├── Resources/
│   │   ├── Assets.xcassets
│   │   ├── Localizable.xcstrings       # String Catalog (Xcode 15+)
│   │   └── PrivacyInfo.xcprivacy       # Required privacy manifest
│   └── Preview Content/
│       └── PreviewData.swift           # Shared mock data for Previews
│
├── MyAppWidget/                        # WidgetKit extension target
│   ├── MyAppWidget.swift
│   ├── HabitWidgetView.swift
│   └── LiveActivityView.swift
│
├── MyAppWatch WatchKit App/            # watchOS target
│   ├── MyAppWatchApp.swift
│   └── WatchHabitsView.swift
│
├── MyAppWatch WatchKit Extension/      # watchOS extension
│   └── WatchHabitStore.swift
│
├── MyAppClip/                          # App Clip target
│   └── AppClipEntryView.swift
│
├── Packages/                           # Local SPM packages (modular architecture)
│   ├── SharedModels/                   # Codable models shared with Vapor backend
│   │   ├── Package.swift
│   │   └── Sources/SharedModels/
│   │       ├── HabitDTO.swift
│   │       └── APIResponse.swift
│   └── SharedUI/                       # Cross-platform UI primitives (if multi-platform)
│       ├── Package.swift
│       └── Sources/SharedUI/
│           └── DesignTokens.swift
│
├── Backend/                            # Vapor server (optional — include if full-stack)
│   ├── Package.swift
│   ├── Sources/App/
│   │   ├── configure.swift
│   │   ├── routes.swift
│   │   └── Controllers/
│   │       └── HabitController.swift
│   └── Tests/AppTests/
│
└── MyAppTests/                         # XCTest suite
    ├── Unit/
    │   ├── HabitStoreTests.swift
    │   └── HabitRepositoryTests.swift
    └── Snapshots/
        └── HabitsViewSnapshotTests.swift
```

---

## App Entry Point Template

```swift
// MyApp.swift
import SwiftUI
import SwiftData

@main
struct MyApp: App {
    // MARK: - Model Container (CloudKit sync enabled)
    let container: ModelContainer = {
        let schema = Schema([
            Habit.self,
            HabitLog.self
        ])
        let configuration = ModelConfiguration(
            schema: schema,
            cloudKitDatabase: .private("iCloud.com.yourcompany.myapp"),
            groupContainer: .identifier("group.com.yourcompany.myapp") // for Widget sharing
        )
        do {
            return try ModelContainer(for: schema, configurations: [configuration])
        } catch {
            fatalError("ModelContainer failed: \(error)")
        }
    }()

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(container)

        // visionOS: add Immersive Space here
        #if os(visionOS)
        ImmersiveSpace(id: "MainImmersiveSpace") {
            ImmersiveSpaceView()
        }
        #endif
    }
}
```

---

## Required Entitlements

Every project needs these capabilities configured in Xcode:

| Capability | Required For |
|---|---|
| iCloud (CloudKit) | SwiftData cloud sync |
| App Groups | Widget ↔ app data sharing |
| Push Notifications | Live Activities, remote sync triggers |
| Associated Domains | Universal Links, Passkeys |
| HealthKit | If accessing health data |
| Siri | App Intents |
| Background Modes | Background fetch, remote notifications |

---

## PrivacyInfo.xcprivacy Template

Apple requires this in every app since 2024. Always include it:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" ...>
<plist version="1.0">
<dict>
    <key>NSPrivacyTracking</key>
    <false/>
    <key>NSPrivacyTrackingDomains</key>
    <array/>
    <key>NSPrivacyCollectedDataTypes</key>
    <array>
        <!-- Only include data types you actually collect -->
        <dict>
            <key>NSPrivacyCollectedDataType</key>
            <string>NSPrivacyCollectedDataTypeOtherUserContent</string>
            <key>NSPrivacyCollectedDataTypeLinked</key>
            <true/>
            <key>NSPrivacyCollectedDataTypeTracking</key>
            <false/>
            <key>NSPrivacyCollectedDataTypePurposes</key>
            <array>
                <string>NSPrivacyCollectedDataTypePurposeAppFunctionality</string>
            </array>
        </dict>
    </array>
    <key>NSPrivacyAccessedAPITypes</key>
    <array>
        <!-- Declare all API types accessed by your app and its dependencies -->
    </array>
</dict>
</plist>
```

---

## SPM Package.swift for SharedModels

```swift
// Packages/SharedModels/Package.swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "SharedModels",
    platforms: [
        .iOS(.v26),
        .macOS(.v26),
        .watchOS(.v11),
        .tvOS(.v18),
        .visionOS(.v2)
    ],
    products: [
        .library(name: "SharedModels", targets: ["SharedModels"]),
    ],
    targets: [
        .target(
            name: "SharedModels",
            path: "Sources/SharedModels",
            swiftSettings: [
                .swiftLanguageMode(.v6)
            ]
        ),
        .testTarget(
            name: "SharedModelsTests",
            dependencies: ["SharedModels"]
        ),
    ]
)
```

---

## Xcode Build Settings (Important)

In your project's `.xcodeproj` build settings, always set:

```
SWIFT_STRICT_CONCURRENCY = complete
SWIFT_VERSION = 6.0
ENABLE_HARDENED_RUNTIME = YES          // Required for notarization
CODE_SIGN_STYLE = Automatic
GENERATE_INFOPLIST_FILE = YES
CURRENT_PROJECT_VERSION = $(MARKETING_VERSION)  // For Xcode Cloud auto-versioning
```

---

## Naming Conventions

- **Types**: `UpperCamelCase` — `HabitStore`, `CloudSyncService`
- **Properties/functions**: `lowerCamelCase` — `currentStreak`, `logCompletion()`
- **Protocols**: End in `-able`, `-ing`, or describe the role — `HabitPersisting`, `StreakCalculating`
- **Views**: Always suffix with `View` — `HabitRowView`, `StreakBadgeView`
- **Stores / ViewModels**: Suffix with `Store` (prefer `@Observable`) — `HabitStore`
- **Repositories**: Suffix with `Repository` — `HabitRepository`
- **Services**: Suffix with `Service` — `HapticsService`, `HabitCoachService`
- **DTOs** (API models): Suffix with `DTO` — `HabitDTO`
- **Actors** (background): Suffix with `Actor` if not a Repository/Service — `SyncActor`
