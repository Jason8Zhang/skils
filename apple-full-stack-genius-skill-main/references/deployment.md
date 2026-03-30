# Deployment, CI/CD, and App Store Best Practices

## Xcode Cloud Setup

Xcode Cloud is Apple's native CI/CD — zero third-party dependencies, deeply integrated with TestFlight.

### xcode-cloud.yml (in .xcode/workflows/)

Xcode Cloud uses a web-based workflow editor, not YAML — but here's the conceptual equivalent:

**Build for TestFlight (every push to `main`):**
1. **Start Condition**: Push to `main` branch
2. **Environment**: Xcode 16+, macOS Sequoia, iOS 18 SDK
3. **Actions**:
   - Build (scheme: MyApp, configuration: Release)
   - Test (run all unit tests + UI tests on iPhone 16 simulator)
   - Archive (automatic signing)
   - TestFlight Internal — push to internal testers automatically
4. **Post-Build**: Send Slack/email notification

**Production Release workflow (manual trigger):**
1. Archive
2. Notarize (for macOS)
3. Submit to App Store Review (manual — don't auto-submit)
4. Phased release (7-day rollout)

### ci_scripts/ (Run Script Actions for Xcode Cloud)

```bash
#!/bin/sh
# ci_scripts/ci_post_clone.sh
# Runs after repo clone — set up environment

set -e

# Install Tuist if used for project generation
# curl -Ls https://install.tuist.io | bash

# Set build number from CI environment
if [[ -n "$CI_BUILD_NUMBER" ]]; then
    xcrun agvtool new-version -all $CI_BUILD_NUMBER
fi

echo "Post-clone setup complete"
```

---

## Versioning Strategy

```
Marketing version (CFBundleShortVersionString): MAJOR.MINOR.PATCH  → e.g., 2.4.1
Build number (CFBundleVersion): auto-incremented by Xcode Cloud  → e.g., 847
```

In Xcode Cloud, let it manage build numbers automatically:
- Project → Build Settings → `CURRENT_PROJECT_VERSION = $(CI_BUILD_NUMBER)`
- Or use `agvtool` in ci_post_clone script

---

## TestFlight Distribution Strategy

| Group | Who | Trigger |
|---|---|---|
| Internal (5 people) | Dev team | Every commit to `main` |
| Beta (up to 10,000) | Power users, press | Manual push weekly |
| Public Beta | Everyone | Optional; App Store listing |

```swift
// Check if running in TestFlight to show beta UI/debug info
var isRunningInTestFlight: Bool {
    guard let receiptURL = Bundle.main.appStoreReceiptURL else { return false }
    return receiptURL.lastPathComponent == "sandboxReceipt"
}
```

---

## App Store Connect Checklist

Before submitting each build:

### Metadata
- [ ] App name (30 char max), subtitle (30 char)
- [ ] Description (4000 char) — use keywords naturally in first 255 chars
- [ ] Keywords field (100 char, comma-separated, NO spaces after commas)
- [ ] What's new in this version (4000 char — write for real users, not engineers)
- [ ] Screenshots for all required sizes:
  - iPhone 6.9" (iPhone 16 Pro Max)
  - iPhone 6.7" (iPhone 15 Plus)
  - iPad Pro 13" (M4)
  - iPad Pro 11" (M4)
- [ ] App Preview video (optional but boosts conversion 30%+)

### Privacy Nutrition Label
Fill out **honestly** — App Store Review will reject if your app collects data you didn't disclose:

```
Data Used to Track You:         ← linked to identity, used for tracking
Data Linked to You:             ← linked to account/device
Data Not Linked to You:         ← anonymous/diagnostic only
```

Common categories: Name, Email Address, User Content, Identifiers, Usage Data, Diagnostics

### App Review Information
- [ ] Demo account credentials (if app requires login)
- [ ] Notes for reviewer explaining non-obvious features
- [ ] Contact email (monitored — reviewers sometimes email)

---

## Phased Release (Always Use)

After approval, use phased release to catch regressions before full rollout:

- Day 1–2: 1% of users
- Day 3–4: 2%
- Day 5–6: 5%
- Day 7: 10%
- Day 8: 20%
- Day 9: 50%
- Day 10: 100%

You can pause or halt rollout at any time via App Store Connect if crash rates spike.

**Monitor via:** Xcode Organizer → Crashes, MetricKit, your own analytics (if privacy-preserving).

---

## ASO (App Store Optimization)

**Keyword research:**
- Use AppFollow, Sensor Tower, or App Annie for competitor keyword gaps
- Target keywords with **medium competition + medium-high traffic** (not the top-10 obvious ones)
- Primary categories: choose both a main and a secondary category wisely

**Conversion optimization:**
1. First 2 screenshots carry 80% of the weight — make them show the core value
2. Use device mockups (real iPhone/iPad frames)
3. Feature text overlay on screenshots — big, bold, benefit-first
4. App icon: test variations with App Store Connect Product Page Optimization A/B test

---

## StoreKit 2 — Subscriptions

```swift
// StoreService.swift
@MainActor
final class StoreService: ObservableObject {
    @Published private(set) var purchasedProductIDs: Set<String> = []
    @Published private(set) var products: [Product] = []

    private var transactionListener: Task<Void, Error>?

    init() {
        transactionListener = listenForTransactions()
        Task { await loadProducts() }
    }

    func loadProducts() async {
        do {
            products = try await Product.products(for: [
                "com.yourapp.pro.monthly",
                "com.yourapp.pro.yearly"
            ])
        } catch {
            print("Product load failed: \(error)")
        }
    }

    func purchase(_ product: Product) async throws {
        let result = try await product.purchase()
        switch result {
        case .success(let verification):
            let transaction = try checkVerified(verification)
            await updatePurchasedProducts()
            await transaction.finish()
        case .userCancelled, .pending:
            break
        @unknown default:
            break
        }
    }

    // CRITICAL: Always listen for transactions on launch
    // Handles: renewals, refunds, upgrades, StoreKit testing
    private func listenForTransactions() -> Task<Void, Error> {
        Task.detached {
            for await result in Transaction.updates {
                if let transaction = try? self.checkVerified(result) {
                    await self.updatePurchasedProducts()
                    await transaction.finish()
                }
            }
        }
    }

    private func updatePurchasedProducts() async {
        var purchased: Set<String> = []
        for await result in Transaction.currentEntitlements {
            if let transaction = try? checkVerified(result) {
                purchased.insert(transaction.productID)
            }
        }
        purchasedProductIDs = purchased
    }

    private func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified: throw StoreError.failedVerification
        case .verified(let value): return value
        }
    }
}

enum StoreError: Error {
    case failedVerification
}
```

---

## Passkeys (Sign In with No Password)

```swift
// PasskeyAuthService.swift
import AuthenticationServices

@MainActor
final class PasskeyAuthService: NSObject, ASAuthorizationControllerDelegate {
    func registerPasskey(for userID: String, username: String) {
        let provider = ASAuthorizationPlatformPublicKeyCredentialProvider(
            relyingPartyIdentifier: "yourapp.com"  // Must match Associated Domains
        )
        let request = provider.createCredentialRegistrationRequest(
            challenge: generateChallenge(),
            name: username,
            userID: userID.data(using: .utf8)!
        )
        let controller = ASAuthorizationController(authorizationRequests: [request])
        controller.delegate = self
        controller.presentationContextProvider = self
        controller.performRequests()
    }

    func authorizationController(
        controller: ASAuthorizationController,
        didCompleteWithAuthorization authorization: ASAuthorization
    ) {
        switch authorization.credential {
        case let credential as ASAuthorizationPlatformPublicKeyCredentialRegistration:
            // Send credential.rawAttestationObject to your server
            Task { await APIClient.shared.registerPasskey(credential) }
        case let credential as ASAuthorizationPlatformPublicKeyCredentialAssertion:
            // Send credential.rawAuthenticatorData + signature to server for verification
            Task { await APIClient.shared.verifyPasskey(credential) }
        default:
            break
        }
    }
}
```

---

## MetricKit — Production Performance Monitoring

```swift
// AppDelegate.swift (or @main struct)
import MetricKit

class MetricKitSubscriber: NSObject, MXMetricManagerSubscriber {
    override init() {
        super.init()
        MXMetricManager.shared.add(self)
    }

    // Called at most once per day with the previous 24h of data
    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            // Analyze hang rate, launch time, memory usage
            if let launchMetrics = payload.applicationLaunchMetrics {
                let timeToFirstDraw = launchMetrics.histogrammedTimeToFirstDraw
                // Log to your analytics backend (privacy-preserving aggregates only)
            }
        }
    }

    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        for payload in payloads {
            // Crash logs, disk write exceptions, hang reports
            if let crashDiagnostics = payload.crashDiagnostics {
                // Forward to Sentry/Crashlytics or your own pipeline
            }
        }
    }
}
```
