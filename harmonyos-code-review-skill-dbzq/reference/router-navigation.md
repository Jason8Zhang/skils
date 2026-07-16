# 路由与 Navigation 审查

## 基本原则

1. **禁止新增 `@ohos.router`** —— 全部走项目自定义路由 `tztZFRouter.callRoute` 或标准 `Navigation` + `NavPathStack`
2. **标准 Navigation 必须绑定 NavPathStack** —— `Navigation(this.navPathStack)` 形式
3. **deepLink 参数必须白名单校验** —— 防注入
4. **多 Tab 栈独立管理** —— `tztZFNavigationController.dictMap: Map<number, NavPathStack>` 隔离

---

## 一、禁用 @ohos.router（红线）

```typescript
// ❌ 错误：使用 @ohos.router
import router from '@ohos.router'

router.pushUrl({ url: 'pages/Detail' })
router.replaceUrl({ url: 'pages/Settings' })
router.back()

// ✅ 正确：使用项目自定义路由
import { tztZFRouter } from 'tztZFUI'

tztZFRouter.callRoute('pages/Detail', 'push', { id: '123' })
tztZFRouter.callRoute('pages/Settings', 'replace')
tztZFRouter.callRoute('pages/Back', 'pop')
```

**检测命令：**
```bash
grep -rE "@ohos\.router" --include="*.ets" .
# 输出应为空（除文档/注释外）
```

---

## 二、标准 Navigation 模式

### 2.1 基础结构

```typescript
// ✅ 正确：Navigation 绑定 NavPathStack
@ComponentV2
struct MainPage {
  @Local navPathStack: NavPathStack = new NavPathStack()

  build() {
    Navigation(this.navPathStack) {
      // Home content
    }
    .navDestination(this.routerMap)
  }

  @Builder
  routerMap(name: string, param: ESObject) {
    if (name === 'detail') {
      DetailPage()
    } else if (name === 'settings') {
      SettingsPage()
    }
  }
}
```

### 2.2 页面操作

```typescript
// push 新页面
this.navPathStack.pushPath({ name: 'detail', param: { id: '123' } })

// replace 当前页面
this.navPathStack.replacePath({ name: 'settings' })

// pop 返回
this.navPathStack.pop()

// pop 到根
this.navPathStack.clear()
```

### 2.3 NavDestination 子页

```typescript
@ComponentV2
struct DetailPage {
  build() {
    NavDestination() {
      Column() {
        Text($r('app.string.detail_title'))
      }
    }
    .title($r('app.string.detail_nav_title'))
  }
}
```

---

## 三、项目自定义路由 tztZFRouter

### 3.1 标准调用

```typescript
import { tztZFRouter } from 'tztZFUI'

// 基本跳转
tztZFRouter.callRoute(path: string, action: 'push' | 'pop' | 'replace' | 'popToRoot',
                      param?: Record<string, ESObject>,
                      callback?: (data: ESObject) => void)
```

**使用示例：**

```typescript
// push 跳转
tztZFRouter.callRoute('detail', 'push', { id: '123' })

// pop 并回传数据
tztZFRouter.callRoute('orderList', 'pop', {}, (data) => {
  hilog.info(0x0000, 'Tag', 'callback: %{public}s', JSON.stringify(data))
})

// replace
tztZFRouter.callRoute('login', 'replace')
```

### 3.2 路由步骤观察

```typescript
import { tztZFRouteStep } from 'tztZFUI'

tztZFRouteStep.observe((step) => {
  hilog.info(0x0000, 'Tag', 'route step: %{public}s', step.action)
})
```

### 3.3 多 Tab 栈隔离

```typescript
// tztZFNavigationController 内部维护
private dictMap: Map<number, NavPathStack> = new Map()

// 通过 tab 索引 push
public pushByTab(tabIndex: number, path: string, param: ESObject): void {
  const stack = this.dictMap.get(tabIndex)
  if (stack) {
    stack.pushPath({ name: path, param: param })
  }
}
```

**审查要点：**
- 多 Tab 跳转必须用 `pushByTab(tabIndex, ...)`，避免栈污染
- 切换 Tab 时不应清空其他 Tab 的栈（保持各自独立）
- `addUniquePageName` 去重机制是否触发

---

## 四、deepLink 校验

### 4.1 白名单校验

```typescript
// ✅ 正确：白名单校验
function handleDeepLink(uri: string): void {
  const allowedPaths: string[] = ['detail', 'settings', 'profile']
  const parsed = new URL(uri)
  const path = parsed.pathname.replace('/', '')

  if (!allowedPaths.includes(path)) {
    hilog.warn(0x0000, 'DeepLink', 'Invalid path: %{public}s', path)
    return
  }

  // 校验参数白名单
  const allowedParams: string[] = ['id', 'type', 'token']
  const param: Record<string, string> = {}
  parsed.searchParams.forEach((v, k) => {
    if (allowedParams.includes(k)) {
      param[k] = v
    }
  })

  tztZFRouter.callRoute(path, 'push', param)
}

// ❌ 错误：直接透传
function handleDeepLink(uri: string): void {
  const parsed = new URL(uri)
  const path = parsed.pathname.replace('/', '')
  tztZFRouter.callRoute(path, 'push', { /* 全部参数透传 */ })  // 危险
}
```

### 4.2 scheme 注册校验

`module.json5` 中 `querySchemes` 必须与代码中 `link` 调用一致：

```json5
{
  "module": {
    "abilities": [
      {
        "skills": [
          {
            "uris": [
              { "scheme": "tzt", "host": "detail" }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## 五、页面注册

### 5.1 main_pages.json

`entry/src/main/resources/base/profile/main_pages.json` 必须注册所有首屏页面：

```json5
{
  "src": [
    "pages/Index",
    "pages/Home",
    "pages/Login"
  ]
}
```

### 5.2 navDestination 注册

子页通过 `Navigation.navDestination(this.routerMap)` 动态注册，不需写入 main_pages.json。

---

## 审查检查清单

- [ ] 无新增 `@ohos.router` 引用
- [ ] Navigation 组件绑定 NavPathStack
- [ ] NavDestination 子页在 `navDestination` 中注册
- [ ] 跳转统一走 `tztZFRouter.callRoute`
- [ ] 多 Tab 跳转走 `pushByTab` 隔离栈
- [ ] deepLink 参数白名单校验
- [ ] deepLink scheme 与 module.json5 一致
- [ ] main_pages.json 注册所有首屏页面
- [ ] 路由路径与 navDestination name 一致
- [ ] 路由参数类型为 `ESObject` 或具体类型
