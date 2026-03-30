# Design Intelligence Reference

A complete design system for building A+ iOS apps. Read this whenever making visual design decisions, choosing colors, planning animations, or designing UI components.

## Table of Contents
1. [Visual Hierarchy Protocol](#visual-hierarchy)
2. [Color Psychology & Palette System](#color)
3. [Typography Scale](#typography)
4. [Motion Intent Taxonomy](#motion)
5. [Component Design Rules](#components)
6. [Icon & Asset Design](#icons)
7. [App Icon Excellence](#app-icons)
8. [Splash Screen / Launch Screen Design](#splash)
9. [Dark Mode Rules](#dark-mode)
10. [Spacing & Layout Grid](#spacing)

---

## 1. Visual Hierarchy Protocol {#visual-hierarchy}

Every screen has exactly ONE primary action. Never two. Use this priority stack:

```
LEVEL 1 — Primary CTA: Filled button, high-contrast, 50pt+ height
LEVEL 2 — Secondary content: Cards with .regularMaterial, moderate shadow
LEVEL 3 — Supporting text: .secondary color, smaller font weight
LEVEL 4 — Tertiary/decorative: Ultra-thin material, ghosted icons
```

**F-pattern and Z-pattern reading:**
- Long-form content (settings, lists): F-pattern — most important content top-left
- Promotional / hero screens: Z-pattern — logo top-left → CTA bottom-right
- Card grids: Center of card gets 70% visual weight; put key data there

**60/30/10 Color Rule — always:**
- 60% neutral (background, cards) — `.systemBackground`, `.secondarySystemBackground`
- 30% brand color (headers, selected states, active icons)
- 10% accent (CTAs, highlights, badges, notifications)

---

## 2. Color Psychology & Palette System {#color}

### Never use pure black or white
```swift
// ❌ Never
Color(.black) // Too harsh, creates visual tension
Color(.white) // Flattens everything

// ✅ Always use Apple's semantic system colors
Color(.label)              // Adapts: near-black in light, near-white in dark
Color(.systemBackground)   // Adapts: pure white-ish in light, near-black in dark
Color(.secondaryLabel)     // 60% opacity label — perfect for subtitles
Color(.tertiaryLabel)      // 30% opacity label — hints, placeholders
```

### Industry-Specific Color Psychology

| App Category | Primary Palette | Accent | Avoid |
|---|---|---|---|
| Finance / Trust | Navy, Slate, Deep Blue | Teal, Gold | Red (loss fear), Neon |
| Health / Wellness | Sage Green, Warm White | Coral, Amber | Dark backgrounds |
| Fitness / Energy | Dark BG (#1C1C1E), High contrast | Electric Blue, Orange | Pastel (weak) |
| Premium / Luxury | Near-Black (#1C1C1E), Dark Charcoal | Gold (#C9A84C), Platinum | Bright primaries |
| Kids / Education | Warm Yellow, Sky Blue, Coral | Playful Purple | Dark, muted tones |
| Productivity | Clean White, Light Gray | System Blue, Indigo | Too many colors |
| Social / Community | Vibrant gradients | Brand accent | Cold/corporate |
| Food / Restaurant | Warm Cream, Tan | Tomato Red, Gold | Clinical white |

### Liquid Glass-Compatible Gradients
```swift
// Premium gradient overlay for hero sections
LinearGradient(
    colors: [
        Color(.systemBackground).opacity(0),
        Color(.systemBackground).opacity(0.8),
        Color(.systemBackground)
    ],
    startPoint: .top,
    endPoint: .bottom
)

// Subtle brand tint for glass cards
RoundedRectangle(cornerRadius: 24, style: .continuous)
    .fill(.regularMaterial)
    .overlay(
        RoundedRectangle(cornerRadius: 24, style: .continuous)
            .fill(brandColor.opacity(0.06))  // 4-8% max opacity tint
    )
```

### Accessibility Color Rules (WCAG AA minimum)
- Body text: minimum 4.5:1 contrast ratio vs background
- Large text (18pt+): minimum 3:1 contrast ratio
- Interactive elements: minimum 3:1 against adjacent colors
- Never use color alone to convey meaning — always pair with icon or text

---

## 3. Typography Scale {#typography}

### Apple Semantic Typography — ALWAYS use these, never fixed points
```swift
// Hierarchy from largest to smallest:
.font(.largeTitle)      // 34pt — Hero titles, splash screens
.font(.title)           // 28pt — Section headers
.font(.title2)          // 22pt — Card headers, navigation titles
.font(.title3)          // 20pt — Sub-section headers
.font(.headline)        // 17pt semibold — Primary labels, button text
.font(.body)            // 17pt — Standard body text
.font(.callout)         // 16pt — Supporting info
.font(.subheadline)     // 15pt — Secondary labels
.font(.footnote)        // 13pt — Legal text, timestamps
.font(.caption)         // 12pt — Metadata, helper text
.font(.caption2)        // 11pt — Absolute minimum, use sparingly

// For weight variations:
.font(.title2.bold())
.font(.title2.weight(.semibold))
.font(.body.monospaced())     // Numbers, code, metrics
```

### Custom Scaled Metrics (for icons, spacing that must scale with Dynamic Type)
```swift
@ScaledMetric(relativeTo: .body) var iconSize: CGFloat = 24
@ScaledMetric(relativeTo: .headline) var avatarSize: CGFloat = 44
```

### Typography Best Practices
- Line length: 45–75 characters per line (use `.lineLimit` with wrapping)
- Line spacing: `lineSpacing(4)` for body text; 0 for headlines
- Kerning: `kerning(-0.5)` for display/hero text makes it feel premium
- Tracking tight on large text; default on body: `tracking(-0.3)` for titles

---

## 4. Motion Intent Taxonomy {#motion}

Every animation must have a purpose. Use this taxonomy:

```swift
enum MotionIntent {
    case confirm     // User completed an action → spring bounce + haptic
    case guide       // Lead attention to next step → subtle pulse or slide-in
    case reveal      // Content appearing → fade + upward slide
    case dismiss     // Content leaving → fade + scale down
    case celebrate   // Achievement unlocked → burst + confetti + bounce
    case error       // Something went wrong → horizontal shake
    case loading     // Waiting → shimmer or rotation (no bounce)
    case transition  // Navigation → slide + opacity fade
}
```

### Animation Values by Intent
```swift
// confirm — spring with tactile feel
.animation(.spring(duration: 0.35, bounce: 0.4), value: isConfirmed)

// reveal — enters from below, fades in
.transition(.asymmetric(
    insertion: .move(edge: .bottom).combined(with: .opacity),
    removal: .opacity.animation(.easeIn(duration: 0.15))
))

// error — shake left-right
func shakeAnimation() -> some View {
    modifier(ShakeEffect(animatableData: shakeCount))
}
struct ShakeEffect: GeometryEffect {
    var animatableData: CGFloat
    func effectValue(size: CGSize) -> ProjectionTransform {
        let translation = sin(animatableData * .pi * 2) * 8
        return ProjectionTransform(CGAffineTransform(translationX: translation, y: 0))
    }
}

// celebrate — scale burst
.scaleEffect(isCelebrating ? 1.15 : 1.0)
.animation(.spring(duration: 0.5, bounce: 0.6), value: isCelebrating)

// loading — shimmer (Metal shader preferred; fallback below)
struct ShimmerModifier: ViewModifier {
    @State private var phase: CGFloat = -1
    func body(content: Content) -> some View {
        content.overlay(
            LinearGradient(
                colors: [.clear, .white.opacity(0.4), .clear],
                startPoint: UnitPoint(x: phase, y: 0.5),
                endPoint: UnitPoint(x: phase + 0.5, y: 0.5)
            )
        )
        .onAppear {
            withAnimation(.linear(duration: 1.2).repeatForever(autoreverses: false)) {
                phase = 1.5
            }
        }
    }
}
```

### Always Gate Animations Behind Reduce Motion
```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion

var springAnimation: Animation {
    reduceMotion ? .none : .spring(duration: 0.4, bounce: 0.3)
}
```

---

## 5. Component Design Rules {#components}

### Corner Radius Scale (must use `.continuous` style always)
```swift
// Sizes and use cases:
32pt — Hero cards, modal sheets, large containers
28pt — Standard cards, feature tiles
20pt — Buttons (large), image thumbnails
16pt — Buttons (medium), input fields
12pt — Tags, badges, chips, small buttons
8pt  — Inline highlights, tooltips
4pt  — Never go below this
```

### Button Hierarchy
```swift
// PRIMARY — filled, high contrast, 50pt minimum height
Button("Get Started") { }
    .buttonStyle(.borderedProminent)
    .controlSize(.large)
    .frame(maxWidth: .infinity, minHeight: 50)
    .cornerRadius(16, antialiased: true)

// SECONDARY — outlined or tinted
Button("Learn More") { }
    .buttonStyle(.bordered)
    .tint(.primary)

// TERTIARY — plain text, destructive actions
Button("Skip", role: .cancel) { }
    .buttonStyle(.plain)
    .foregroundStyle(.secondary)

// DESTRUCTIVE — never use prominent style for destructive
Button("Delete", role: .destructive) { }
    .buttonStyle(.bordered)  // Not .borderedProminent
```

### Card Design Template
```swift
struct DesignSystemCard<Content: View>: View {
    var elevation: CardElevation = .regular
    @ViewBuilder let content: Content

    var body: some View {
        content
            .padding(20)
            .background(elevation.material, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 24, style: .continuous)
                    .strokeBorder(.white.opacity(elevation.borderOpacity), lineWidth: 1)
            )
            .shadow(color: elevation.shadowColor, radius: elevation.shadowRadius, x: 0, y: elevation.shadowY)
    }

    enum CardElevation {
        case flat, regular, raised, floating

        var material: AnyShapeStyle {
            switch self {
            case .flat: return AnyShapeStyle(.ultraThinMaterial)
            case .regular: return AnyShapeStyle(.regularMaterial)
            case .raised: return AnyShapeStyle(.thickMaterial)
            case .floating: return AnyShapeStyle(.ultraThickMaterial)
            }
        }
        var borderOpacity: Double { [0.08, 0.18, 0.22, 0.25][ordinal] }
        var shadowRadius: CGFloat { [0, 12, 20, 30][ordinal] }
        var shadowY: CGFloat { [0, 4, 8, 12][ordinal] }
        var shadowColor: Color { Color(.sRGBLinear, white: 0, opacity: [0, 0.08, 0.12, 0.18][ordinal]) }
        private var ordinal: Int {
            switch self { case .flat: return 0; case .regular: return 1; case .raised: return 2; case .floating: return 3 }
        }
    }
}
```

---

## 6. Icon & Asset Design {#icons}

### SF Symbols First Rule (iOS 26 — 6,000+ symbols)
Before creating ANY custom icon: search SF Symbols 6 app. If a symbol exists, use it.
```swift
// Size weights for different contexts:
Image(systemName: "star.fill")
    .symbolRenderingMode(.hierarchical)  // Multi-color depth
    .foregroundStyle(.yellow)
    .font(.system(size: 24, weight: .semibold))

// For animated symbols (iOS 17+):
Image(systemName: "heart.fill")
    .symbolEffect(.bounce, value: isLiked)
    .symbolEffect(.pulse, isActive: isLoading)
    .symbolEffect(.variableColor.iterative, isActive: isStreaming)
    .contentTransition(.symbolEffect(.replace.magic(fallback: .replace)))
```

### Custom Icon Requirements
When SF Symbols doesn't have what you need:
- Design at 28×28 points master size (vector PDF or SVG → `.xcassets`)
- Provide 1x, 2x, 3x PNG variants if rasterized
- Use 2pt stroke weight minimum
- Match SF Symbols visual style: slightly rounded endpoints, consistent weight
- Test at 16pt, 24pt, 44pt sizes

---

## 7. App Icon Excellence {#app-icons}

### Technical Requirements
```
Master size: 1024×1024 px PNG, sRGB, no transparency, no rounded corners
(Xcode / App Store generates all other sizes automatically)

Required variants per iOS 26 HIG:
- Light mode icon (standard)
- Dark mode icon (no solid background — Apple provides dark BG)
- Tinted icon (monochrome, Apple applies system tint)

Optional but strongly recommended:
- Alternate icons for events/seasons (SwiftUI API: UIApplication.shared.setAlternateIconName)
```

### App Icon Design Principles
1. **Single concept** — one clear symbol, not a scene. Recognizable at 29×29px
2. **No text** unless it IS the logo (e.g., a bank's wordmark)
3. **No iOS chrome** — no screenshots, no device bezels, no App Store UI
4. **Bold at small sizes** — thin lines disappear; use 8pt+ stroke weights in the master
5. **Safe zone** — keep critical elements within 85% of the canvas (Apple clips corners)
6. **Squircle-aware** — Apple applies ~20% corner radius; test by masking preview
7. **Avoid gradient-only backgrounds** — add subtle texture or depth
8. **Dark variant** — for dark mode, use transparent/cutout design, Apple provides dark BG

### AI-Generated App Icon Prompt Formula
When generating via FLUX or similar image models, use this structure:
```
"[Style] app icon for [app concept], [main symbol/subject], [material/texture], 
[lighting], [color palette], flat square 1024x1024, no text, no shadows, 
no rounded corners, clean professional App Store quality"

Examples:
"Minimalist flat app icon for a meditation app, abstract lotus flower made of 
translucent glass layers, soft iridescent teal and lavender, soft studio lighting, 
clean white background, flat square, no text, App Store quality"

"3D rendered app icon for a finance tracker, gold coin with rising bar chart embossed, 
deep navy background with subtle gradient, studio lighting with rim light, 
premium luxury feel, no text, flat square 1024x1024"
```

---

## 8. Splash Screen / Launch Screen Design {#splash}

### iOS 26 Launch Screen Requirements
- Must use `LaunchScreen.storyboard` or `Info.plist UILaunchScreen` (NOT a LaunchScreen.xib)
- Never show fake loading progress — Apple guidelines prohibit it
- Duration goal: under 400ms total (fast launch = best experience)
- Must match the app's initial view so the transition is seamless

### Launch Screen Architecture
```swift
// Recommended: Use UILaunchScreen in Info.plist (simplest, no storyboard needed)
// Info.plist entry:
// UILaunchScreen → UIImageName: "LaunchLogo" (1024×1024 centered)
//                → UIBackgroundColor: "LaunchBackground" (system asset)

// For animated splash (SwiftUI-based, shown after real launch):
struct SplashView: View {
    @State private var logoScale: CGFloat = 0.7
    @State private var logoOpacity: Double = 0
    @State private var isReady = false

    var body: some View {
        ZStack {
            Color(.systemBackground).ignoresSafeArea()

            VStack(spacing: 24) {
                Image("AppLogo")  // Your 512×512 logo
                    .resizable()
                    .scaledToFit()
                    .frame(width: 120, height: 120)
                    .scaleEffect(logoScale)
                    .opacity(logoOpacity)

                Text(appName)
                    .font(.title.bold())
                    .opacity(logoOpacity)
            }
        }
        .onAppear {
            withAnimation(.spring(duration: 0.6, bounce: 0.4)) {
                logoScale = 1.0
                logoOpacity = 1.0
            }
            // Transition to main app after brief delay
            Task {
                try? await Task.sleep(for: .milliseconds(1200))
                await MainActor.run { isReady = true }
            }
        }
    }
}
```

### Splash Screen Visual Design Principles
1. **Brand first** — logo center-stage, nothing competing
2. **Single color background** — use brand color or `.systemBackground` for seamless handoff
3. **Generous whitespace** — logo should be 20–30% of screen height maximum
4. **Tagline optional** — if included, max 5 words, `.title3` or smaller
5. **No UI chrome** — no buttons, no navigation, no progress indicators
6. **Liquid Glass optional** — a subtle material card behind logo can look premium

### AI-Generated Splash Screen Prompt Formula
```
"iOS app splash screen design, [app name] [category], [brand color] background,
centered [logo description] logo, clean minimalist, premium quality,
1290×2796 pixels (iPhone 15 Pro Max), no UI elements, no buttons,
suitable for Apple App Store, [style: modern/playful/luxury/tech]"
```

---

## 9. Dark Mode Rules {#dark-mode}

```swift
// ALWAYS test every view in both light and dark:
#Preview("Dark") {
    ContentView()
        .preferredColorScheme(.dark)
}
#Preview("Light") {
    ContentView()
        .preferredColorScheme(.light)
}

// Never hardcode colors — always use semantic or adaptive:
// ❌ Never
.foregroundColor(Color(red: 0.1, green: 0.1, blue: 0.1))

// ✅ Always
.foregroundStyle(.primary)          // Adapts automatically
.foregroundStyle(.secondary)
Color(.systemBackground)            // Adapts
Color(.secondarySystemBackground)   // Adapts

// For brand colors that need dark variants:
extension Color {
    static let brandPrimary = Color("BrandPrimary")  // Define in Assets.xcassets
    // In asset catalog: set light variant AND dark variant
}
```

---

## 10. Spacing & Layout Grid {#spacing}

### 8pt Grid System (the standard)
```swift
// All spacing values should be multiples of 4 or 8:
// 4, 8, 12, 16, 20, 24, 32, 40, 48, 64

// Standard padding values:
let screenEdge: CGFloat = 20        // Left/right screen edge padding
let cardPadding: CGFloat = 16       // Inside cards
let sectionSpacing: CGFloat = 24    // Between major sections
let itemSpacing: CGFloat = 12       // Between list items
let iconTextSpacing: CGFloat = 8    // Between icon and label
let tightSpacing: CGFloat = 4       // Between related elements

// Component spacing extension:
extension CGFloat {
    static let xs: CGFloat = 4
    static let sm: CGFloat = 8
    static let md: CGFloat = 16
    static let lg: CGFloat = 24
    static let xl: CGFloat = 32
    static let xxl: CGFloat = 48
}
```

### Safe Area & Device Adaptations
```swift
// Always respect safe areas — never overlap system UI:
.padding(.bottom, 90)  // ❌ Hardcoded — breaks on notch vs Dynamic Island

// ✅ Correct approach:
.safeAreaInset(edge: .bottom) {
    TabBarView()  // Or any persistent bottom UI
}

// For Dynamic Island awareness:
GeometryReader { proxy in
    let topInset = proxy.safeAreaInsets.top  // 59pt on Dynamic Island, 44pt on notch, 20pt on SE
}
```
