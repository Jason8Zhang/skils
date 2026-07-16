# 编码规范 审查

## 基本原则

1. **命名表达意图** —— 看到名字就知道做什么；项目统一 `tztZF*` 前缀
2. **格式统一** —— 缩进 2/4 空格统一、行宽 ≤ 100、双引号字符串
3. **注释解释 Why** —— 不解释 What；不写废话；JSDoc 中文
4. **不可变优先** —— 不修改入参；返回新对象
5. **小文件优先** —— 单文件 200-400 行，最多 800 行
6. **生产无 console.log** —— 一律 `hilog` + `%{private}s` 脱敏

---

## 一、命名规范

### 1.1 文件命名

```typescript
// ✅ PascalCase：组件 / 类 / 接口
UserProfile.ets
NetworkService.ets
OrderModel.ets

// ✅ camelCase：工具 / 工具函数
formatDate.ets
httpRequest.ets
md5Util.ets

// ✅ 全小写：单文件工具
constants.ets
types.ets
```

**反例：**
```typescript
// ❌ 下划线 / 数字开头 / 拼音
user_profile.ets
user1.ets
yonghuxinxi.ets
```

### 1.2 标识符命名

```typescript
// ✅ PascalCase：类、接口、@ComponentV2、@Builder、@ObservedV2
class UserService { }
interface IUserRepository { }
@ComponentV2
struct UserProfileView { }
@ObservedV2
class UserModel { }

// ✅ camelCase：变量、函数、属性
let userName: string = ''
function getUserInfo(): void { }

// ✅ UPPER_SNAKE_CASE：常量
const MAX_RETRY_COUNT = 3
const DEFAULT_PAGE_SIZE = 20
const API_BASE_URL = 'https://api.example.com'

// ✅ 私有前缀（下划线）或 private 修饰符
private _internalState: number = 0
```

### 1.3 布尔命名

```typescript
// ✅ is / has / should / can 前缀
let isLoading: boolean = false
let hasUserAgreed: boolean = false
let shouldRefresh: boolean = true
let canSubmit: boolean = false

// ❌ 反例：状态不明的布尔
let flag: boolean = false
let status: boolean = true
```

### 1.4 项目前缀 `tztZF*`

```typescript
// ✅ 项目统一前缀
class tztZFNetworkService { }
@ComponentV2
struct tztZFHeadPage { }
function tztZFRouterCall(): void { }

// ✅ 自定义路由相关统一 tztZF
class tztZFRouter { }
class tztZFNavigationController { }
class tztZFAppObj { }

// ❌ 反例：无前缀或不一致前缀
class MyRouter { }     // ❌ 缺前缀
class ZFRouter { }     // ❌ 不一致
class RetRouter { }    // ❌ 错前缀
```

### 1.5 装饰器命名

```typescript
// ✅ @Builder 函数用 camelCase + 描述性
@Builder
function tztZFStockCard(stock: StockModel): void { }

// ✅ @ComponentV2 struct 用 PascalCase
@ComponentV2
struct StockDetailPage { }
```

---

## 二、格式规范

### 2.1 缩进与空格

```typescript
// ✅ 2 空格或 4 空格，项目统一（建议 2）
function example(): void {
  const obj = {
    name: 'tom',
    age: 18
  }
  if (obj.age > 0) {
    console.log('positive')
  }
}

// ❌ 反例：Tab 与空格混用
function bad(): void {
	const obj = { name: 'tom' }  // Tab
    const obj2 = { name: 'tom' }  // 4 空格
}
```

### 2.2 行宽

```typescript
// ✅ 每行 ≤ 100 字符
function longFunction(
  param1: string,
  param2: number,
  param3: boolean
): ReturnType {
  // ...
}

// ❌ 反例：单行过长
function longFunction(param1: string, param2: number, param3: boolean, param4: string, param5: number): ReturnType { /* ... */ }
```

### 2.3 字符串引号

```typescript
// ✅ 统一双引号
const name: string = "tom"
const template: string = `hello ${name}`

// ❌ 反例：混用
const a = 'single'  // 风格不一致
const b = "double"
```

### 2.4 分号

```typescript
// ✅ 行尾统一带分号
const count: number = 0;
function add(a: number, b: number): number {
  return a + b;
}
```

### 2.5 尾逗号

```typescript
// ✅ 多行对象 / 数组尾随逗号
const config = {
  baseUrl: 'https://api.example.com',
  timeout: 10000,
  retries: 3,
}

const items = [
  'a',
  'b',
  'c',
]
```

### 2.6 import 顺序

```typescript
// ✅ 分组：内置 → 第三方 → 项目 → 相对
import { hilog } from '@kit.PerformanceAnalysisKit'
import { rcp } from '@kit.RemoteCommunicationKit'

import { MMKV } from '@tencent/mmkv'

import { tztZFRouter } from 'tztZFUI'
import { tztZFAppObj } from 'tztZFResource'

import { UserModel } from './UserModel'
import { formatDate } from '../utils/formatDate'
```

---

## 三、注释规范

### 3.1 文件头注释

```typescript
/**
 * 用户管理服务
 * 负责用户信息加载、登录、登出
 *
 * @author 张三
 * @since 2026-01-15
 * @see UserRepository
 */
```

### 3.2 JSDoc 函数注释

```typescript
/**
 * 加载用户信息
 * @param userId 用户ID
 * @returns 用户信息对象；用户不存在返回 null
 * @throws 网络异常
 */
async function loadUser(userId: string): Promise<UserModel | null> {
  // ...
}
```

### 3.3 行内注释：解释 Why

```typescript
// ✅ 解释 why
// 必须延迟 300ms，等待弹窗关闭动画完成
setTimeout(() => refreshData(), 300)

// 必须用 parseInt 而不是 Number，因为 ID 可能带前导零
const id = parseInt(rawId, 10)

// ❌ 反例：解释 what（废话）
// 设置 count 为 0
count = 0
// 循环遍历数组
for (const item of items) { }
```

### 3.4 TODO / FIXME

```typescript
// TODO(zhangsan): 优化为分页加载
// FIXME: 网络错误时无重试机制
// HACK: 临时方案，等 SDK 升级后替换
```

### 3.5 不写废弃注释

```typescript
// ❌ 反例
// 已废弃，请使用 newFunction
function oldFunction(): void { }

// ✅ 正确：直接删除废弃代码
```

---

## 四、不可变模式

### 4.1 不修改入参

```typescript
// ❌ 错误：修改入参
function updateUser(user: UserModel, name: string): void {
  user.name = name  // 修改原对象
}

// ✅ 正确：返回新对象
function updateUser(user: UserModel, name: string): UserModel {
  return { ...user, name: name }
}
```

### 4.2 数组不修改

```typescript
// ❌ 错误：push / splice
items.push(newItem)
items.splice(0, 1)

// ✅ 正确：concat / filter / map
const newItems = items.concat(newItem)
const filtered = items.filter((_, i) => i !== 0)
const mapped = items.map((item) => transform(item))
```

### 4.3 @ObservedV2 字段修改

```typescript
// ⚠️ 特殊：@ObservedV2 / @Trace 字段可以修改（驱动 UI 更新）
@ObservedV2
class UserModel {
  @Trace name: string = ''
}
user.name = 'tom'  // OK（@Trace 字段）

// ❌ 反例：非 @Trace 字段修改不触发 UI 更新
@ObservedV2
class BadModel {
  count: number = 0  // 缺 @Trace
}
model.count = 1  // UI 不更新
```

---

## 五、错误处理

### 5.1 catch 子句无类型

```typescript
// ❌ 错误：catch 带类型（ArkTS 编译失败）
try { /* ... */ } catch (e: any) { /* ... */ }

// ✅ 正确：省略类型
try { /* ... */ } catch (e) { /* ... */ }
```

### 5.2 错误日志

```typescript
// ✅ 正确：hilog + 脱敏
try {
  await fetchData()
} catch (e) {
  hilog.error(0x0000, 'Tag', 'fetch failed: %{private}s', String(e))
}

// ❌ 反例：console + 不脱敏
console.log('error:', e)  // console.log + 敏感信息
```

### 5.3 用户友好提示

```typescript
// ✅ 正确：toast + 日志
try {
  await submit()
} catch (e) {
  hilog.error(0x0000, 'Tag', 'submit failed: %{private}s', String(e))
  promptAction.showToast({ message: $r('app.string.submit_failed') })
}
```

---

## 六、文件组织

### 6.1 单文件长度

```typescript
// ✅ 单文件 200-400 行
// UserService.ets: 250 行
//  - 用户加载
//  - 用户保存
//  - 用户登出

// ❌ 反例：单文件 > 800 行
// BigService.ets: 1200 行（拆分为多个职责文件）
```

### 6.2 一文件一组件（V2）

```typescript
// ✅ 正确：UserProfileView.ets 只含一个 @ComponentV2
// UserProfileView.ets
@ComponentV2
export struct UserProfileView {
  build() { /* ... */ }
}

// ❌ 反例：一文件多组件
// Views.ets
@ComponentV2 export struct A { }  // ❌
@ComponentV2 export struct B { }  // ❌
@ComponentV2 export struct C { }  // ❌
```

### 6.3 按领域组织

```
✅ 按领域
features/
  user/
    UserModel.ets
    UserService.ets
    UserViewModel.ets
    UserProfileView.ets
  order/
    OrderModel.ets
    OrderService.ets
    OrderListView.ets

❌ 按类型
models/
  UserModel.ets
  OrderModel.ets
views/
  UserView.ets
  OrderView.ets
```

---

## 七、修饰符使用

### 7.1 public / private

```typescript
// ✅ 类成员显式标注
class UserService {
  public async loadUser(id: string): Promise<UserModel> { /* ... */ }
  private validateId(id: string): boolean { /* ... */ }
}

// @ComponentV2 struct 内部默认 public，无需重复
@ComponentV2
struct Page {
  @Local count: number = 0  // public
  private timerId: number = -1  // private
}
```

### 7.2 readonly

```typescript
// ✅ 不可变字段
class Config {
  readonly apiUrl: string = 'https://api.example.com'
  readonly maxRetries: number = 3
}
```

---

## 八、控制台日志

### 8.1 生产禁用 console.log

```typescript
// ❌ 错误：生产代码 console.log
console.log('user info:', user)
console.log('data:', JSON.stringify(data))

// ✅ 正确：hilog
hilog.info(0x0000, 'Tag', 'user loaded: %{public}s', user.id)
hilog.debug(0x0000, 'Tag', 'data: %{private}s', JSON.stringify(data))

// ⚠️ 警告：console.error 也建议替换
console.error('failed:', e)  // 替换为 hilog.error
```

### 8.2 脱敏

```typescript
// ✅ 敏感信息用 %{private}s
hilog.info(0x0000, 'Tag', 'token: %{private}s', token)
hilog.info(0x0000, 'Tag', 'phone: %{private}s', phone)

// ❌ 反例：%{public}s 泄露
hilog.info(0x0000, 'Tag', 'token: %{public}s', token)  // 泄露
```

---

## 九、接口 vs 类型别名

### 9.1 接口优先

```typescript
// ✅ 优先用 interface
interface UserModel {
  id: string
  name: string
}

// ✅ 类型别名用于联合 / 工具类型
type Status = 'pending' | 'success' | 'failed'
type Nullable<T> = T | null
```

### 9.2 接口命名

```typescript
// ✅ I 前缀（项目约定）或仅 PascalCase
interface IUserService { }   // 项目风格
interface UserService { }    // TS 风格

// ❌ 反例：下划线 / 数字
interface IUser_Service { }  // ❌
interface UserService2 { }   // ❌
```

---

## 十、ESObject 谨慎使用

```typescript
// ⚠️ ESObject 用于跨模块 / 动态数据
function handleData(data: ESObject): void {
  const name = data['name'] as string  // 需断言
}

// ❌ 反例：滥用 ESObject 失去类型保护
function bad(data: ESObject): UserModel {
  return data  // 失去类型保护
}

// ✅ 正确：明确类型
function good(data: UserModel): UserModel {
  return data
}
```

---

## 审查检查清单

### 命名
- [ ] 文件 PascalCase / camelCase 一致
- [ ] 类 / 接口 / 组件 PascalCase
- [ ] 变量 / 函数 / 属性 camelCase
- [ ] 常量 UPPER_SNAKE_CASE
- [ ] 布尔以 is/has/should/can 开头
- [ ] 项目标识符带 tztZF 前缀

### 格式
- [ ] 缩进统一（2 或 4 空格）
- [ ] 行宽 ≤ 100
- [ ] 双引号字符串
- [ ] 行尾分号
- [ ] 多行结构尾随逗号
- [ ] import 分组排序

### 注释
- [ ] 公共函数有 JSDoc
- [ ] 注释解释 Why 而非 What
- [ ] 文件头有作者 / 时间
- [ ] 无废弃代码注释

### 不可变
- [ ] 不修改入参（@Trace 字段除外）
- [ ] 数组操作 concat / filter / map
- [ ] 返回新对象而非修改原对象

### 错误处理
- [ ] catch 无类型
- [ ] hilog 替代 console.log
- [ ] 错误有用户友好提示
- [ ] 敏感信息用 %{private}s

### 文件组织
- [ ] 单文件 ≤ 800 行
- [ ] 一文件一组件
- [ ] 按领域组织
- [ ] 公共 / 私有修饰符明确

### 其他
- [ ] 生产无 console.log
- [ ] 优先 interface 而非 type
- [ ] ESObject 用法合理
