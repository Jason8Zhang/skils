# Foundation Models Framework — iOS 26

Complete guide to integrating Apple's on-device 3B parameter LLM. Read this whenever building any AI feature in an iOS app.

## Overview

Foundation Models gives every app access to the same ~3B parameter LLM that powers Apple Intelligence — on-device, free, private, offline. Available iOS 26+ on Apple Intelligence-enabled devices (iPhone 15 Pro+).

**What it excels at:** Summarization, entity extraction, classification, structured output, text generation, tool calling, conversational context.

**What it cannot do:** General world knowledge (not a chatbot), math, code generation, factual Q&A about events.

**Always provide a fallback** for devices without Apple Intelligence.

---

## Basic Usage Pattern

```swift
import FoundationModels

// 1. Check availability first
guard SystemLanguageModel.default.availability == .available else {
    // Fall back to cloud API or simpler feature
    return
}

// 2. Create a session (reuse across turns)
let session = LanguageModelSession()

// 3. Prewarm if you know you'll need it soon
await session.prewarm()

// 4. Generate a response
let response = try await session.respond(to: "Summarize this in 2 sentences: \(longText)")
print(response.content)
```

---

## Guided Generation (Type-Safe Structured Output)

The killer feature: get back Swift structs instead of raw text.

```swift
import FoundationModels

// 1. Define your output type with @Generable
@Generable
struct TaskExtraction {
    let title: String
    let dueDate: String?        // "tomorrow", "Friday", etc.
    let priority: Priority
    let tags: [String]
    
    @Generable
    enum Priority: String {
        case low, medium, high, urgent
    }
}

// 2. Generate structured output
let session = LanguageModelSession()
let response = try await session.respond(
    to: "Extract task info from: 'Call Sarah about the urgent Q4 report by Friday'",
    generating: TaskExtraction.self
)

// response.content is type-safe TaskExtraction
print(response.content.title)       // "Call Sarah about the Q4 report"
print(response.content.priority)    // .urgent
print(response.content.dueDate)     // "Friday"
```

### Streaming Structured Output
```swift
// For responsive UI — show partial results as they generate
let stream = session.streamResponse(
    to: prompt,
    generating: RecipeSuggestion.self  // @Generable type
)

// response.content is RecipeSuggestion.PartiallyGenerated
// Properties appear as Optional and fill in over time
for try await partial in stream {
    await MainActor.run {
        self.partialRecipe = partial.content
    }
}
```

---

## Tool Calling

Let the model call your app's functions to get data it needs:

```swift
import FoundationModels

// 1. Define a tool
struct WeatherTool: Tool {
    let name = "get_weather"
    let description = "Gets current weather for a location"
    
    @Generable
    struct Arguments {
        let city: String
        let country: String
    }
    
    func call(arguments: Arguments) async throws -> ToolOutput {
        // Call your weather service
        let weather = try await WeatherService.shared.fetch(
            city: arguments.city,
            country: arguments.country
        )
        return ToolOutput(stringValue: "Currently \(weather.condition), \(weather.temp)°C in \(arguments.city)")
    }
}

// 2. Create session with tools
let session = LanguageModelSession(tools: [WeatherTool()])

// 3. The model decides when to call the tool
let response = try await session.respond(
    to: "Should I bring an umbrella in Tokyo today?"
)
// Model automatically calls WeatherTool, then uses result to answer
print(response.content)  // "Yes, it's currently rainy in Tokyo..."
```

### HealthKit Integration Tool (Common Pattern)
```swift
struct HealthDataTool: Tool {
    let name = "get_health_summary"
    let description = "Retrieves user's recent health and fitness data"
    
    @Generable
    struct Arguments {
        let dataType: String  // "steps", "sleep", "heart_rate"
        let period: String    // "today", "this_week", "this_month"
    }
    
    func call(arguments: Arguments) async throws -> ToolOutput {
        let data = try await HealthKitService.shared.query(
            type: arguments.dataType,
            period: arguments.period
        )
        return ToolOutput(stringValue: data.summary)
    }
}
```

---

## Multi-Turn Conversations (Context Management)

```swift
// Sessions maintain context across multiple turns
@Observable
@MainActor
final class ConversationStore {
    private var session = LanguageModelSession(
        systemPrompt: Instructions("""
            You are a helpful assistant in [AppName]. You help users with [specific task].
            Keep responses concise (2-3 sentences unless asked for detail).
            Always stay on topic.
        """)
    )
    var messages: [ChatMessage] = []
    var isResponding: Bool { session.isResponding }
    
    func send(_ userMessage: String) async throws {
        messages.append(ChatMessage(role: .user, content: userMessage))
        
        let response = try await session.respond(to: userMessage)
        messages.append(ChatMessage(role: .assistant, content: response.content))
    }
    
    // Stream for responsive UI:
    func sendStreaming(_ userMessage: String) async throws {
        messages.append(ChatMessage(role: .user, content: userMessage))
        var assistantMessage = ""
        
        let stream = session.streamResponse(to: userMessage)
        for try await chunk in stream {
            assistantMessage = chunk.content
            if !messages.isEmpty {
                messages[messages.count - 1] = ChatMessage(role: .assistant, content: assistantMessage)
            }
        }
    }
    
    func clearConversation() {
        session = LanguageModelSession()
        messages = []
    }
}
```

---

## Model Adapter Training (Advanced — Fine-tuning)

For highly specialized use cases, train a LoRA adapter on your domain data:

```swift
// WARNING: Adapters must be retrained when Apple updates the base model (each OS update)
// Only worth it for very domain-specific tasks where prompting alone is insufficient

// Training data format:
struct TrainingExample: Codable {
    let prompt: String
    let completion: String
}

// Submit for training (this is a cloud operation, not on-device):
// See: developer.apple.com/documentation/foundationmodels/adapter-training
```

---

## Availability & Fallback Pattern

```swift
// Always handle unavailability gracefully:
@Observable
@MainActor
final class AIFeatureManager {
    
    var canUseFoundationModels: Bool {
        SystemLanguageModel.default.availability == .available
    }
    
    func smartSummarize(_ text: String) async -> String {
        if canUseFoundationModels {
            return await summarizeOnDevice(text)
        } else {
            return await summarizeViaCloud(text)  // Cloud API fallback
        }
    }
    
    private func summarizeOnDevice(_ text: String) async -> String {
        let session = LanguageModelSession()
        let response = try? await session.respond(
            to: "Summarize this in 1-2 sentences: \(text)"
        )
        return response?.content ?? fallbackSummarize(text)
    }
    
    private func summarizeViaCloud(_ text: String) async -> String {
        // Call your Vapor backend which calls a cloud AI API
        // Return result or basic string truncation
    }
    
    private func fallbackSummarize(_ text: String) -> String {
        // Basic fallback: first sentence
        text.components(separatedBy: ". ").first ?? text
    }
}
```

---

## Common App Integration Patterns

### Smart Auto-Complete (Type-Ahead Suggestions)
```swift
@Generable
struct SuggestionList {
    let suggestions: [String]  // Max 3 items
}

func generateSuggestions(for partialInput: String, context: String) async -> [String] {
    let session = LanguageModelSession()
    let response = try? await session.respond(
        to: "Given context '\(context)', suggest 3 completions for: '\(partialInput)'",
        generating: SuggestionList.self
    )
    return response?.content.suggestions ?? []
}
```

### Entity Extraction (Contacts, Dates, Tasks)
```swift
@Generable
struct ExtractedEntities {
    let people: [String]
    let dates: [String]
    let locations: [String]
    let actionItems: [String]
}

func extractFromNote(_ note: String) async -> ExtractedEntities? {
    let session = LanguageModelSession()
    let response = try? await session.respond(
        to: "Extract people, dates, locations, and action items from: \(note)",
        generating: ExtractedEntities.self
    )
    return response?.content
}
```

### Smart Content Classification
```swift
@Generable
struct ContentClassification {
    let category: Category
    let sentiment: Sentiment
    let urgency: UrgencyLevel
    let summary: String
    
    @Generable enum Category: String { case work, personal, finance, health, social, other }
    @Generable enum Sentiment: String { case positive, neutral, negative }
    @Generable enum UrgencyLevel: String { case low, medium, high, immediate }
}
```

---

## Performance Tips

- **Prewarm sessions** ahead of time: `await session.prewarm()` when you know AI will be needed soon
- **Reuse sessions** for multi-turn conversations — don't create a new one per message
- **Limit context size** — the ~3B model has a constrained context window; trim old history
- **Stream by default** — always use `streamResponse` for user-facing generation for responsive feel
- **Background sessions** — run Foundation Models on a background actor, not MainActor
- **Don't use for**: math calculations, code generation, factual world knowledge, real-time data

---

## What NOT to Use Foundation Models For

```swift
// ❌ Math / Calculations — use Swift math directly
// ❌ Code generation — model not trained for it
// ❌ General knowledge Q&A ("What year was X?") — unreliable
// ❌ Real-time data ("What's the stock price?") — use APIs
// ❌ Image generation — Foundation Models is text only
// ❌ Replacing web search — no internet access
// ❌ Large document analysis — context window too small

// ✅ Best uses:
// ✅ Extracting structure from user-written text
// ✅ Generating personalized summaries of app data
// ✅ Smart suggestions based on user's history (in-app)
// ✅ Classifying user input for routing/filtering
// ✅ Conversational assistant for app-specific domain
// ✅ Auto-tagging, categorizing content the user creates
```
