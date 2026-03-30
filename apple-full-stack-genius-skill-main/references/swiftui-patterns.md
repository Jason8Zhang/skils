# SwiftUI Patterns & Liquid Glass Component Library

## Navigation Pattern (2026)

```swift
// Root navigation — NavigationStack with typed path (not NavigationView)
struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        TabView {
            Tab("Habits", systemImage: "checkmark.circle") {
                NavigationStack(path: $path) {
                    HabitsView()
                        .navigationDestination(for: Habit.self) { habit in
                            HabitDetailView(habit: habit)
                        }
                        .navigationDestination(for: HabitLog.self) { log in
                            LogDetailView(log: log)
                        }
                }
            }
            Tab("Stats", systemImage: "chart.bar.fill") {
                StatsView()
            }
            Tab("Settings", systemImage: "gearshape.fill") {
                SettingsView()
            }
        }
        .tabViewStyle(.sidebarAdaptable) // collapses to tab bar on iPhone, sidebar on iPad/Mac
    }
}
```

---

## Liquid Glass Component Library

### LiquidGlassCard

```swift
struct LiquidGlassCard<Content: View>: View {
    var cornerRadius: CGFloat = 28
    var padding: CGFloat = 20
    @ViewBuilder let content: () -> Content

    var body: some View {
        content()
            .padding(padding)
            .background(
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .fill(.regularMaterial)
                    .overlay(
                        RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                            .strokeBorder(
                                LinearGradient(
                                    colors: [.white.opacity(0.25), .white.opacity(0.05)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                ),
                                lineWidth: 1
                            )
                    )
            )
            .shadow(color: .black.opacity(0.1), radius: 20, x: 0, y: 8)
    }
}

// Usage:
LiquidGlassCard {
    VStack(alignment: .leading, spacing: 8) {
        Text(habit.title).font(.title3.bold())
        Text("\(habit.streak) day streak").font(.caption).foregroundStyle(.secondary)
    }
}
```

### PrimaryButton

```swift
struct PrimaryButton: View {
    let title: String
    let systemImage: String?
    var role: ButtonRole? = nil
    let action: () async -> Void

    @State private var isPressed = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        Button(role: role) {
            Task { await action() }
        } label: {
            HStack(spacing: 8) {
                if let systemImage {
                    Image(systemName: systemImage)
                }
                Text(title)
            }
            .font(.body.bold())
            .foregroundStyle(.white)
            .frame(maxWidth: .infinity, minHeight: 52)
            .background(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [Color.accentColor, Color.accentColor.opacity(0.8)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
            )
            .scaleEffect(isPressed ? 0.97 : 1.0)
            .animation(reduceMotion ? .none : .spring(duration: 0.2, bounce: 0.4), value: isPressed)
        }
        .simultaneousGesture(
            DragGesture(minimumDistance: 0)
                .onChanged { _ in isPressed = true }
                .onEnded { _ in isPressed = false }
        )
    }
}
```

### StreakRing (Custom SwiftUI + Metal-like Canvas)

```swift
struct StreakRing: View {
    let progress: Double   // 0.0 – 1.0
    let streak: Int
    var size: CGFloat = 80

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        ZStack {
            // Track
            Circle()
                .stroke(Color.primary.opacity(0.1), lineWidth: size * 0.1)

            // Progress arc
            Circle()
                .trim(from: 0, to: progress)
                .stroke(
                    AngularGradient(
                        colors: [.orange, .yellow, .orange],
                        center: .center,
                        startAngle: .degrees(-90),
                        endAngle: .degrees(270)
                    ),
                    style: StrokeStyle(
                        lineWidth: size * 0.1,
                        lineCap: .round
                    )
                )
                .rotationEffect(.degrees(-90))
                .animation(
                    reduceMotion ? .none : .spring(duration: 0.6, bounce: 0.2),
                    value: progress
                )

            // Streak count
            VStack(spacing: 0) {
                Text("\(streak)")
                    .font(.system(size: size * 0.28, weight: .bold, design: .rounded))
                Text("days")
                    .font(.system(size: size * 0.14, weight: .medium))
                    .foregroundStyle(.secondary)
            }
        }
        .frame(width: size, height: size)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(streak) day streak, \(Int(progress * 100))% complete")
    }
}
```

---

## List Patterns

```swift
// Swipeable list with haptic feedback
struct HabitsView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \Habit.createdAt, order: .forward) private var habits: [Habit]
    @State private var store = HabitStore()

    var body: some View {
        List {
            ForEach(habits) { habit in
                HabitRowView(habit: habit)
                    .listRowBackground(Color.clear)
                    .listRowSeparator(.hidden)
                    .listRowInsets(EdgeInsets(top: 6, leading: 16, bottom: 6, trailing: 16))
                    .swipeActions(edge: .trailing, allowsFullSwipe: true) {
                        Button(role: .destructive) {
                            withAnimation { modelContext.delete(habit) }
                        } label: {
                            Label("Delete", systemImage: "trash")
                        }
                    }
                    .swipeActions(edge: .leading) {
                        Button {
                            Task { await store.logCompletion(for: habit) }
                        } label: {
                            Label("Log", systemImage: "checkmark.circle.fill")
                        }
                        .tint(.green)
                    }
            }
        }
        .listStyle(.plain)
        .scrollContentBackground(.hidden)
    }
}
```

---

## Sheet & Full-Screen Presentation

```swift
struct AddHabitSheet: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(\.modelContext) private var modelContext
    @State private var title = ""
    @State private var selectedColor = Color.accentColor

    var body: some View {
        NavigationStack {
            Form {
                Section("Name") {
                    TextField("e.g. Morning run", text: $title)
                        .submitLabel(.done)
                }
                Section("Color") {
                    ColorPicker("Pick a color", selection: $selectedColor, supportsOpacity: false)
                }
            }
            .navigationTitle("New Habit")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Add") {
                        let habit = Habit(title: title, colorHex: selectedColor.hexString)
                        modelContext.insert(habit)
                        dismiss()
                    }
                    .disabled(title.isEmpty)
                }
            }
        }
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
        .presentationCornerRadius(32)
        .presentationBackground(.regularMaterial)
    }
}
```

---

## Adaptive Layout (all device sizes)

```swift
struct AdaptiveHabitsLayout: View {
    @Environment(\.horizontalSizeClass) private var hSizeClass
    @Environment(\.verticalSizeClass) private var vSizeClass

    var columns: [GridItem] {
        if hSizeClass == .regular {
            // iPad / Mac / Landscape
            return Array(repeating: GridItem(.flexible(), spacing: 16), count: 3)
        } else {
            // iPhone Portrait
            return [GridItem(.flexible())]
        }
    }

    var body: some View {
        ScrollView {
            LazyVGrid(columns: columns, spacing: 16) {
                // content
            }
            .padding()
        }
    }
}
```

---

## Animation Patterns

```swift
// ✅ Spring animation for state changes (feels physical)
withAnimation(.spring(duration: 0.4, bounce: 0.3)) {
    isExpanded.toggle()
}

// ✅ Matched geometry effect for hero transitions
@Namespace private var habitNamespace

// In source view:
.matchedGeometryEffect(id: habit.id, in: habitNamespace)

// In destination view:
.matchedGeometryEffect(id: habit.id, in: habitNamespace)

// ✅ Phase animator for multi-step sequences
.phaseAnimator([false, true]) { content, phase in
    content
        .scaleEffect(phase ? 1.05 : 1.0)
        .opacity(phase ? 1.0 : 0.7)
} animation: { phase in
    phase ? .spring(duration: 0.3) : .easeOut(duration: 0.15)
}

// ✅ Keyframe animator for complex multi-property animation
.keyframeAnimator(initialValue: AnimationValues()) { content, value in
    content
        .rotationEffect(value.angle)
        .scaleEffect(value.scale)
} keyframes: { _ in
    KeyframeTrack(\.angle) {
        CubicKeyframe(.zero, duration: 0.1)
        CubicKeyframe(.degrees(15), duration: 0.15)
        CubicKeyframe(.degrees(-10), duration: 0.15)
        CubicKeyframe(.zero, duration: 0.2)
    }
    KeyframeTrack(\.scale) {
        SpringKeyframe(1.2, duration: 0.3)
        SpringKeyframe(1.0, duration: 0.3)
    }
}
```

---

## Haptic Feedback (always use for meaningful interactions)

```swift
// HapticsService.swift
@MainActor
final class HapticsService {
    static let shared = HapticsService()

    // Simple UIKit haptics (quick, no setup)
    func success() {
        UINotificationFeedbackGenerator().notificationOccurred(.success)
    }

    func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle = .medium) {
        UIImpactFeedbackGenerator(style: style).impactOccurred()
    }

    // Core Haptics for custom patterns (e.g., streak celebration)
    func streakCelebration() {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else { return }
        // Custom AHAP pattern or programmatic events here
        let sharpness = CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.5)
        let intensity = CHHapticEventParameter(parameterID: .hapticIntensity, value: 1.0)
        let event = CHHapticEvent(
            eventType: .hapticTransient,
            parameters: [sharpness, intensity],
            relativeTime: 0
        )
        // ... start engine and play pattern
    }
}
```

---

## SwiftUI Preview Best Practices

```swift
#Preview("Habit Row — Active Streak") {
    HabitRowView(habit: .preview)
        .padding()
        .background(.background)
        .previewLayout(.sizeThatFits)
}

#Preview("Habit Row — Dark Mode") {
    HabitRowView(habit: .preview)
        .padding()
        .background(.background)
        .preferredColorScheme(.dark)
}

// In PreviewData.swift:
extension Habit {
    static var preview: Habit {
        let habit = Habit(title: "Morning Run", colorHex: "#FF6B35")
        habit.streak = 21
        return habit
    }
}
```

---

## Continuity — Handoff Support

```swift
// In your top-level view, declare the user activity
.userActivity("com.yourapp.viewhabit") { activity in
    activity.title = habit.title
    activity.userInfo = ["habitID": habit.id.uuidString]
    activity.isEligibleForHandoff = true
    activity.isEligibleForSearch = true
    activity.becomeCurrent()
}

// In the App struct, handle incoming Handoff activities
.onContinueUserActivity("com.yourapp.viewhabit") { activity in
    guard let idString = activity.userInfo?["habitID"] as? String,
          let id = UUID(uuidString: idString) else { return }
    // Navigate to the habit
    path.append(id)
}
```
