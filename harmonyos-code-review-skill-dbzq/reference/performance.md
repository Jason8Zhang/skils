# 性能 审查

## 基本原则

1. **动画属性红线** —— 改 width/height/padding/margin 触发整树 measure+layout
2. **大数据集 LazyForEach** —— 替代 ForEach 按需构建
3. **renderGroup 提升渲染层** —— 复杂动画子组件
4. **避免冗余 rebuild** —— @Local 拆细
5. **image 缓存策略** —— cachedCount + syncLoad(false)
6. **富文本复用** —— hpRichText 单例

---

## 一、动画性能红线

### 1.1 属性分类

| 属性类型 | 性能影响 | 推荐做法 |
|---------|---------|---------|
| `transform` (translate/scale/rotate) | 🟢 仅合成层重绘 | ✅ 动画首选 |
| `opacity` | 🟢 仅合成层重绘 | ✅ 动画首选 |
| `backgroundColor` | 🟡 触发重绘 | 谨慎用 |
| `width` / `height` | 🔴 触发 measure+layout | ❌ 动画禁止 |
| `padding` / `margin` | 🔴 触发 measure+layout | ❌ 动画禁止 |
| `top` / `left` | 🟡 等同 transform | 用 transform 替代 |

### 1.2 错误示例

```typescript
// ❌ 错误：动画改 width/height
@ComponentV2
struct BadCard {
  @Local width: number = 100
  @Local height: number = 50

  build() {
    Column() { Text('content') }
      .width(this.width)
      .height(this.height)
      .animation({ duration: 300 })
      .onClick(() => {
        this.width = 200  // 触发 measure+layout
        this.height = 100
      })
  }
}
```

### 1.3 正确示例

```typescript
// ✅ 正确：transform 替代
@ComponentV2
struct GoodCard {
  @Local scale: number = 1.0

  build() {
    Column() { Text('content') }
      .width(100)
      .height(50)
      .scale({ x: this.scale, y: this.scale })
      .animation({ duration: 300, curve: Curve.EaseInOut })
      .onClick(() => {
        this.scale = this.scale === 1.0 ? 1.5 : 1.0  // 仅合成层
      })
  }
}
```

### 1.4 renderGroup 提升

```typescript
// ✅ 正确：复杂动画子组件用 renderGroup
@ComponentV2
struct ComplexAnimatedPanel {
  build() {
    Column() {
      // 多层嵌套 + transform/opacity 频繁变化
    }
    .renderGroup(true)  // 独立渲染层
  }
}
```

---

## 二、列表性能

### 2.1 LazyForEach 替代 ForEach

```typescript
// ❌ 错误：ForEach 一次性构建
ForEach(this.items, (item) => { ListItem() { /* ... */ } })

// ✅ 正确：LazyForEach 按需构建
LazyForEach(this.dataSource, (item) => { ListItem() { /* ... */ } }, (item) => item.id)
```

### 2.2 key 生成器

```typescript
// ❌ 错误：无 key（性能差 + 状态错乱）
LazyForEach(this.dataSource, (item) => { /* ... */ })

// ✅ 正确：稳定 key
LazyForEach(this.dataSource, (item) => { /* ... */ }, (item) => item.id)

// ⚠️ 警告：index 作为 key（数据增删时状态错乱）
LazyForEach(this.dataSource, (item, index) => { /* ... */ }, (_, index) => index)  // 不推荐
```

### 2.3 列表项缓存

```typescript
// ✅ 正确：复用 ListItem
List() {
  LazyForEach(this.dataSource, (item) => {
    ListItem() {
      ItemComponent({ item: item })  // 组件内部做好状态隔离
    }
  }, (item) => item.id)
}
.cachedCount(3)  // 缓存 3 个
```

### 2.4 分页加载

```typescript
@ComponentV2
struct PageableList {
  @Local items: ItemModel[] = []
  @Local isLoading: boolean = false
  @Local hasMore: boolean = true
  @Local page: number = 1
  private pageSize: number = 20

  aboutToAppear() {
    this.loadNextPage()
  }

  async loadNextPage(): Promise<void> {
    if (this.isLoading || !this.hasMore) return
    try {
      this.isLoading = true
      const newItems = await this.fetchPage(this.page, this.pageSize)
      if (newItems.length < this.pageSize) {
        this.hasMore = false
      }
      this.items = this.items.concat(newItems)
      this.page++
    } finally {
      this.isLoading = false
    }
  }

  build() {
    List() {
      LazyForEach(this.dataSource, (item) => {
        ListItem() { ItemComponent({ item: item }) }
      })
      if (this.isLoading) {
        ListItem() { LoadingComponent() }
        .onAppear(() => this.loadNextPage())  // 触底加载
      }
    }
  }
}
```

---

## 三、组件重建优化

### 3.1 @Local 拆细

```typescript
// ❌ 错误：@Local 拆分过粗
@ObservedV2
class PageState {
  @Trace user: UserModel = new UserModel()
  @Trace list: ListModel[] = []
  @Trace formData: FormData = new FormData()
}

@ComponentV2
struct BadPage {
  @Local state: PageState = new PageState()
  // state.user.name 变化 → 整 state 重建 → 整页 rebuild
}

// ✅ 正确：@Local 拆细
@ComponentV2
struct GoodPage {
  @Local user: UserModel = new UserModel()
  @Local list: ListModel[] = []
  @Local formData: FormData = new FormData()
  // user.name 变化 → 仅 user 触发依赖它的组件 rebuild
}
```

### 3.2 @Computed 派生值

```typescript
@ComponentV2
struct Cart {
  @Local items: ItemModel[] = []

  @Computed
  get total(): number {
    return this.items.reduce((s, i) => s + i.price, 0)
  }

  @Computed
  get itemCount(): number {
    return this.items.length
  }
}
```

### 3.3 @Monitor 替代手动同步

```typescript
// ❌ 错误：setter 手动同步
set selectedId(id: string) {
  this._selectedId = id
  this.refreshRelatedState()
}

// ✅ 正确：@Monitor 自动响应
@Local selectedId: string = ''

@Monitor('selectedId')
onSelectedIdChange(): void {
  this.refreshRelatedState()
}
```

---

## 四、image 性能

### 4.1 缓存策略

```typescript
// ✅ 正确：设置缓存
Image($r('app.media.banner'))
  .objectFit(ImageFit.Cover)
  .cachedCount(3)        // 缓存 3 张
  .syncLoad(false)       // 异步加载
  .interpolation(ImageInterpolation.Medium)  // 中等质量插值
```

### 4.2 懒加载

```typescript
// ✅ 正确：图片懒加载（仅视口内渲染）
List() {
  LazyForEach(this.dataSource, (item) => {
    ListItem() {
      Image(item.imageUrl)
        .cachedCount(3)
        .syncLoad(false)
    }
  })
}
```

### 4.3 大图优化

```typescript
// ✅ 正确：缩略图 + 点击放大
@Local showLarge: boolean = false
@Local largeImageUrl: string = ''

build() {
  Stack() {
    Image(this.showLarge ? this.largeImageUrl : item.thumbnailUrl)
      .onClick(() => {
        this.largeImageUrl = item.imageUrl
        this.showLarge = true
      })
  }
}
```

---

## 五、富文本性能

### 5.1 hpRichText 复用

```typescript
// ❌ 错误：每次构建新实例
hpRichText({ source: htmlString })

// ✅ 正确：复用单例
@Local richTextComp: RichTextComponent = new RichTextComponent()

aboutToAppear() {
  this.richTextComp.setHtml(htmlString)
}

build() {
  this.richTextComp.render()
}
```

### 5.2 长文本分页

```typescript
@Local pageSize: number = 3000  // 单次渲染字符数
@Local currentPage: number = 0

@Computed
get pagedText(): string {
  return this.fullText.slice(this.currentPage * this.pageSize, (this.currentPage + 1) * this.pageSize)
}
```

---

## 六、状态管理性能

### 6.1 避免大对象 @Local

```typescript
// ❌ 错误：大对象整体 @Local
@Local hugeConfig: HugeConfig = new HugeConfig()  // 任何字段变化都触发依赖组件 rebuild

// ✅ 正确：拆字段
@Local configField1: string = ''
@Local configField2: number = 0
```

### 6.2 @ObservedV2 + @Trace 嵌套

```typescript
@ObservedV2
class OrderModel {
  @Trace id: string = ''
  @Trace user: UserModel = new UserModel()  // 嵌套对象也 @Trace
  @Trace items: OrderItem[] = []

  @Computed
  get total(): number {
    return this.items.reduce((s, i) => s + i.price, 0)
  }
}
```

---

## 七、启动性能

### 7.1 启动任务分阶段

```typescript
// entry/src/main/ets/startUp/TztZFStartupConfig.ets
class TztZFStartupConfig implements StartupConfigEntry {
  onConfig(): Array<StartupTaskEntry> {
    return [
      { taskName: 'InitMMKV', task: new InitMMKVTask(), dependencies: [] },
      { taskName: 'InitNetwork', task: new InitNetworkTask(), dependencies: ['InitMMKV'] },
      { taskName: 'InitPush', task: new InitPushTask(), dependencies: ['InitNetwork'] }
    ]
  }
}
```

### 7.2 隐私合规后启动

```typescript
// ✅ 正确：隐私同意后启动 SDK
if (PrivacyAgreementUtil.hasUserAgreedPrivacy()) {
  SDKRegister.setup()
}
```

### 7.3 首屏不加载非关键数据

```typescript
// ❌ 错误：首屏一次加载所有数据
async aboutToAppear() {
  await this.loadUserInfo()
  await this.loadAccountList()
  await this.loadMarketData()
  await this.loadMessageList()
}

// ✅ 正确：分阶段
async aboutToAppear() {
  await this.loadCriticalData()  // 首屏必须
  // 非关键数据延后
  setTimeout(() => this.loadAccountList(), 1000)
  setTimeout(() => this.loadMessageList(), 3000)
}
```

---

## 八、内存与资源

### 8.1 资源释放

```typescript
@ComponentV2
struct HeavyPage {
  private listener: (data: ESObject) => void = (data) => { /* ... */ }

  aboutToAppear() {
    EventBus.on('dataUpdate', this.listener)
  }

  aboutToDisappear() {
    EventBus.off('dataUpdate', this.listener)  // 释放
  }
}
```

### 8.2 image 释放

```typescript
// Image 组件销毁时自动释放，但需注意：
// - 不缓存超大图片
// - cachedCount 不超过视口可见数
```

### 8.3 定时器清理

```typescript
@ComponentV2
struct TimerPage {
  private timerId: number = -1

  aboutToAppear() {
    this.timerId = setInterval(() => { /* ... */ }, 1000)
  }

  aboutToDisappear() {
    if (this.timerId !== -1) {
      clearInterval(this.timerId)
      this.timerId = -1
    }
  }
}
```

---

## 审查检查清单

### 动画
- [ ] 动画中未改 width/height/padding/margin
- [ ] 优先 transform / opacity
- [ ] 复杂动画子组件 renderGroup(true)
- [ ] 状态驱动而非手动 setter

### 列表
- [ ] 大数据集 LazyForEach
- [ ] 提供稳定 key 生成器
- [ ] 分页加载（触底加载更多）
- [ ] cachedCount 合理

### 状态管理
- [ ] @Local 拆细，避免大对象
- [ ] @ObservedV2 嵌套字段 @Trace
- [ ] @Computed 派生值不重复计算

### 资源
- [ ] image 缓存 + 异步加载
- [ ] 富文本复用单例
- [ ] 定时器 / 事件订阅在 aboutToDisappear 清理
- [ ] 大图片按需加载（缩略图 + 大图）

### 启动
- [ ] 启动任务分阶段
- [ ] 隐私合规守门
- [ ] 首屏只加载关键数据
