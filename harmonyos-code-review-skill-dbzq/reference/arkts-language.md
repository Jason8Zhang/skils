# ArkTS 语言合规 审查

## 基本原则

ArkTS 是 TypeScript 的严格静态子集，违反以下约束**直接导致编译失败**。审查时优先运行 `hvigorw assembleHap` 触发编译器，再用本清单做语义级复核。

1. **类型系统封闭**：禁止 `any` / `unknown` / `as const` / `infer` / 映射类型 / 交叉类型
2. **函数与类受限**：禁止 `function` 表达式、嵌套函数、generator、`apply/call/bind`、`new.target`
3. **对象与属性受限**：禁止 `obj["field"]` 动态访问、`delete` 操作符、`in` 操作符、`#` 私有字段
4. **模块系统受限**：禁止 `require()`、`export = ...`、UMD、模块通配导入

---

## 一、类型系统

### 1.1 禁用类型

```typescript
// ❌ 错误：any / unknown
let data: any = fetchData()
function parse(input: unknown) { /* ... */ }

// ✅ 正确：显式类型
interface UserInfo {
  name: string
  age: number
}
let data: UserInfo = fetchData()
function parse(input: string): UserInfo { /* ... */ }
```

### 1.2 工具类型限制

```typescript
// ❌ 错误：使用 Pick / Omit / ReturnType 等
type UserName = Pick<User, 'name'>

// ✅ 正确：仅用 Partial / Required / Readonly / Record
type UserSnapshot = Partial<User>
type ReadonlyUser = Readonly<User>
type UserMap = Record<string, User>
```

注意：`Record<K, V>` 取值类型为 `V | undefined`，必须做空值校验。

### 1.3 catch 子句

```typescript
// ❌ 错误：catch 带类型
try { /* ... */ } catch (e: any) { /* ... */ }

// ✅ 正确：省略类型
try { /* ... */ } catch (e) {
  hilog.error(0x0000, 'TAG', 'failed: %{public}s', String(e))
}
```

---

## 二、函数与类

### 2.1 禁用 function 表达式

```typescript
// ❌ 错误
const handler = function(x: number): number { return x * 2 }

// ✅ 正确：箭头函数
const handler = (x: number): number => x * 2
```

### 2.2 禁用 apply / call / bind

```typescript
// ❌ 错误
const bound = someFunc.bind(this)
someFunc.apply(this, args)

// ✅ 正确：传统 OOP
class MyService {
  private service: SomeService = new SomeService()
  doWork(): void {
    this.service.execute(args)  // 直接方法调用
  }
}
```

### 2.3 禁用构造器中声明类字段

```typescript
// ❌ 错误
class User {
  constructor(public name: string, public age: number) {}
}

// ✅ 正确：在类体中声明
class User {
  name: string = ''
  age: number = 0
  constructor(name: string, age: number) {
    this.name = name
    this.age = age
  }
}
```

### 2.4 this 范围

```typescript
// ❌ 错误：this 在静态方法中
class MyClass {
  static helper(): void {
    this.someMethod()  // 编译失败
  }
}

// ✅ 正确：this 仅在实例方法中
class MyClass {
  private someMethod(): void { /* ... */ }
  instanceMethod(): void {
    this.someMethod()  // OK
  }
}
```

### 2.5 类作为值

```typescript
// ❌ 错误
const Cls = MyClass
const instance = new Cls()

// ✅ 正确：类声明只引入类型
const instance = new MyClass()
```

---

## 三、对象与属性

### 3.1 动态字段访问

```typescript
// ❌ 错误
const value = obj['field']
obj['dynamicKey'] = 'x'

// ✅ 正确：直接访问
const value = obj.field
```

### 3.2 delete 操作符

```typescript
// ❌ 错误
delete obj.field

// ✅ 正确：用 nullable
interface User {
  name: string
  email: string | null
}
const user: User = { name: 'A', email: null }
user.email = null  // 用 null 表达缺失
```

### 3.3 in / Symbol

```typescript
// ❌ 错误
if ('field' in obj) { /* ... */ }
const key = Symbol('k')

// ✅ 正确：用 instanceof / 显式 nullable
if (obj instanceof User) { /* ... */ }
```

### 3.4 # 私有字段

```typescript
// ❌ 错误
class Foo {
  #secret: string = ''
}

// ✅ 正确：用 private 关键字
class Foo {
  private secret: string = ''
}
```

### 3.5 对象字面量

```typescript
// ❌ 错误：赋给 any / Object
const x: any = { a: 1 }
const y: Object = { method(): void {} }

// ✅ 正确：编译期可推断的接口/类
interface Config { timeout: number }
const cfg: Config = { timeout: 5000 }
```

---

## 四、解构与展开

### 4.1 解构赋值/参数

```typescript
// ❌ 错误
const { name, age } = user
function process({ id, name }: User) { /* ... */ }

// ✅ 正确：中间变量 + 字段访问
const name = user.name
const age = user.age
function process(user: User): void {
  const id = user.id
  const name = user.name
}
```

### 4.2 展开运算符

```typescript
// ❌ 错误：展开对象
const merged = { ...a, ...b }

// ✅ 正确：仅数组/数组派生类允许展开
const items = [1, 2, ...otherArray]
function process(first: number, ...rest: number[]) { /* ... */ }
```

---

## 五、模块与导入

### 5.1 导入规范

```typescript
// ❌ 错误
const foo = require('foo')
export = MyClass

// ✅ 正确
import { foo } from 'foo'
export class MyClass { /* ... */ }
```

### 5.2 import 顺序

```typescript
// ❌ 错误：import 与其他语句混排
const x = 1
import { foo } from 'foo'

// ✅ 正确：import 必须先于其他语句
import { foo } from 'foo'
const x = 1
```

### 5.3 跨语言依赖

```typescript
// ❌ 错误：TypeScript 代码 import ArkTS 代码
// (在 .ts 文件中)
import { SomeStruct } from './X.ets'  // 禁止

// ✅ 正确：ArkTS 可依赖 TS，TS 不可依赖 ArkTS
```

---

## 六、其他强约束

| 约束 | 替代方案 |
|------|---------|
| `var` | 用 `let` / `const` |
| `for...in` | 用 `for` 循环 + 索引 |
| `with` | 用局部变量提取 |
| JSX | 鸿蒙用 ArkUI 描述式语法 |
| 索引签名 | 用数组 |
| 一元 `+` / `-` / `~` 对字符串 | 先 `Number()` / `parseInt()` 显式转换 |
| `globalThis` | 用模块导出/导入 |
| 命名空间语句块 | 用模块或类 |

---

## 七、命名与格式

| 元素 | 规范 | 示例 |
|------|------|------|
| 变量/函数 | camelCase | `getUserInfo` |
| 类/接口 | PascalCase | `UserViewModel` |
| 常量 | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE` |
| 组件文件 (.ets) | PascalCase | `HomePage.ets` |
| 工具文件 | camelCase | `formatDate.ets` |
| 字符串 | 双引号 | `"hello"` |
| 行尾 | 分号 | `;` |

---

## 审查检查清单

### 类型系统
- [ ] 无 `any` / `unknown` 类型
- [ ] 无 `as const` / `infer` / 映射类型 / 交叉类型
- [ ] 工具类型仅用 `Partial` / `Required` / `Readonly` / `Record`
- [ ] `Record` 取值后做空值校验
- [ ] catch 子句省略类型

### 函数与类
- [ ] 无 `function` 表达式
- [ ] 无嵌套函数
- [ ] 无 `apply` / `call` / `bind`
- [ ] 类字段在类体声明，不在构造器声明
- [ ] `this` 仅在实例方法中使用
- [ ] 无 `new.target`

### 对象与属性
- [ ] 无 `obj["field"]` 动态访问
- [ ] 无 `delete` / `in` 操作符
- [ ] 无 `#` 私有字段
- [ ] 无 `Symbol()` API（除 `Symbol.iterator`）
- [ ] 对象字面量仅赋给编译期可推断的接口/类

### 解构与模块
- [ ] 无解构赋值/参数
- [ ] 无对象展开
- [ ] 无 `require()` / `export = ...`
- [ ] import 在其他语句之前
- [ ] TS 文件未 import ArkTS 文件

### 其他
- [ ] 无 `var` / `for...in` / `with` / JSX
- [ ] 无 `globalThis` / 命名空间语句
- [ ] 命名符合 camelCase / PascalCase / UPPER_SNAKE_CASE
- [ ] 双引号字符串、行尾分号
