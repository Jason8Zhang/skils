# Code Quality & Audit System

The full end-to-end audit protocol for achieving A+ code quality. Run this EVERY time you finish building an app, feature, or module. Zero tolerance for dead code, bugs, security issues, or deprecated patterns.

## Table of Contents
1. [A+ Quality Standard](#standard)
2. [Automated Audit Tools](#tools)
3. [Swift 6 Correctness Audit](#swift6)
4. [Security Audit Checklist](#security)
5. [Dead Code Elimination](#dead-code)
6. [Performance Audit](#performance)
7. [Accessibility Audit](#accessibility)
8. [Localization Audit](#localization)
9. [Pre-Submission Final Checklist](#final)

---

## 1. A+ Quality Standard {#standard}

An app achieves A+ grade when ALL of the following pass:

```
✅ Zero compiler warnings (not just errors — warnings too)
✅ Zero SwiftLint violations (strict ruleset)
✅ Zero Periphery dead code findings
✅ Zero deprecated API usage
✅ Zero force-unwraps (!) in production code paths
✅ Zero hardcoded strings (all in String Catalogs)
✅ Zero hardcoded colors (all semantic or asset catalog)
✅ Zero blocking MainActor calls (all I/O on background actors)
✅ Zero accessibility omissions (every interactive element labeled)
✅ Zero security issues (no cleartext, no keychain misuse)
✅ All Xcode Previews compile and render correctly
✅ All unit tests pass
✅ App builds for ALL enabled platforms (iOS, iPadOS, watchOS, etc.)
✅ No runtime crashes in TestFlight beta
```

---

## 2. Automated Audit Tools {#tools}

### SwiftLint — Style & Code Quality
```bash
# Install
brew install swiftlint

# Run in project root
swiftlint lint --strict

# Recommended .swiftlint.yml:
```
```yaml
# .swiftlint.yml — place in project root
excluded:
  - Pods
  - .build
  - DerivedData

opt_in_rules:
  - array_init
  - closure_end_indentation
  - closure_spacing
  - collection_alignment
  - contains_over_filter_count
  - contains_over_filter_is_empty
  - discouraged_object_literal
  - empty_collection_literal
  - empty_string
  - explicit_init
  - fallthrough
  - fatal_error_message
  - file_name
  - first_where
  - force_unwrapping          # Treat as error
  - implicit_return
  - joined_default_parameter
  - last_where
  - literal_expression_end_indentation
  - multiline_arguments
  - multiline_literal_brackets
  - operator_usage_whitespace
  - overridden_super_call
  - pattern_matching_keywords
  - prefer_self_type_over_type_of_self
  - redundant_nil_coalescing
  - redundant_type_annotation
  - sorted_imports
  - unneeded_parentheses_in_closure_argument
  - vertical_parameter_alignment_on_call
  - yoda_condition

disabled_rules:
  - todo   # We allow TODO during development

force_cast: error
force_try: error
force_unwrapping: error
line_length:
  warning: 120
  error: 160
  ignores_comments: true
file_length:
  warning: 400
  error: 600
type_body_length:
  warning: 250
  error: 400
function_body_length:
  warning: 60
  error: 100
```

### SwiftFormat — Code Formatting
```bash
# Install
brew install swiftformat

# Run in project root
swiftformat . --swiftversion 6.0

# Key formatting rules enforced:
# - Trailing commas in collections
# - Consistent import sorting
# - Removing redundant return
# - Consistent spacing
# - Removing unused self
```

### Periphery — Dead Code Detection
```bash
# Install
brew install peripheryapp/periphery/periphery

# Initial setup (interactive)
periphery scan --setup

# Ongoing scan
periphery scan

# Recommended .periphery.yml:
```
```yaml
# .periphery.yml
workspace: YourApp.xcworkspace
schemes:
  - YourApp
  - YourAppTests
targets:
  - YourApp
retain_public: false          # Set true if building a framework
retain_objc_accessible: true  # Required for any @objc / UIKit code
retain_assign_only_properties: false
disable_redundant_public_analysis: false
```
```bash
# Integrate in CI — fail build on findings:
periphery scan --format xcode 2>&1 | grep "warning:\|error:" | while read line; do
    echo "$line"
done
# Non-zero exit if any findings
```

### Xcode Build Settings for Maximum Warning Detection
```
SWIFT_STRICT_CONCURRENCY = complete          // Catch all actor isolation issues
TREAT_WARNINGS_AS_ERRORS = YES               // Zero-tolerance warnings in CI
CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES
CLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR
CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR
GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE
```

---

## 3. Swift 6 Correctness Audit {#swift6}

### Deprecated Pattern Detection — Search & Replace

Before finalizing any code, scan for ALL of these and fix:

```swift
// ❌ PATTERN 1: ObservableObject (deprecated in Swift 6 / iOS 17+)
// Search: `: ObservableObject`
// Fix: Use @Observable macro
@Observable
final class ViewModel {  // ✅ No ObservableObject
    var data: [Item] = []
}

// ❌ PATTERN 2: @Published (goes with ObservableObject)
// Search: `@Published`
// Fix: Regular stored property in @Observable class
@Observable
final class Store {
    var items: [Item] = []  // ✅ No @Published needed
}

// ❌ PATTERN 3: NavigationView (deprecated iOS 16+)
// Search: `NavigationView {`
// Fix: NavigationStack
NavigationStack {  // ✅
    ContentView()
}

// ❌ PATTERN 4: @StateObject (only needed for ObservableObject)
// Search: `@StateObject`
// Fix: Use @State with @Observable class
@State private var viewModel = ViewModel()  // ✅

// ❌ PATTERN 5: .animation without value parameter (iOS 15+)
// Search: `.animation(.` followed by `)` without `value:`
// Fix: Always provide value
.animation(.spring(duration: 0.3), value: isExpanded)  // ✅

// ❌ PATTERN 6: DispatchQueue.main.async
// Search: `DispatchQueue.main.async`
// Fix: MainActor.run
await MainActor.run { /* UI update */ }  // ✅

// ❌ PATTERN 7: try! (except ModelContainer initialization)
// Search: `try!` (except in ModelContainer init)
// Fix: Proper error handling
do {
    let result = try riskyOperation()
} catch {
    handleError(error)
}

// ❌ PATTERN 8: UIViewController subclass (unless strictly needed for UIKit bridge)
// Search: `: UIViewController`
// Fix: Use SwiftUI View + UIViewControllerRepresentable only when needed

// ❌ PATTERN 9: swiftLanguageVersion(.v6) — deprecated
// Search: `swiftLanguageVersion(.v6)`
// Fix: .swiftLanguageMode(.v6)
.swiftLanguageMode(.v6)  // ✅

// ❌ PATTERN 10: Hardcoded strings in UI
// Search for Text(""), Button(""), Label("", ...) with literal strings
// Fix: Use String Catalogs and String(localized:)
Text("welcome_title")  // ✅ Key in String Catalog
// Or in Swift:
let title = String(localized: "welcome.title")
```

### Actor Isolation Checklist
```swift
// Every service class must declare its actor:
@MainActor final class ViewModel { ... }    // UI-facing classes
actor Repository { ... }                     // Background data classes  
@globalActor actor CloudSyncActor { ... }    // Custom global actor

// Crossing actor boundaries must be explicit:
Task { @MainActor in
    // UI update from background context
}

// Sendable types must be declared:
struct DataModel: Sendable, Codable { ... }  // For cross-actor transfer
```

---

## 4. Security Audit Checklist {#security}

### Data Storage Security
```swift
// ✅ Sensitive data in Keychain — NEVER UserDefaults
import Security

final class KeychainService {
    static func save(_ value: String, for key: String) throws {
        let data = Data(value.utf8)
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly  // ✅ Device-only
        ]
        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw KeychainError.saveFailed(status) }
    }
}

// ❌ Never store sensitive data in:
UserDefaults.standard.set(token, forKey: "authToken")  // ❌ Plaintext plist
// Files without Data Protection:
try data.write(to: fileURL)  // ❌ Missing protection attribute
// ✅ With protection:
try data.write(to: fileURL, options: [.completeFileProtection])
```

### Network Security
```swift
// ✅ ATS (App Transport Security) — always HTTPS
// Info.plist: NSAllowsArbitraryLoads must be false (default)
// Never add NSAllowsArbitraryLoads = true for production

// ✅ Certificate pinning for high-security apps (finance, health):
class PinningURLSessionDelegate: NSObject, URLSessionDelegate {
    func urlSession(_ session: URLSession, 
                    didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust,
              let certificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        // Compare against pinned certificate
        let pinnedData = // load from bundle
        if SecCertificateCopyData(certificate) == pinnedData as CFData {
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```

### Input Validation
```swift
// ✅ Validate all user input before processing
struct InputValidator {
    static func sanitizeForDisplay(_ input: String) -> String {
        // Strip HTML/script injection attempts for WebView display
        input.replacingOccurrences(of: "<[^>]+>", with: "", options: .regularExpression)
    }
    
    static func isValidEmail(_ email: String) -> Bool {
        let regex = #"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$"#
        return email.range(of: regex, options: [.regularExpression, .caseInsensitive]) != nil
    }
    
    static func isValidURL(_ urlString: String) -> Bool {
        guard let url = URL(string: urlString) else { return false }
        return url.scheme == "https"  // Only accept HTTPS
    }
}
```

### Privacy & Permissions
```swift
// ✅ Request permissions only when needed (not on launch)
// ✅ Provide clear NSUsageDescription strings in Info.plist
// ✅ Handle permission denied gracefully with Settings deep link

// Required Info.plist strings for common permissions:
// NSCameraUsageDescription — "Used to scan QR codes"
// NSPhotoLibraryUsageDescription — "To save and share images"
// NSLocationWhenInUseUsageDescription — "To show nearby locations"
// NSHealthShareUsageDescription — "To display your fitness data"
// NSMicrophoneUsageDescription — "For voice input features"

// ✅ Check permission status before requesting:
let status = await PHPhotoLibrary.requestAuthorization(for: .readWrite)
switch status {
case .authorized, .limited: /* proceed */
case .denied, .restricted: /* show settings prompt */
case .notDetermined: /* request */
@unknown default: break
}
```

---

## 5. Dead Code Elimination {#dead-code}

### Automated Detection with Periphery
```bash
# Full scan with xcode output for inline warnings:
periphery scan --format xcode

# Common categories Periphery catches:
# - Unused functions and methods
# - Unused properties and variables
# - Unused protocols (conformed but never used as existential)
# - Unused parameters in functions
# - Unused enum cases
# - Unused imports
```

### Manual Dead Code Audit Patterns

Search for these patterns in your codebase:

```swift
// ❌ Commented-out code blocks — delete them
// let oldValue = calculateOld()  // TODO: use this someday
// ✅ If you need it someday, Git history has it.

// ❌ TODOs older than 30 days — fix or delete the feature
// TODO: implement this (added 3 months ago)

// ❌ Debug/test code left in production
print("DEBUG: \(value)")  // ❌ Use os_log or remove
#if DEBUG
print("only in debug")  // ✅ Wrapped in DEBUG flag — acceptable
#endif

// ❌ Unused imported frameworks
import Combine  // ❌ If you're not using any Combine code

// ❌ Empty protocol conformances
extension MyClass: CustomStringConvertible {
    var description: String { "" }  // ❌ Empty or TODO
}

// ❌ Unreachable code
func calculate() -> Int {
    return 42
    let unused = 10  // ❌ Unreachable
}
```

### Unused Assets Detection
```bash
# Check for unused image assets:
# Install: brew install fui (Find Unused Images)
fui find

# Or manual approach — search for each asset name in code:
find . -name "*.swift" -exec grep -l "imageName" {} \;

# Check for unused color assets similarly
```

---

## 6. Performance Audit {#performance}

### Main Thread Checklist
```swift
// ✅ Every database/network/file operation must be off MainActor
// Run Xcode's Main Thread Checker: Product → Scheme → Edit Scheme → 
// Diagnostics → Main Thread Checker: ON

actor DataRepository {
    // ✅ All heavy work happens here, off main thread
    func fetchItems() async throws -> [Item] {
        try await Task.detached {
            // heavy computation
        }.value
    }
}

@MainActor
final class ViewModel: ObservableObject {
    func loadData() async {
        let items = try? await DataRepository.shared.fetchItems()
        // ✅ Back on MainActor automatically for UI update
        self.items = items ?? []
    }
}
```

### Memory & Retain Cycle Audit
```swift
// ✅ Check for retain cycles with [weak self]:
// In closures that capture self in long-lived context:
NotificationCenter.default.addObserver(forName: .myNotification, object: nil, queue: nil) { [weak self] _ in
    self?.handleNotification()
}

// In Task captures — if self outlives the Task, use [weak self]:
Task { [weak self] in
    await self?.loadData()
}

// ✅ Use Instruments → Leaks to verify:
// Profile → Instruments → Leaks
// Look for red leak indicators
```

### Image Performance
```swift
// ✅ Always use AsyncImage with proper caching:
AsyncImage(url: imageURL) { phase in
    switch phase {
    case .success(let image):
        image.resizable().scaledToFill()
            .transaction { $0.animation = nil }  // ✅ Prevents flash
    case .failure:
        placeholderView
    case .empty:
        ProgressView()
    @unknown default:
        EmptyView()
    }
}

// ✅ For high-frequency image loading (lists, grids), use URLCache:
let config = URLSessionConfiguration.default
config.urlCache = URLCache(memoryCapacity: 50_000_000, diskCapacity: 200_000_000)
```

---

## 7. Accessibility Audit {#accessibility}

### Automated Testing
```swift
// ✅ Add accessibility snapshot tests:
func testAccessibilityLabels() {
    let view = ContentView()
    let vc = UIHostingController(rootView: view)
    // Use Xcode's Accessibility Inspector to verify all elements
}

// Run in Terminal against Simulator:
// xcrun simctl accessibility <device-id> audit
```

### Manual Audit Steps
1. **VoiceOver test** — enable VoiceOver, navigate entire app with swipe/tap
   - Every interactive element must be reachable and have a useful label
   - Logical reading order (top-to-bottom, left-to-right)
2. **Dynamic Type test** — Settings → Accessibility → Larger Text → max size
   - No text truncation that hides critical information
   - No layout overflow/overlap
3. **Reduce Motion test** — Settings → Accessibility → Reduce Motion → ON
   - All animations must have a non-motion fallback
4. **Color Contrast test** — use Xcode's Accessibility Inspector → Color Contrast
   - All text meets 4.5:1 minimum
5. **Button size test** — all tap targets minimum 44×44pt

### Accessibility Red Flags in Code
```swift
// ❌ Image without label:
Image("decorative-wave")  // Is this decorative or meaningful?

// ✅ Decorative image (hidden from VoiceOver):
Image("decorative-wave").accessibilityHidden(true)

// ✅ Meaningful image:
Image("profile-photo").accessibilityLabel("Profile photo of \(user.name)")

// ❌ Custom button without label:
Button { action() } label: { Image(systemName: "chevron.right") }

// ✅ With label:
Button { action() } label: { Image(systemName: "chevron.right") }
    .accessibilityLabel("Show details")
```

---

## 8. Localization Audit {#localization}

### Required for Any App Targeting Global Markets
```swift
// ✅ Use String Catalogs (Xcode 15+):
// File → New → String Catalog
// Xcode auto-discovers all localizable strings on build

// ✅ Every user-visible string must be localizable:
Text("Settings")           // ✅ SwiftUI Text is auto-localized
Text(verbatim: "Settings") // ❌ verbatim skips localization
String(localized: "settings.title")  // ✅ For non-SwiftUI contexts

// ❌ Hardcoded strings:
Text("Welcome back, \(name)!")  // ❌ If targeting multiple languages

// ✅ Localized with format:
Text("welcome.back \(name)")  // ✅ Key with interpolation in String Catalog
```

### Localization Testing Checklist
```bash
# Test in pseudo-language (catches untranslated strings):
# Scheme → Edit → Options → App Language → Accented Pseudo-Language

# Test RTL (right-to-left layout):
# Scheme → Edit → Options → App Language → Right-to-Left Pseudo-Language

# Test with longest language (German expands text ~30%):
# Set device language to German; verify no truncation
```

---

## 9. Pre-Submission Final Checklist {#final}

Run through this before EVERY App Store submission:

### Code Quality
- [ ] `swiftlint lint --strict` passes with zero violations
- [ ] `swiftformat . --lint` shows no formatting issues  
- [ ] `periphery scan` shows no unused declarations
- [ ] Zero compiler warnings (Xcode build log)
- [ ] Zero force-unwraps `!` in non-init production paths
- [ ] All TODO/FIXME comments are tracked (none forgotten)

### Functionality
- [ ] App cold-launches in under 400ms on iPhone 11 (minimum supported)
- [ ] App works with no internet connection (graceful degradation)
- [ ] All user-facing errors show meaningful messages (no raw errors)
- [ ] Deep links / universal links all work
- [ ] Push notifications work in production (not just sandbox)
- [ ] In-app purchases work in Sandbox and Production

### Platform Integration
- [ ] Dark mode: every screen tested in dark mode
- [ ] Dynamic Type: every screen at max text size
- [ ] Landscape: tested if app supports both orientations
- [ ] iPad: tested on iPad if universal app
- [ ] Notch / Dynamic Island: no UI hidden behind system chrome

### Privacy & Security  
- [ ] Privacy Nutrition Label accurately reflects data collected
- [ ] All permission descriptions explain why permission is needed
- [ ] No personal data in logs
- [ ] API keys not in source code (use environment variables / Secrets.xcconfig)
- [ ] App Transport Security: no exceptions unless justified

### App Store Assets
- [ ] App icon: all three variants (light, dark, tinted) provided
- [ ] Screenshots: all required device sizes captured
- [ ] App Preview video (optional but increases conversion 25%)
- [ ] App Store description has localized versions for target markets
- [ ] Keywords optimized for ASO

### Testing
- [ ] Unit test coverage > 80% for business logic
- [ ] UI tests cover critical user flows (onboarding, purchase, core loop)
- [ ] Tested on physical device (not just Simulator)
- [ ] TestFlight beta with at least 5 external testers
- [ ] Crash-free rate > 99.5% in TestFlight
