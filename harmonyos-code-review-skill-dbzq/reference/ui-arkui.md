# ArkUI 渲染与组件 审查

## 基本原则

1. **动画属性红线** —— 禁止频繁改 `width` / `height` / `padding` / `margin`
2. **大数据集用 LazyForEach** —— 替代 ForEach 避免一次构建
3. **复杂动画 renderGroup(true)** —— 减少渲染批次
4. **资源引用走 `$r()`** —— 字符串/颜色/尺寸
5. **组件文件 < 400 行** —— 接近 800 行必须拆分

---

## 一、动画属性红线（🚨 一票否决）

### 1.1 禁用动画改尺寸

```typescript
// ❌ 错误：动画改 width / height / padding / margin（性能灾难）
@ComponentV2
struct BadCard {
  @Local cardWidth: number = 100
  @Local cardHeight: number = 50

  build() {
    Column()
      .width(this.cardWidth)
      .height(this.cardHeight)
      .padding(10)
      .animation({ duration: 300 })
      .onClick(() => {
        this.cardWidth = 200
        this.cardHeight = 100
        this.padding = 20
      })
  }
}

// ✅ 正确：用 transform / scale 替代
@ComponentV2
struct GoodCard {
  @Local cardScale: number = 1.0

  build() {
    Column() {
      Text('content')
    }
    .width(100)
    .height(50)
    .padding(10)
    .scale({ x: this.cardScale, y: this.cardScale })
    .animation({ duration: 300, curve: Curve.EaseInOut })
    .onClick(() => {
      this.cardScale = this.cardScale === 1.0 ? 1.5 : 1.0
    })
  }
}
```

**原因：** 改 width/height/padding/margin 触发整个组件树重新 measure + layout，开销大。transform/opacity 仅触发 GPU 合成层，60fps 流畅。

### 1.2 状态驱动动画

```typescript
// ✅ 正确：声明式 + 状态驱动
@ComponentV2
struct AnimatedCard {
  @Local isExpanded: boolean = false
  @Local cardScale: number = 0.8
  @Local cardOpacity: number = 0.5

  build() {
    Column() {
      // content
    }
    .scale({ x: this.cardScale, y: this.cardScale })
    .opacity(this.cardOpacity)
    .animation({ duration: 300, curve: Curve.EaseInOut })
    .onClick(() => {
      this.isExpanded = !this.isExpanded
      this.cardScale = this.isExpanded ? 1.0 : 0.8
      this.cardOpacity = this.isExpanded ? 1.0 : 0.5
    })
  }
}

// ✅ 正确：显式 animateTo
animateTo({ duration: 300, curve: Curve.EaseInOut }, () => {
  this.isExpanded = true
  this.cardScale = 1.0
})
```

---

## 二、列表与懒加载

### 2.1 LazyForEach 替代 ForEach

```typescript
// ❌ 错误：ForEach 一次性构建所有 item
@ComponentV2
struct BadList {
  @Local items: ItemModel[] = []  // 假设 10000 条

  aboutToAppear() {
    for (let i = 0; i < 10000; i++) {
      this.items.push(new ItemModel(i))
    }
  }

  build() {
    List() {
      ForEach(this.items, (item: ItemModel) => {  // 一次性构建 10000 个
        ListItem() { ItemComponent({ item: item }) }
      })
    }
  }
}

// ✅ 正确：LazyForEach 按需构建
class ItemDataSource implements IDataSource {
  private items: ItemModel[] = []

  totalCount(): number {
    return this.items.length
  }

  getData(index: number): ItemModel {
    return this.items[index]
  }

  registerDataChangeListener(listener: DataChangeListener): void {
    // ...
  }

  unregisterDataChangeListener(listener: DataChangeListener): void {
    // ...
  }
}

@ComponentV2
struct GoodList {
  @Local dataSource: ItemDataSource = new ItemDataSource()

  aboutToAppear() {
    for (let i = 0; i < 10000; i++) {
      this.dataSource.items.push(new ItemModel(i))
    }
    this.dataSource.notifyDataReload()
  }

  build() {
    List() {
      LazyForEach(this.dataSource, (item: ItemModel) => {
        ListItem() { ItemComponent({ item: item }) }
      }, (item: ItemModel) => item.id)  // key 生成器必填
    }
  }
}
```

### 2.2 key 生成器必填

```typescript
// ❌ 错误：无 key 生成器
LazyForEach(this.dataSource, (item: ItemModel) => { /* ... */ })

// ✅ 正确：提供稳定 key
LazyForEach(this.dataSource, (item: ItemModel) => { /* ... */ }, (item: ItemModel) => item.id)
```

---

## 三、renderGroup

```typescript
// ✅ 正确：复杂动画子组件用 renderGroup 减少渲染批次
@ComponentV2
struct ComplexAnimatedChild {
  build() {
    Column() {
      // 复杂子组件
    }
    .renderGroup(true)  // 提升到独立渲染层
  }
}
```

**适用场景：**
- 多层嵌套的复杂动画
- 半透明 / 模糊 / 阴影效果叠加
- transform / opacity 频繁变化

---

## 四、资源引用

### 4.1 强制使用 $r()

```typescript
// ❌ 错误：硬编码字符串
Text('登录')
  .fontSize(16)
  .fontColor('#333333')
  .backgroundColor('#FFFFFF')
  .width(100)
  .height(40)

// ✅ 正确：$r() 引用资源
Text($r('app.string.login'))
  .fontSize($r('app.float.font_size_body'))
  .fontColor($r('app.color.text_primary'))
  .backgroundColor($r('app.color.bg_primary'))
  .width($r('app.float.button_width'))
  .height($r('app.float.button_height'))
```

### 4.2 资源类型

| 资源 | 引用 | 文件位置 |
|------|------|---------|
| 字符串 | `$r('app.string.xxx')` | `resources/base/element/string.json` |
| 颜色 | `$r('app.color.xxx')` | `resources/base/element/color.json` |
| 尺寸 | `$r('app.float.xxx')` | `resources/base/element/float.json` |
| 媒体 | `$r('app.media.xxx')` | `resources/base/media/` |
| 插图 | `$r('app.symbol.xxx')` | 鸿蒙 Symbol |

### 4.3 国际化

```typescript
// 暗色模式颜色自动切换
// light: color.json
// dark: color.json（在 dark 元素目录）
// 引用端不变
.fontColor($r('app.color.text_primary'))  // 自动切换
```

---

## 五、组件复用

### 5.1 @Builder 抽取

```typescript
// ✅ 正确：轻量 UI 片段用 @Builder
@ComponentV2
struct OrderCard {
  @Param order: OrderModel = new OrderModel()

  @Builder
  statusTag(status: string) {
    Text(status)
      .fontSize(10)
      .fontColor(Color.White)
      .backgroundColor('#FF0000')
      .padding(4)
  }

  build() {
    Column() {
      this.statusTag(this.order.status)
      Text(this.order.title)
    }
  }
}
```

### 5.2 组件抽取原则

- 跨文件复用 → 单独 .ets 文件 + @ComponentV2 + @Param + @Event
- 文件内复用 → @Builder
- 单文件 < 400 行
- 接近 800 行必须拆分

---

## 六、状态拆分粒度

```typescript
// ❌ 错误：@Local 拆分过粗，触发整组件 rebuild
@ComponentV2
struct BadForm {
  @Local formData: FormData = new FormData()  // 任何字段变化都 rebuild

  build() {
    Column() {
      TextInput({ text: this.formData.name })
      TextInput({ text: this.formData.phone })
      Button(this.formData.submitText)
    }
  }
}

// ✅ 正确：@Local 拆细
@ComponentV2
struct GoodForm {
  @Local name: string = ''
  @Local phone: string = ''
  @Local isSubmitting: boolean = false

  build() {
    Column() {
      TextInput({ text: this.name })
        .onChange((v) => { this.name = v })
      TextInput({ text: this.phone })
        .onChange((v) => { this.phone = v })
      Button(this.isSubmitting ? '提交中...' : '提交')
    }
  }
}
```

---

## 七、布局性能

### 7.1 避免深嵌套

```typescript
// ❌ 错误：深嵌套布局
Column() {
  Row() {
    Column() {
      Row() {
        Column() {
          Text('content')
        }
      }
    }
  }
}

// ✅ 正确：扁平布局
Column() {
  Row() {
    Text('content')
  }
}
```

### 7.2 优先 Grid / List

```typescript
// ❌ 错误：用 Column/Row 模拟列表
Column() {
  ForEach(this.items, (item) => { Row() { /* ... */ } })
}

// ✅ 正确：List/Grid + LazyForEach
List() {
  LazyForEach(this.dataSource, (item) => {
    ListItem() { /* ... */ }
  }, (item) => item.id)
}
```

---

## 八、富文本与图片

### 8.1 hpRichText 复用

```typescript
// ❌ 错误：每次构建新实例
hpRichText({ source: htmlString })

// ✅ 正确：复用 hpRichText 实例
@Local richTextComp: RichTextComponent = new RichTextComponent()
build() {
  this.richTextComp.source = htmlString
  this.richTextComp.render()
}
```

### 8.2 image 缓存

```typescript
// ✅ 正确：设置缓存策略
Image($r('app.media.banner'))
  .objectFit(ImageFit.Cover)
  .cachedCount(3)  // 缓存 3 张
  .syncLoad(false) // 异步加载
```

---

## 审查检查清单

### 动画
- [ ] 动画中未改 width/height/padding/margin
- [ ] 优先使用 transform / opacity
- [ ] 状态驱动动画或显式 animateTo
- [ ] 复杂动画子组件 renderGroup(true)

### 列表
- [ ] 大数据集使用 LazyForEach
- [ ] LazyForEach 提供 key 生成器
- [ ] 优先 List/Grid 而非 Column/Row 模拟

### 资源
- [ ] 字符串 / 颜色 / 尺寸走 $r() 引用
- [ ] 资源文件 base + 各语言目录完整
- [ ] 暗色模式颜色已配置

### 组件
- [ ] 组件文件 < 400 行
- [ ] 跨文件复用抽组件，单文件复用 @Builder
- [ ] @Local 拆细避免整组件 rebuild

### 布局
- [ ] 避免深嵌套（> 4 层）
- [ ] 优先扁平布局
- [ ] 富文本 / image 复用
