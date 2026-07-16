# 架构 审查指南

## 基本原则

1. **MVVM 分层清晰** —— View / ViewModel / Model / Service 职责分明
2. **SOLID 原则** —— 单一职责、开闭、里氏替换、接口隔离、依赖倒置
3. **模块边界清晰** —— entry + 20 个 HAR/HSP
4. **路由职责单一** —— `tztZFRouter` 承担 path 解析 + 步骤观察 + 跨模块传参
5. **Repository 模式** —— 数据访问封装

---

## 一、SOLID 原则

### 1.1 单一职责（SRP）

```typescript
// ❌ 错误：一个类承担多个职责
class UserPageController {
  loadUserData() { /* 网络 */ }
  renderUI() { /* UI */ }
  saveToDB() { /* 数据库 */ }
  logAnalytics() { /* 埋点 */ }
}

// ✅ 正确：拆分
class UserService {
  loadUserData(): Promise<UserModel> { /* ... */ }
}

class UserViewModel {
  @Trace user: UserModel = new UserModel()
  async loadUser(): Promise<void> { /* ... */ }
}

class AnalyticsTracker {
  logPageView(page: string): void { /* ... */ }
}
```

### 1.2 开闭原则（OCP）

```typescript
// ❌ 错误：修改现有类
class OrderCalculator {
  calculate(type: string, amount: number): number {
    if (type === 'normal') return amount
    if (type === 'discount') return amount * 0.9
    if (type === 'vip') return amount * 0.8
    // 新增类型需修改此类
  }
}

// ✅ 正确：扩展
interface PricingStrategy {
  calculate(amount: number): number
}

class NormalPricing implements PricingStrategy {
  calculate(amount: number): number { return amount }
}

class DiscountPricing implements PricingStrategy {
  calculate(amount: number): number { return amount * 0.9 }
}

class OrderCalculator {
  constructor(private strategy: PricingStrategy) {}
  calculate(amount: number): number {
    return this.strategy.calculate(amount)
  }
}
```

### 1.3 里氏替换（LSP）

```typescript
// ✅ 子类可替换父类
abstract class BaseRepository<T> {
  abstract findById(id: string): Promise<T | null>
  abstract save(entity: T): Promise<void>
}

class UserRepository extends BaseRepository<UserModel> {
  findById(id: string): Promise<UserModel | null> { /* ... */ }
  save(user: UserModel): Promise<void> { /* ... */ }
}
```

### 1.4 接口隔离（ISP）

```typescript
// ❌ 错误：胖接口
interface IUserService {
  login(): Promise<void>
  logout(): Promise<void>
  getUserInfo(): Promise<UserModel>
  uploadAvatar(file: File): Promise<void>
  sendSms(phone: string): Promise<void>
  bindBankCard(card: CardInfo): Promise<void>
}

// ✅ 正确：拆分
interface IAuthService {
  login(): Promise<void>
  logout(): Promise<void>
}

interface IUserInfoService {
  getUserInfo(): Promise<UserModel>
  updateUserInfo(user: UserModel): Promise<void>
}

interface IAvatarService {
  uploadAvatar(file: File): Promise<void>
}
```

### 1.5 依赖倒置（DIP）

```typescript
// ❌ 错误：依赖具体类
class OrderViewModel {
  private db: MySQLDatabase = new MySQLDatabase()
  async saveOrder(): Promise<void> {
    await this.db.insert('orders', this.order)
  }
}

// ✅ 正确：依赖抽象
interface IOrderRepository {
  save(order: OrderModel): Promise<void>
}

class OrderViewModel {
  constructor(private repo: IOrderRepository) {}
  async saveOrder(): Promise<void> {
    await this.repo.save(this.order)
  }
}
```

---

## 二、MVVM 架构（项目实际变体）

### 2.1 分层职责

```
┌─────────────────────┐
│ View (@ComponentV2) │  ← 仅渲染，无业务逻辑
└──────────┬──────────┘
           │ @Param / @Event
┌──────────▼──────────┐
│ ViewModel (Controller) │  ← 业务逻辑、状态管理
│ (持有 page 生命周期)
└──────────┬──────────┘
           │ 调用
┌──────────▼──────────┐
│ Model (@ObservedV2) │  ← 数据模型 + @Trace
└──────────┬──────────┘
           │ 调用
┌──────────▼──────────┐
│ Service             │  ← 网络、数据库、文件
└─────────────────────┘
```

### 2.2 View 规范

```typescript
// ✅ 正确：View 仅渲染
@ComponentV2
struct UserProfileView {
  @Param viewModel: UserProfileViewModel = new UserProfileViewModel()

  build() {
    Column() {
      if (this.viewModel.isLoading) {
        LoadingComponent()
      } else if (this.viewModel.user) {
        UserCard({ user: this.viewModel.user })
      }
    }
  }
}

// ❌ 错误：View 内业务逻辑
@ComponentV2
struct BadView {
  @Local user: UserModel = new UserModel()

  aboutToAppear() {
    // ❌ View 直接发请求
    httpRequest.get('https://api.example.com/user').then((data) => {
      this.user = data
    })
  }
}
```

### 2.3 ViewModel 规范

```typescript
// ✅ 正确：ViewModel 持业务逻辑
@ObservedV2
class UserProfileViewModel {
  @Trace user: UserModel | null = null
  @Trace isLoading: boolean = false
  @Trace error: Error | null = null

  constructor(private userService: IUserService) {}

  async loadUser(userId: string): Promise<void> {
    try {
      this.isLoading = true
      this.error = null
      this.user = await this.userService.getUser(userId)
    } catch (e) {
      this.error = e as Error
    } finally {
      this.isLoading = false
    }
  }
}
```

### 2.4 Model 规范

```typescript
// ✅ 正确：纯数据类
@ObservedV2
class UserModel {
  @Trace id: string = ''
  @Trace name: string = ''
  @Trace email: string = ''
  @Trace avatar: string = ''

  @Computed
  get displayName(): string {
    return this.name || this.email
  }
}

// ❌ 错误：Model 内有网络调用
@ObservedV2
class BadUserModel {
  @Trace name: string = ''

  async fetchDetail(): Promise<void> {
    const data = await httpRequest.get('/user')  // ❌
    this.name = data.name
  }
}
```

### 2.5 Service 规范

```typescript
// ✅ 正确：Service 封装数据访问
interface IUserService {
  getUser(id: string): Promise<UserModel>
  updateUser(user: UserModel): Promise<void>
}

class UserService implements IUserService {
  constructor(private repo: IUserRepository) {}

  async getUser(id: string): Promise<UserModel> {
    const data = await this.repo.findById(id)
    return UserModel.fromJson(data)
  }

  async updateUser(user: UserModel): Promise<void> {
    await this.repo.save(user)
  }
}
```

---

## 三、模块化架构

### 3.1 模块职责

| 模块 | 职责 |
|------|------|
| `entry` | 入口、首页、tab 装配 |
| `tztZFJY` | 交易业务（买卖、撤单、持仓）|
| `tztZFHQ` | 行情数据（实时、K 线、分时）|
| `tztZFUI` | 共享 UI 组件、路由 |
| `tztZFResource` | 资源、路由路径常量 |
| `RetUtils` | 工具类（网络、加密）|
| `RetBusiness` | 业务工具类 |

### 3.2 依赖方向

```
entry
  ├── tztZFJY
  │     ├── tztZFUI
  │     │     ├── tztZFResource
  │     │     └── RetUtils
  │     ├── tztZFHQ
  │     └── RetBusiness
  ├── tztZFHQ
  │     └── tztZFUI
  ├── tztZFSys
  │     └── tztZFUI
  └── ...
```

**禁止反向依赖**（如 `tztZFUI` 依赖 `tztZFJY`）。

### 3.3 公共代码

```typescript
// 错误：业务代码放共享 UI 模块
// tztZFUI/src/main/ets/.../TradeService.ets  // ❌

// 正确：业务代码放业务模块
// tztZFJY/src/main/ets/.../TradeService.ets  // ✅
```

---

## 四、路由架构

### 4.1 tztZFRouter 职责

`tztZFRouter` 承担：
- path 解析（字符串路径 → NavPathStack name）
- 步骤观察（`tztZFRouteStep.observe`）
- 跨模块传参（`param` 参数）
- deepLink 接入

### 4.2 多 Tab 栈

```typescript
// tztZFNavigationController
class tztZFNavigationController {
  private dictMap: Map<number, NavPathStack> = new Map()

  public pushByTab(tabIndex: number, path: string, param: ESObject): void {
    const stack = this.dictMap.get(tabIndex)
    if (stack) {
      stack.pushPath({ name: path, param: param })
    }
  }
}
```

**审查要点：**
- 切换 Tab 不应清空其他 Tab 的栈
- 同一 Tab 内 push 不应跳到其他 Tab
- `addUniquePageName` 去重机制是否正确

### 4.3 路由命名规范

```
tztZFUI/src/main/ets/routes/RoutePaths.ets

class RoutePaths {
  static readonly HOME = 'home'
  static readonly TRADE = 'trade'
  static readonly QUOTE = 'quote'
  static readonly LOGIN = 'login'
  static readonly TRADE_DETAIL = 'tradeDetail'
}
```

---

## 五、Repository 模式

### 5.1 数据访问封装

```typescript
// 抽象接口
interface IUserRepository {
  findById(id: string): Promise<UserModel | null>
  save(user: UserModel): Promise<void>
  delete(id: string): Promise<void>
}

// 网络实现
class UserApiRepository implements IUserRepository {
  constructor(private api: NetworkService) {}

  async findById(id: string): Promise<UserModel | null> {
    return this.api.get<UserModel>(`/user/${id}`)
  }

  async save(user: UserModel): Promise<void> {
    await this.api.post('/user', user)
  }

  async delete(id: string): Promise<void> {
    await this.api.delete(`/user/${id}`)
  }
}

// 本地缓存实现
class UserCacheRepository implements IUserRepository {
  constructor(private mmkv: MMKV) {}

  async findById(id: string): Promise<UserModel | null> {
    const data = this.mmkv.getString(`user:${id}`)
    return data ? UserModel.fromJsonString(data) : null
  }

  async save(user: UserModel): Promise<void> {
    this.mmkv.set(`user:${user.id}`, user.toJsonString())
  }

  async delete(id: string): Promise<void> {
    this.mmkv.delete(`user:${id}`)
  }
}
```

### 5.2 组合 Repository

```typescript
class CachedUserRepository implements IUserRepository {
  constructor(
    private remote: UserApiRepository,
    private cache: UserCacheRepository
  ) {}

  async findById(id: string): Promise<UserModel | null> {
    const cached = await this.cache.findById(id)
    if (cached) return cached
    const fresh = await this.remote.findById(id)
    if (fresh) await this.cache.save(fresh)
    return fresh
  }
}
```

---

## 六、API 响应封装

```typescript
// 统一响应格式
interface ApiResponse<T> {
  success: boolean
  data: T | null
  error: string | null
  meta?: {
    total: number
    page: number
    pageSize: number
  }
}

// 转换函数
async function request<T>(path: string): Promise<T> {
  const resp = await api.get<ApiResponse<T>>(path)
  if (!resp.success || !resp.data) {
    throw new Error(resp.error || 'Unknown error')
  }
  return resp.data
}
```

---

## 七、反模式

### 7.1 上帝类

```typescript
// ❌ 反模式：单个类承担所有功能
class AppManager {
  loadUser() { /* ... */ }
  loadTrade() { /* ... */ }
  loadMarket() { /* ... */ }
  loadMessage() { /* ... */ }
  loadConfig() { /* ... */ }
  // ... 几十个方法
}
```

### 7.2 紧耦合

```typescript
// ❌ 反模式：直接调用其他 ViewModel
class OrderViewModel {
  @Local user: UserModel = new UserModel()
  constructor() {
    const userVM = AppStorage.get<UserViewModel>('userVM')  // ❌
    this.user = userVM.user
  }
}

// ✅ 正确：通过 Service 解耦
class OrderViewModel {
  @Local user: UserModel = new UserModel()
  constructor(private userService: IUserService) {
    this.userService.getCurrentUser().then(u => { this.user = u })
  }
}
```

### 7.3 循环依赖

```typescript
// ❌ 反模式：A → B → A
// tztZFJY/.../TradeService.ets
import { UserService } from 'tztZFJY/UserService'  // ❌

// tztZFJY/.../UserService.ets
import { TradeService } from 'tztZFJY/TradeService'  // ❌
```

---

## 审查检查清单

### SOLID
- [ ] 单一职责（类职责清晰）
- [ ] 开闭原则（扩展优于修改）
- [ ] 接口隔离（接口精简）
- [ ] 依赖倒置（依赖抽象非具体）

### MVVM
- [ ] View 仅渲染，无业务逻辑
- [ ] ViewModel 持业务逻辑与状态
- [ ] Model 是纯数据类（@ObservedV2 + @Trace）
- [ ] Service 封装数据访问

### 模块化
- [ ] 模块边界清晰
- [ ] 无反向依赖
- [ ] 无循环依赖
- [ ] 业务代码不在 UI 模块

### 路由
- [ ] tztZFRouter 职责单一
- [ ] 多 Tab 栈独立管理
- [ ] 路由命名规范
- [ ] deepLink 白名单

### 反模式
- [ ] 无上帝类
- [ ] 无 ViewModel 间直接调用
- [ ] 无循环 import
