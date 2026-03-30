# Server-Side Swift with Vapor 4

## When to Add a Backend

Add a Vapor backend when your app needs:
- Multi-user data that must be shared across accounts (not just devices)
- Server-side push notification triggers
- Complex business logic that shouldn't run on-device
- Analytics aggregation, leaderboards, social features

If all data is per-user private, **CloudKit alone is sufficient** — don't add Vapor just to have a backend.

---

## Shared Models SPM Package (Client + Server)

The key advantage of Server-Side Swift: share `Codable` models with the iOS app.

```swift
// Packages/SharedModels/Sources/SharedModels/HabitDTO.swift
// swift-tools-version: 6.0 — no imports needed beyond Foundation
import Foundation

public struct HabitDTO: Codable, Sendable, Identifiable {
    public let id: UUID
    public var title: String
    public var colorHex: String
    public var streak: Int
    public var isArchived: Bool
    public var createdAt: Date
    public var updatedAt: Date

    public init(
        id: UUID = UUID(),
        title: String,
        colorHex: String = "#007AFF",
        streak: Int = 0,
        isArchived: Bool = false,
        createdAt: Date = .now,
        updatedAt: Date = .now
    ) {
        self.id = id
        self.title = title
        self.colorHex = colorHex
        self.streak = streak
        self.isArchived = isArchived
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }
}

public struct APIResponse<T: Codable & Sendable>: Codable, Sendable {
    public let data: T?
    public let error: APIError?
    public let meta: ResponseMeta?

    public struct APIError: Codable, Sendable {
        public let code: String
        public let message: String
    }

    public struct ResponseMeta: Codable, Sendable {
        public let page: Int?
        public let perPage: Int?
        public let total: Int?
    }
}
```

---

## Vapor App Structure

```swift
// Backend/Sources/App/configure.swift
import Vapor
import Fluent
import FluentPostgresDriver

public func configure(_ app: Application) async throws {
    // MARK: - Database
    app.databases.use(
        .postgres(configuration: .init(
            hostname: Environment.get("DB_HOST") ?? "localhost",
            username: Environment.get("DB_USER") ?? "vapor",
            password: Environment.get("DB_PASS") ?? "",
            database: Environment.get("DB_NAME") ?? "habits_db",
            tls: .prefer(try .init(configuration: .clientDefault))
        )),
        as: .psql
    )

    // MARK: - Migrations
    app.migrations.add(CreateHabit())
    app.migrations.add(CreateHabitLog())
    try await app.autoMigrate()

    // MARK: - Middleware
    app.middleware.use(CORSMiddleware(configuration: .init(
        allowedOrigin: .any(["https://yourapp.com"]),
        allowedMethods: [.GET, .POST, .PUT, .DELETE, .OPTIONS],
        allowedHeaders: [.accept, .authorization, .contentType]
    )))

    // MARK: - Routes
    try routes(app)
}
```

```swift
// Backend/Sources/App/routes.swift
import Vapor
import SharedModels

func routes(_ app: Application) throws {
    let api = app.grouped("api", "v1")

    // Public health check
    api.get("health") { _ in HTTPStatus.ok }

    // Authenticated routes
    let protected = api.grouped(UserAuthMiddleware())
    try protected.register(collection: HabitController())
}
```

---

## Controller Pattern

```swift
// Backend/Sources/App/Controllers/HabitController.swift
import Vapor
import Fluent
import SharedModels

struct HabitController: RouteCollection {
    func boot(routes: RoutesBuilder) throws {
        let habits = routes.grouped("habits")
        habits.get(use: index)
        habits.post(use: create)
        habits.group(":habitID") { habit in
            habit.get(use: show)
            habit.put(use: update)
            habit.delete(use: delete)
        }
    }

    // GET /api/v1/habits
    @Sendable
    func index(req: Request) async throws -> [HabitDTO] {
        let userID = try req.auth.require(User.self).requireID()
        let habits = try await Habit.query(on: req.db)
            .filter(\.$owner.$id == userID)
            .filter(\.$isArchived == false)
            .sort(\.$createdAt, .ascending)
            .all()
        return habits.map(\.dto)
    }

    // POST /api/v1/habits
    @Sendable
    func create(req: Request) async throws -> Response {
        let dto = try req.content.decode(HabitDTO.self)
        let userID = try req.auth.require(User.self).requireID()

        let habit = Habit(from: dto, ownerID: userID)
        try await habit.save(on: req.db)

        let response = Response(status: .created)
        try response.content.encode(habit.dto)
        return response
    }
}
```

---

## Fluent Model (maps to HabitDTO)

```swift
// Backend/Sources/App/Models/Habit.swift
import Fluent
import Vapor
import SharedModels

final class Habit: Model, @unchecked Sendable {
    static let schema = "habits"

    @ID(key: .id) var id: UUID?
    @Field(key: "title") var title: String
    @Field(key: "color_hex") var colorHex: String
    @Field(key: "streak") var streak: Int
    @Field(key: "is_archived") var isArchived: Bool
    @Timestamp(key: "created_at", on: .create) var createdAt: Date?
    @Timestamp(key: "updated_at", on: .update) var updatedAt: Date?
    @Parent(key: "owner_id") var owner: User
    @Children(for: \.$habit) var logs: [HabitLog]

    init() {}

    init(from dto: HabitDTO, ownerID: User.IDValue) {
        self.id = dto.id
        self.title = dto.title
        self.colorHex = dto.colorHex
        self.streak = dto.streak
        self.isArchived = dto.isArchived
        self.$owner.id = ownerID
    }

    var dto: HabitDTO {
        HabitDTO(
            id: id!,
            title: title,
            colorHex: colorHex,
            streak: streak,
            isArchived: isArchived,
            createdAt: createdAt ?? .now,
            updatedAt: updatedAt ?? .now
        )
    }
}
```

---

## iOS API Client (Swift 6 async/await)

```swift
// Core/Services/APIClient.swift
actor APIClient {
    static let shared = APIClient()
    private let baseURL = URL(string: "https://api.yourapp.com/api/v1")!
    private let session: URLSession

    init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        self.session = URLSession(configuration: config)
    }

    func fetchHabits() async throws -> [HabitDTO] {
        let request = try makeRequest(path: "habits", method: "GET")
        let (data, response) = try await session.data(for: request)
        try validate(response)
        return try JSONDecoder.iso8601.decode([HabitDTO].self, from: data)
    }

    func createHabit(_ habit: HabitDTO) async throws -> HabitDTO {
        var request = try makeRequest(path: "habits", method: "POST")
        request.httpBody = try JSONEncoder.iso8601.encode(habit)
        let (data, response) = try await session.data(for: request)
        try validate(response)
        return try JSONDecoder.iso8601.decode(HabitDTO.self, from: data)
    }

    private func makeRequest(path: String, method: String) throws -> URLRequest {
        var request = URLRequest(url: baseURL.appendingPathComponent(path))
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        // Add auth token from Keychain
        if let token = KeychainService.shared.accessToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        return request
    }

    private func validate(_ response: URLResponse) throws {
        guard let http = response as? HTTPURLResponse,
              (200..<300).contains(http.statusCode) else {
            throw APIError.serverError
        }
    }
}

extension JSONDecoder {
    static let iso8601: JSONDecoder = {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }()
}

extension JSONEncoder {
    static let iso8601: JSONEncoder = {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        return encoder
    }()
}
```

---

## Deployment (Fly.io — Recommended for Vapor)

```dockerfile
# Dockerfile (in Backend/ directory)
FROM swift:6.0-jammy AS build
WORKDIR /build
COPY . .
RUN swift build -c release --disable-sandbox

FROM ubuntu:jammy-20230804
RUN apt-get update && apt-get install -y libssl-dev libsqlite3-dev
WORKDIR /app
COPY --from=build /build/.build/release/App .
COPY --from=build /build/Public ./Public
EXPOSE 8080
CMD ["./App", "serve", "--env", "production", "--hostname", "0.0.0.0", "--port", "8080"]
```

```toml
# fly.toml
app = "my-habits-api"
primary_region = "ord"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 1
```

Deploy:
```bash
fly launch         # first time
fly deploy         # subsequent updates
fly postgres create --name habits-db  # managed PostgreSQL
fly postgres attach habits-db
```
