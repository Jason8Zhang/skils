# AI Image Generation & Asset Pipeline

Complete guide to generating high-end images, app icons, splash screens, and in-app visual assets. Read this whenever the user needs app icons, splash screens, logos, or in-app imagery.

## Table of Contents
1. [Image Generation Strategy](#strategy)
2. [App Icon Generation](#app-icon)
3. [Splash Screen Generation](#splash)
4. [Logo Generation](#logo)
5. [In-App AI Imagery](#in-app)
6. [Swift Image Service](#swift-service)
7. [Asset Pipeline & Xcode Integration](#asset-pipeline)
8. [Prompt Engineering for App Assets](#prompts)

---

## 1. Image Generation Strategy {#strategy}

### Provider Hierarchy (2026)
Use this priority order for generating app assets:

```
1. FLUX.2 [pro] via fal.ai     → Production app icons, splash screens, marketing assets
   Model: "fal-ai/flux-2-pro"   Pricing: ~$0.03/megapixel   Quality: ⭐⭐⭐⭐⭐

2. FLUX.2 [max] via fal.ai     → Maximum quality hero images
   Model: "fal-ai/flux-2-max"   Pricing: higher             Quality: ⭐⭐⭐⭐⭐

3. FLUX.1 [schnell] via fal.ai → Fast iterations, previews
   Model: "fal-ai/flux/schnell" Pricing: ~$0.003/image      Quality: ⭐⭐⭐⭐

4. GPT Image (gpt-image-1.5)   → When text rendering in image needed
   via OpenAI API               Pricing: ~$0.04/image

Note: ALWAYS route through Vapor backend proxy — NEVER expose API keys in iOS client.
```

### When to Use Each
- **App icon**: FLUX.2 [pro] — needs maximum quality, used everywhere
- **Splash screen background**: FLUX.2 [pro] or FLUX.2 [max]
- **In-app illustrations**: FLUX.1 [dev] or FLUX.1 [schnell] for speed
- **Quick preview/iteration**: FLUX.1 [schnell] (1–2 seconds)
- **Text in image needed**: GPT Image (FLUX struggles with text)

---

## 2. App Icon Generation {#app-icon}

### Master Prompt Templates

**Minimalist / Premium style:**
```
Minimalist iOS app icon for [APP_CONCEPT], [MAIN_SYMBOL] rendered in [MATERIAL: frosted glass/
polished metal/soft matte/glossy ceramic], [COLOR_PALETTE], soft studio lighting with 
subtle reflection, clean white background, perfectly centered, no text, no shadows on 
background, flat square composition, ultra-high quality App Store icon, 1024x1024
```

**3D Rendered style:**
```
3D rendered iOS app icon for [APP_CONCEPT], [MAIN_SYMBOL] centered, depth and dimension,
[COLOR_PALETTE] with subtle gradient, professional studio lighting, rim lighting effect,
photorealistic material quality, isolated on [SOLID_COLOR] background, no text,
perfectly square composition, premium App Store quality, 1024x1024
```

**Illustrated / Flat style:**
```
Flat vector iOS app icon, [APP_CONCEPT], bold [MAIN_SYMBOL], [COLOR_1] and [COLOR_2]
color palette, clean geometric shapes, modern minimalism, no gradients, no shadows,
solid background, professional design, no text, App Store ready, 1024x1024
```

**Liquid Glass style (iOS 26 aesthetic):**
```
iOS 26 Liquid Glass app icon for [APP_CONCEPT], [MAIN_SYMBOL] made of translucent
glass material, light refracting through edges, subtle iridescent sheen, 
[BASE_COLOR] with glass overlay, depth and layers, frosted glass texture,
premium Apple design aesthetic, no text, flat square, 1024x1024
```

### App Icon Variants (all three required for iOS 26)

**Dark mode variant prompt addition:**
```
...same icon but designed for dark mode, no background (transparent), 
icon elements only on transparent/dark background, will be placed on 
Apple's system dark background automatically
```

**Tinted variant prompt:**
```
...monochrome version of the same icon, single color [#FFFFFF or brand color],
silhouette/outline style, for system tinting, transparent background
```

### Post-Generation Processing
After generating the 1024×1024 master:
1. Import to Xcode → Assets.xcassets → AppIcon
2. Set "Single Size" (iOS 26 — Xcode auto-generates all sizes)
3. Add dark variant to "Dark Appearance"  
4. Test on multiple device simulators

---

## 3. Splash Screen Generation {#splash}

### Splash Screen is NOT the Launch Screen
- **LaunchScreen.storyboard**: Static image shown during cold start (system-controlled, fast)
- **SplashView (SwiftUI)**: Animated brand screen shown AFTER launch (your code)

Both should visually match for a seamless experience.

### Launch Screen Background Prompt
```
iPhone app launch screen background for [APP_NAME] [CATEGORY],
[BRAND_COLOR] as dominant color, subtle [TEXTURE: grain/gradient/geometric],
ultra clean and minimal, no UI elements, no text, no buttons,
professional mobile app design, portrait orientation, 
2796x1290 pixels (iPhone 15 Pro Max portrait)
```

### Hero Splash Illustration Prompt
```
Cinematic hero illustration for [APP_CONCEPT] mobile app splash screen,
[VISUAL_METAPHOR: e.g. "floating productivity items in zero gravity"],
[STYLE: isometric 3D / flat illustration / photorealistic],
[COLOR_PALETTE], generous whitespace at center for logo placement,
premium mobile app quality, landscape aspect ratio suitable for full-bleed background,
no text, 2000x1000 pixels
```

---

## 4. Logo Generation {#logo}

### Logomark (symbol only — for app icon, favicon, etc.)
```
Professional logomark for [COMPANY/APP], [CONCEPT/METAPHOR],
clean vector style, scalable design, works at small sizes,
[COLOR_PALETTE: 1-2 colors max], geometric precision,
transparent background, SVG-quality clarity, no text, 
suitable for tech startup / mobile app
```

### Wordmark (text + symbol combined)
```
App logotype for "[APP_NAME]", modern sans-serif wordmark,
[STYLE: tech/playful/premium/minimal], [ACCENT_SYMBOL] integrated with text,
[PRIMARY_COLOR] on white background, professional brand identity,
clean and memorable, App Store marketing quality
```

### Logo Usage Rules (always follow Apple HIG)
- Never place logo within 40pt of screen edges on marketing materials
- Minimum size: 44×44pt (tap target compliance)  
- Always provide 2× and 3× PNG variants in Assets.xcassets
- Maintain contrast ratio ≥ 3:1 against any background it appears on
- Never stretch, rotate, or recolor without explicit brand permission

---

## 5. In-App AI Imagery {#in-app}

### On-Device First (iOS 26 — Foundation Models)
Foundation Models handles text-to-description well, but not image generation.
For on-device image generation: use Core ML with a compressed diffusion model.

```swift
// Check what's available before deciding generation path:
enum ImageGenerationPath {
    case onDeviceCoreML    // Private, offline, ~5-10s, limited quality
    case cloudFalAI        // Best quality, requires network, ~2-3s
    case cloudReplicate    // Alternative, good quality
    
    static func recommend(for quality: ImageQuality, privacyRequired: Bool) -> ImageGenerationPath {
        if privacyRequired { return .onDeviceCoreML }
        switch quality {
        case .preview: return .cloudFalAI  // schnell model, fastest
        case .standard: return .cloudFalAI // dev model
        case .premium: return .cloudFalAI  // pro model
        }
    }
}
```

### Use Cases for In-App Generation
- **Personalized avatars** — generate user avatar from description
- **Recipe illustrations** — "Generate appetizing photo of [dish name]"
- **Travel / Places** — "Generate scenic image of [destination]"
- **Product mockups** — "Show [product] in [lifestyle context]"
- **Story illustrations** — children's book, journaling, creative writing apps

---

## 6. Swift Image Service {#swift-service}

### Architecture: Always proxy through Vapor backend

```swift
// ❌ NEVER: Direct API calls from iOS client (exposes API keys)
// ✅ ALWAYS: Route through your Vapor backend

// iOS Client — ImageGenerationService.swift
actor ImageGenerationService {
    static let shared = ImageGenerationService()
    private let baseURL = URL(string: "https://api.yourvaporapp.com")!
    
    enum GenerationQuality: String {
        case preview = "schnell"    // ~1-2 seconds
        case standard = "dev"       // ~3-5 seconds  
        case premium = "pro"        // ~5-8 seconds
    }
    
    struct GenerationRequest: Codable {
        let prompt: String
        let quality: String
        let width: Int
        let height: Int
        let negativePrompt: String?
    }
    
    struct GenerationResult: Codable {
        let imageURL: URL
        let seed: Int
        let generationTime: Double
    }
    
    func generateImage(
        prompt: String,
        quality: GenerationQuality = .standard,
        size: CGSize = CGSize(width: 1024, height: 1024),
        negativePrompt: String? = nil
    ) async throws -> URL {
        let request = GenerationRequest(
            prompt: enhancePrompt(prompt),
            quality: quality.rawValue,
            width: Int(size.width),
            height: Int(size.height),
            negativePrompt: negativePrompt
        )
        
        var urlRequest = URLRequest(url: baseURL.appendingPathComponent("/api/generate-image"))
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)
        
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw ImageGenerationError.serverError
        }
        
        let result = try JSONDecoder().decode(GenerationResult.self, from: data)
        return result.imageURL
    }
    
    // Automatically enhance prompts for better App Store quality results
    private func enhancePrompt(_ base: String) -> String {
        "\(base), high quality, professional, sharp focus, 8k resolution"
    }
    
    enum ImageGenerationError: Error {
        case networkUnavailable
        case serverError
        case invalidResponse
        case generationFailed(String)
    }
}
```

### Vapor Backend — Image Generation Route
```swift
// Routes/ImageGenerationController.swift
struct ImageGenerationController: RouteCollection {
    func boot(routes: RoutesBuilder) throws {
        routes.post("api", "generate-image", use: generateImage)
    }
    
    @Sendable
    func generateImage(req: Request) async throws -> Response {
        let body = try req.content.decode(GenerationRequestDTO.self)
        
        // Select fal.ai model based on quality
        let modelID: String
        switch body.quality {
        case "schnell": modelID = "fal-ai/flux/schnell"
        case "dev":     modelID = "fal-ai/flux/dev"
        default:        modelID = "fal-ai/flux-2-pro"
        }
        
        let falRequest = FalAIRequest(
            prompt: body.prompt,
            imageSize: FalImageSize(width: body.width, height: body.height),
            numInferenceSteps: body.quality == "schnell" ? 4 : 28,
            guidanceScale: 3.5,
            enableSafetyChecker: true
        )
        
        let headers: HTTPHeaders = [
            "Authorization": "Key \(Environment.get("FAL_API_KEY") ?? "")",
            "Content-Type": "application/json"
        ]
        
        let falResponse = try await req.client.post(
            "https://fal.run/\(modelID)",
            headers: headers
        ) { req in
            try req.content.encode(falRequest, as: .json)
        }
        
        let result = try falResponse.content.decode(FalAIResponse.self)
        
        return Response(
            status: .ok,
            body: .init(data: try JSONEncoder().encode(
                GenerationResultDTO(imageURL: result.images[0].url, seed: result.seed)
            ))
        )
    }
}
```

### SwiftUI Image Generation View
```swift
struct GeneratedImageView: View {
    let prompt: String
    @State private var imageURL: URL?
    @State private var isGenerating = false
    @State private var error: String?
    
    var body: some View {
        Group {
            if let url = imageURL {
                AsyncImage(url: url) { image in
                    image
                        .resizable()
                        .scaledToFill()
                } placeholder: {
                    shimmerPlaceholder
                }
                .transition(.opacity.animation(.easeIn(duration: 0.3)))
            } else if isGenerating {
                shimmerPlaceholder
            } else {
                placeholderThumbnail
            }
        }
        .task { await generate() }
    }
    
    private var shimmerPlaceholder: some View {
        Rectangle()
            .fill(.quaternary)
            .modifier(ShimmerModifier())
    }
    
    @MainActor
    private func generate() async {
        isGenerating = true
        defer { isGenerating = false }
        do {
            imageURL = try await ImageGenerationService.shared.generateImage(prompt: prompt)
        } catch {
            self.error = error.localizedDescription
        }
    }
}
```

---

## 7. Asset Pipeline & Xcode Integration {#asset-pipeline}

### Asset Catalog Organization
```
Assets.xcassets/
├── AppIcon.appiconset/
│   ├── Contents.json          ← single 1024×1024, Xcode generates rest
│   ├── AppIcon-Light@3x.png   ← light mode
│   ├── AppIcon-Dark@3x.png    ← dark mode (transparent bg)
│   └── AppIcon-Tinted@3x.png  ← monochrome tinted
│
├── LaunchAssets/
│   ├── LaunchLogo.imageset/   ← logo for LaunchScreen
│   └── LaunchBG.colorset/     ← launch screen background color
│
├── Brand/
│   ├── LogoFull.imageset/     ← full wordmark, light+dark variants
│   ├── LogoMark.imageset/     ← icon only, light+dark variants
│   └── BrandPrimary.colorset/ ← brand color, light+dark variants
│
├── Illustrations/
│   ├── OnboardingHero1.imageset/
│   ├── EmptyStateDefault.imageset/
│   └── SuccessConfetti.imageset/
│
└── Generated/                 ← AI-generated, cached images
    └── [uuid].imageset/       ← dynamically added at runtime
```

### Image Size Requirements by Context
```
App Icon master:        1024×1024 px
Marketing screenshots:  iPhone 15 Pro Max: 1290×2796 px portrait
                        iPad Pro 13": 2064×2752 px
Launch screen bg:       2796×1290 px (portrait) / 2796×1290 (landscape)
In-app hero image:      1200×600 px (2:1 ratio, loads fast)
Card thumbnail:         600×400 px (3:2 ratio)
Avatar:                 512×512 px
```

---

## 8. Prompt Engineering for App Assets {#prompts}

### Negative Prompts (always add these for cleaner results)
```
Standard negative: "blurry, low quality, watermark, text overlay, 
UI elements, buttons, frames, borders, pixelated, jpeg artifacts,
overexposed, dark shadows, cluttered background"

App icon specific: "text, words, letters, numbers, multiple objects, 
cluttered, border, frame, rounded corners, drop shadow, 
realistic photograph"

In-app imagery: "watermark, copyright text, stock photo watermark,
low resolution, compression artifacts, unrealistic proportions"
```

### Style Reference Keywords by App Category

| Category | Style Keywords |
|---|---|
| Finance | "professional, corporate, sleek, dark blue, gold accents, charts" |
| Health | "clean, medical, trustworthy, teal, soft shadows, organic shapes" |
| Fitness | "dynamic, energetic, dark background, bright accent, athletic" |
| Food | "appetizing, warm lighting, bokeh, lifestyle photography" |
| Travel | "cinematic, golden hour, wide angle, vibrant, wanderlust" |
| Kids | "playful, colorful, cartoon style, friendly characters, soft" |
| Productivity | "minimal, geometric, clean lines, subtle gradient, modern" |
| Luxury | "premium, dark, gold, black, high contrast, exclusive feel" |

### Iteration Strategy
1. Start with FLUX.1 [schnell] for fast $0.003 previews — iterate 5-10 times
2. Once prompt is dialed in, generate final with FLUX.2 [pro] (~$0.03)
3. For icons: always generate 4 variants (different seeds), pick the best
4. Use `seed` parameter to regenerate exact variant with minor prompt tweaks
