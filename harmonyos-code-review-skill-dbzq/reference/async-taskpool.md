# 异步与 TaskPool 审查

## 基本原则

1. **UI 操作必须在主线程** —— `@ohos.app.ability.UIAbility` 同步逻辑不能阻塞主线程
2. **TaskPool 内禁调单例** —— `tztZFAppObj` / `tztZFNavigationController` 等存在 race 风险
3. **Promise/await 错误处理完整** —— try/catch + 用户友好提示
4. **aboutToAppear 异步竞态** —— 组件销毁后回调需守卫
5. **网络 IO 走 `rcp.Session` 拦截器** —— 不裸调用

---

## 一、UI 主线程

### 1.1 禁止主线程耗时

```typescript
// ❌ 错误：主线程同步网络请求
aboutToAppear() {
  const data = httpRequest.sync('https://api.example.com/data')  // 阻塞 UI
  this.list = data
}

// ✅ 正确：异步 + await
async aboutToAppear() {
  try {
    const data = await httpRequest.async('https://api.example.com/data')
    this.list = data
  } catch (e) {
    hilog.error(0x0000, 'Tag', 'request failed: %{private}s', String(e))
  }
}
```

### 1.2 长时间任务用 TaskPool

```typescript
import { taskpool } from '@kit.ArkTS'

// ✅ 正确：耗时计算放 TaskPool
async function heavyComputation(items: number[]): Promise<number> {
  return taskpool.execute(async () => {
    let sum = 0
    for (const item of items) {
      sum += Math.sqrt(item)
    }
    return sum
  })
}
```

### 1.3 长任务放 worker 线程

```typescript
import { worker } from '@kit.ArkTS'

// 创建 worker
const workerInstance = new worker.ThreadWorker('entry/ets/workers/HeavyTask.ts')

// 主线程发消息
workerInstance.postMessage({ cmd: 'start', data: largeArray })

// 接收结果
workerInstance.onmessage = (msg) => {
  hilog.info(0x0000, 'Tag', 'result: %{public}s', JSON.stringify(msg.data))
}
```

---

## 二、TaskPool 单例陷阱（项目特有红线）

### 2.1 项目警告

参考 `entry/src/main/ets/startUp/TztZFStartupTaskAsync.ets:6-7` 注释：

> "避免在 TaskPool 中调用单例方法"

### 2.2 反例

```typescript
// ❌ 错误：TaskPool 内调用单例（race 风险）
async function badTaskPoolWork(): Promise<void> {
  taskpool.execute(async () => {
    // tztZFAppObj / tztZFNavigationController 是单例
    // 多 TaskPool 任务并发访问会引发 race
    tztZFAppObj.setUserInfo(user)  // 危险
    tztZFNavigationController.pushByTab(0, 'detail', {})  // 危险
  })
}
```

### 2.3 正确做法

```typescript
// ✅ 正确：TaskPool 内只做纯计算，单例操作回主线程
async function goodTaskPoolWork(): Promise<void> {
  const result = await taskpool.execute(async (data: number[]) => {
    // 纯计算，无单例访问
    return data.reduce((s, v) => s + v, 0)
  }, largeArray)

  // 回主线程操作单例
  tztZFAppObj.setComputedValue(result)
}
```

### 2.4 单例线程安全方案

```typescript
// 方案 1：UI 线程回写
async function safeSetUser(info: UserInfo): Promise<void> {
  // TaskPool 计算 → 主线程回写
  const processed = await taskpool.execute(processUser, info)
  tztZFAppObj.setUserInfo(processed)  // 主线程
}

// 方案 2：消息队列
class SafeQueue {
  private queue: Array<() => void> = []
  private isProcessing: boolean = false

  enqueue(task: () => void): void {
    this.queue.push(task)
    this.processNext()
  }

  private async processNext(): Promise<void> {
    if (this.isProcessing || this.queue.length === 0) return
    this.isProcessing = true
    const task = this.queue.shift()
    if (task) await task()
    this.isProcessing = false
    this.processNext()
  }
}
```

---

## 三、Promise/await 错误处理

### 3.1 必加 try/catch

```typescript
// ❌ 错误：无 try/catch，错误向上抛可能未捕获
async function loadData(): Promise<void> {
  const data = await fetchData()  // 网络异常时崩溃
  this.list = data
}

// ✅ 正确：try/catch + 友好提示
async function loadData(): Promise<void> {
  try {
    const data = await fetchData()
    this.list = data
  } catch (e) {
    hilog.error(0x0000, 'Tag', 'load failed: %{private}s', String(e))
    promptAction.showToast({ message: $r('app.string.network_error') })
  }
}
```

### 3.2 catch 子句无类型

```typescript
// ❌ 错误：catch 带类型（ArkTS 禁止）
try { /* ... */ } catch (e: any) { /* ... */ }

// ✅ 正确：省略类型
try { /* ... */ } catch (e) { /* ... */ }
```

### 3.3 Promise.all 错误处理

```typescript
// ✅ 正确：Promise.allSettled 收集所有结果
async function loadMultiple(): Promise<void> {
  const results = await Promise.allSettled([
    fetchUserInfo(),
    fetchAccountInfo(),
    fetchMarketData()
  ])

  const user = results[0].status === 'fulfilled' ? results[0].value : null
  const account = results[1].status === 'fulfilled' ? results[1].value : null
  const market = results[2].status === 'fulfilled' ? results[2].value : null

  if (!user || !account) {
    promptAction.showToast({ message: $r('app.string.partial_load_failed') })
  }
}
```

---

## 四、aboutToAppear 异步竞态

### 4.1 组件销毁后回调

```typescript
// ❌ 错误：用户已离开页面，setDataV 仍触发
@ComponentV2
struct BadPage {
  @Local data: DataModel | null = null

  aboutToAppear() {
    setTimeout(() => {
      this.data = fetchData()  // 用户可能已 back
    }, 5000)
  }

  build() {
    Column() {
      if (this.data) Text(this.data.title)
    }
  }
}

// ✅ 正确：守卫 isActive 标志
@ComponentV2
struct GoodPage {
  @Local data: DataModel | null = null
  @Local isActive: boolean = false

  aboutToAppear() {
    this.isActive = true
    setTimeout(() => {
      if (this.isActive) {
        this.data = fetchData()
      }
    }, 5000)
  }

  aboutToDisappear() {
    this.isActive = false
  }

  build() {
    Column() {
      if (this.data) Text(this.data.title)
    }
  }
}
```

### 4.2 cancel token

```typescript
// ✅ 正确：使用 AbortController
class DataLoader {
  private controller: AbortController = new AbortController()

  async load(): Promise<DataModel> {
    return fetch('https://api.example.com/data', { signal: this.controller.signal })
  }

  cancel(): void {
    this.controller.abort()
  }
}

@ComponentV2
struct Page {
  @Local data: DataModel | null = null
  private loader: DataLoader = new DataLoader()

  aboutToAppear() {
    this.loader.load().then(d => { this.data = d }).catch(/* ... */)
  }

  aboutToDisappear() {
    this.loader.cancel()
  }
}
```

---

## 五、网络 IO 与拦截器

### 5.1 rcp.Session 单例

```typescript
// ✅ 正确：rcp.Session 单例复用
import { rcp } from '@kit.RemoteCommunicationKit'

class NetworkService {
  private static instance: NetworkService
  private session: rcp.Session

  private constructor() {
    this.session = rcp.createSession({
      baseAddress: 'https://api.example.com',
      interceptors: [new RequestHeaderEncoder(), new ResponseDecoder()]
    })
  }

  static getInstance(): NetworkService {
    if (!NetworkService.instance) {
      NetworkService.instance = new NetworkService()
    }
    return NetworkService.instance
  }

  async request<T>(path: string): Promise<T> {
    const resp = await this.session.get(path)
    return resp.body as T
  }
}
```

### 5.2 拦截器职责

- **RequestHeaderEncoder**：token 注入、签名、参数编码
- **ResponseDecoder**：解密、错误码转换、日志脱敏

### 5.3 超时与重试

```typescript
// ✅ 正确：超时配置
const session = rcp.createSession({
  requestConfig: {
    timeout: 10000  // 10s
  }
})

// ✅ 正确：重试策略
async function withRetry<T>(fn: () => Promise<T>, retries: number = 3): Promise<T> {
  let lastError: unknown
  for (let i = 0; i < retries; i++) {
    try {
      return await fn()
    } catch (e) {
      lastError = e
      await new Promise(r => setTimeout(r, 1000 * (i + 1)))
    }
  }
  throw lastError
}
```

---

## 六、事件回调

### 6.1 异步事件处理

```typescript
// ✅ 正确：onClick 内异步操作完整错误处理
Button('submit')
  .onClick(async () => {
    try {
      this.isSubmitting = true
      await this.submitForm()
      promptAction.showToast({ message: $r('app.string.submit_success') })
    } catch (e) {
      hilog.error(0x0000, 'Tag', 'submit failed: %{private}s', String(e))
      promptAction.showToast({ message: $r('app.string.submit_failed') })
    } finally {
      this.isSubmitting = false
    }
  })
```

### 6.2 避免事件回调泄漏

```typescript
// ❌ 错误：未取消订阅
aboutToAppear() {
  EventBus.on('userUpdate', this.handleUserUpdate)
}

// ✅ 正确：aboutToDisappear 取消
aboutToDisappear() {
  EventBus.off('userUpdate', this.handleUserUpdate)
}
```

---

## 审查检查清单

### 主线程
- [ ] 无主线程同步耗时操作（网络 / 文件 / 重计算）
- [ ] 长任务用 TaskPool 或 worker
- [ ] 异步逻辑 await 完整

### TaskPool
- [ ] TaskPool 内未访问 `tztZFAppObj` / `tztZFNavigationController` 等单例
- [ ] TaskPool 内只做纯计算，单例操作回主线程
- [ ] 长时间 worker 用 message queue 串行化

### 错误处理
- [ ] 所有 await 都有 try/catch
- [ ] catch 子句无类型标注
- [ ] Promise.allSettled 收集部分失败
- [ ] 错误有用户友好提示

### 生命周期
- [ ] aboutToAppear 异步逻辑有 isActive / cancel 守卫
- [ ] 事件订阅在 aboutToDisappear 取消
- [ ] 资源在组件销毁时释放

### 网络
- [ ] rcp.Session 单例复用
- [ ] 拦截器职责单一（编码 / 解码 / 脱敏）
- [ ] 有超时与重试配置
