# V2 状态管理 审查

## 基本原则

**项目处于 V1→V2 渐进迁移期（V1 57 处 vs V2 112 处）。审查规则：**

1. **新增代码必须 V2**（@ComponentV2 / @Local / @Param / @Event / @Provider / @Consumer / @Monitor / @Computed / @ObservedV2 / @Trace）
2. **存量 V1 临时允许**（@Component / @State / @Prop / @Link / @ObjectLink / @Observed / @Provide / @Consume / @Watch）只做维护，不得扩增
3. **V1 → V6.0 后部分 API 失效**，新增代码若误用 V1 会导致升级失败

---

## 一、V2 装饰器清单

| 装饰器 | 作用 | 替代 V1 |
|--------|------|---------|
| `@ComponentV2` | 标记 V2 组件 struct | `@Component` |
| `@Local` | 组件内部可变状态 | `@State` |
| `@Param` | 父传子的只读 props | `@Prop` / `@Link`（部分） |
| `@Event` | 子传父的回调 | `$` 回调函数 |
| `@Provider` | 跨层级向下提供状态 | `@Provide` |
| `@Consumer` | 跨层级向上消费状态 | `@Consume` |
| `@Monitor` | 监听状态变化 | `@Watch` |
| `@Computed` | 派生计算值 | getter + 手动触发 |
| `@ObservedV2` | 标记可观察类 | `@Observed` |
| `@Trace` | 标记可观察字段 | 无（V1 用 @ObjectLink） |

---

## 二、禁用 V1 装饰器（红线）

**新增代码严禁使用以下 V1 装饰器：**

```typescript
// ❌ 全部错误 —— 这些是 V1 装饰器
@Component          // → @ComponentV2
@State              // → @Local
@Prop               // → @Param
@Link               // → @Param + @Event
@ObjectLink         // → @Param 引用 @ObservedV2 对象
@Observed           // → @ObservedV2 + @Trace
@Provide            // → @Provider
@Consume            // → @Consumer
@Watch              // → @Monitor
```

**检测命令：**
```bash
# 扫描新增 .ets 文件是否含 V1 装饰器
git diff --name-only --diff-filter=A | xargs grep -lE "@(State|Prop|Link|ObjectLink|Observed|Provide|Consume|Watch|Component)\b" 2>/dev/null
```

---

## 三、@ComponentV2 规范

### 3.1 一文件一组件

```typescript
// ❌ 错误：一个文件多个组件
@ComponentV2
struct UserCard { /* ... */ }

@ComponentV2
struct UserList { /* ... */ }

// ✅ 正确：每个组件单独文件
// UserCard.ets
@ComponentV2
struct UserCard { /* ... */ }
```

### 3.2 @Local 替代 @State

```typescript
// ❌ 错误
@Component
struct Counter {
  @State count: number = 0
}

// ✅ 正确
@ComponentV2
struct Counter {
  @Local count: number = 0

  build() {
    Button(`count: ${this.count}`)
      .onClick(() => { this.count++ })
  }
}
```

### 3.3 @Param 单向只读

```typescript
// ❌ 错误：在子组件直接修改 @Param
@ComponentV2
struct UserCard {
  @Param user: UserModel = new UserModel()
  build() {
    Button('rename')
      .onClick(() => { this.user.name = 'X' })  // 禁止
  }
}

// ✅ 正确：通过 @Event 回传
@ComponentV2
struct UserCard {
  @Param user: UserModel = new UserModel()
  @Event onRename: (newName: string) => void = () => {}
  build() {
    Button('rename')
      .onClick(() => { this.onRename('X') })
  }
}
```

---

## 四、@ObservedV2 + @Trace

```typescript
// ❌ 错误：@ObservedV2 类的字段未 @Trace
@ObservedV2
class UserModel {
  name: string = ''  // 不可观察
}

// ✅ 正确
@ObservedV2
class UserModel {
  @Trace name: string = ''
  @Trace age: number = 0
}
```

**注意：** 嵌套对象也必须 `@Trace`，否则不会触发 UI 刷新。

```typescript
@ObservedV2
class OrderModel {
  @Trace id: string = ''
  @Trace user: UserModel = new UserModel()  // 嵌套对象也 @Trace
}
```

---

## 五、@Provider / @Consumer 配对

```typescript
// ✅ 正确：键名一致
@ComponentV2
struct ParentPage {
  @Provider('userState') userModel: UserModel = new UserModel()
  build() { Column() { ChildComponent() } }
}

@ComponentV2
struct ChildComponent {
  @Consumer('userState') userModel: UserModel = new UserModel()
  build() { Text(this.userModel.name) }
}

// ❌ 错误：键名不匹配（'userState' vs 'user'）
@ComponentV2
struct ChildComponent {
  @Consumer('user') userModel: UserModel = new UserModel()  // 拿不到值
  build() { Text(this.userModel.name) }  // 永远空
}
```

---

## 六、@Monitor 替代 @Watch

```typescript
// ❌ 错误：V1 @Watch
@Component
struct Form {
  @State @Watch('onNameChange') name: string = ''
  onNameChange(): void { /* ... */ }
}

// ✅ 正确：V2 @Monitor
@ComponentV2
struct Form {
  @Local name: string = ''

  @Monitor('name')
  onNameChange(monitor: IMonitor): void {
    hilog.info(0x0000, 'Form', 'name changed: %{public}s', this.name)
  }
}
```

---

## 七、@Computed 派生值

```typescript
// ✅ 正确：纯计算
@ComponentV2
struct Cart {
  @Local items: ItemModel[] = []

  @Computed
  get total(): number {
    return this.items.reduce((sum, item) => sum + item.price, 0)
  }

  build() { Text(`total: ${this.total}`) }
}

// ❌ 错误：包含副作用
@Computed
get totalWithLog(): number {
  hilog.info(0x0000, 'Cart', 'computing...')  // 副作用
  return this.items.length
}
```

---

## 八、V1 误用检测清单

| 反模式 | 影响 | 修复 |
|--------|------|------|
| @State 在 V2 组件中 | 编译警告、未来 API 失效 | 改 @Local |
| @Link 在 V2 组件中 | 编译警告 | 改 @Param + @Event |
| @Watch 在 V2 组件中 | 编译警告 | 改 @Monitor |
| @Observed 类与 V2 混用 | UI 不刷新 | 改 @ObservedV2 + @Trace |
| @StorageLink 在 V2 组件中 | 编译警告、未来 API 失效 | 改 @Provider/@Consumer |
| @Component 与 @ComponentV2 混用 | 状态隔离异常 | 统一 V2 |

---

## 审查检查清单

- [ ] 新增代码无 V1 装饰器（@State / @Prop / @Link / @ObjectLink / @Watch / @Observed / @Provide / @Consume / @Component）
- [ ] @ComponentV2 文件一组件一文件
- [ ] @ObservedV2 类的可观察字段均 @Trace
- [ ] @Param 单向只读，子组件内不直接修改
- [ ] @Provider / @Consumer 键名配对一致
- [ ] @Monitor 替代 @Watch 正确使用
- [ ] @Computed 不包含副作用
- [ ] 嵌套对象字段也 @Trace
- [ ] 新增代码全部走 V2 装饰器体系
- [ ] V1 存量代码未做新增扩增（仅维护）
