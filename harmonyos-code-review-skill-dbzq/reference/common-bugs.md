# 鸿蒙常见 Bug 审查

## 概述

本文档列出融e通鸿蒙项目**实际遇到 + 鸿蒙特有**的常见 Bug，供审查时参考。共 18 条，按严重程度分级。

---

## 🔴 阻塞性 Bug

### Bug 1：V1 装饰器在 API 6.0 后失效

**症状：** 升级到鸿蒙 6.0 后 @State / @Link / @Watch 等装饰器行为异常或编译失败

**根因：** V1 装饰器在新版本被逐步废弃

**审查要点：**
```bash
# 扫描新增 .ets 文件 V1 装饰器
git diff --name-only --diff-filter=A | xargs grep -lE "@(State|Prop|Link|ObjectLink|Observed|Provide|Consume|Watch|Component)\b" 2>/dev/null
```

**修复：**
```typescript
// @State → @Local
// @Link → @Param + @Event
// @Watch → @Monitor
// @Component → @ComponentV2
```

参见 [state-mgmt-v2.md](state-mgmt-v2.md)

### Bug 2：硬编码 URL / 密钥

**症状：** 源码中存在明文 URL / token / API key

**根因：** 临时调试 / 复制粘贴遗留

**反例：**
```typescript
// ❌ entry/src/main/ets/widget/card/httprequest/tztZFHttpRequest.ets:2
const URL = "https://kh.tzt.cn/reqxml"  // 硬编码

// ❌ DeepLinking.ets
const URL = "http://action:10061/?..."  // 明文 HTTP
```

**修复：**
```typescript
// ✅ 走 BuildProfile
import { BuildProfile } from 'BuildProfile'
const URL = BuildProfile.REQUEST_URL
```

**检测命令：**
```bash
grep -rE "(http://|https://[^/]*\?[a-z_]+=[a-z0-9])" --include="*.ets" entry/ | grep -v "//"
grep -rE "(token|api_key|secret)\s*[:=]\s*['\"][a-zA-Z0-9]{16,}" --include="*.ets"
```

### Bug 3：隐私协议未守门

**症状：** 用户未同意隐私时已采集数据 / 推送已注册 / MMKV 已初始化

**根因：** `SDKRegister.setup()` 调用前未检查 `hasUserAgreedPrivacy`

**反例：**
```typescript
// ❌ EntryAbility.onCreate
onCreate(want: Want): void {
  SDKRegister.setup()  // 违规
}

// ✅ 正确
onCreate(want: Want): void {
  if (PrivacyAgreementUtil.hasUserAgreedPrivacy()) {
    SDKRegister.setup()
  }
}
```

### Bug 4：明文 HTTP

**症状：** 拦截器未升级 https，URL 直接 `http://`

**检测命令：**
```bash
grep -rE "http://" --include="*.ets" | grep -v "//"
```

**修复：**
```typescript
// 拦截器升级
class RequestHeaderEncoder implements Interceptor {
  intercept(ctx, next) {
    if (ctx.request.url.startsWith('http://')) {
      ctx.request.url = ctx.request.url.replace('http://', 'https://')
    }
    return next.handle(ctx)
  }
}
```

---

## 🟡 重要 Bug

### Bug 5：@Link / @Prop 父组件未同步

**症状：** 子组件修改 @Link 字段，父组件 UI 不更新

**根因：** 父组件未使用 @State 包裹 / @Link 字段未正确初始化

**反例：**
```typescript
// ❌ 错误
@Component
struct Parent {
  @State count: number = 0  // 应有 @State
  build() {
    Child({ count: this.count })
  }
}

@Component
struct Child {
  @Link count: number  // 父组件若无 @State 则链接失败
}
```

**修复（V1）：**
```typescript
@Component
struct Parent {
  @State count: number = 0
  build() {
    Child({ count: this.count })
  }
}
```

**V2 推荐：**
```typescript
@ComponentV2
struct Parent {
  @Local count: number = 0
  build() {
    Child({ count: this.count })
  }
}

@ComponentV2
struct Child {
  @Param count: number = 0
  @Event onCountChange: (v: number) => void = () => {}
}
```

### Bug 6：@StorageLink 在 V2 组件中误用

**症状：** V2 组件用 @StorageLink，编译警告或运行不响应

**根因：** @StorageLink 是 V1 装饰器，V2 应改用 @Provider / @Consumer

**修复：**
```typescript
// ❌ 错误
@ComponentV2
struct Page {
  @StorageLink('user') user: UserModel = new UserModel()
}

// ✅ 正确
@ComponentV2
struct Page {
  @Consumer('user') user: UserModel = new UserModel()
}

// 顶层 Provider
@ComponentV2
struct App {
  @Provider('user') user: UserModel = new UserModel()
}
```

### Bug 7：单例跨线程 race

**症状：** TaskPool 任务并发访问 `tztZFAppObj`，数据错乱

**根因：** 单例未做线程安全，TaskPool 多任务并发读写

**反例：**
```typescript
// ❌ 错误
taskpool.execute(async () => {
  tztZFAppObj.setUserInfo(user)  // race
})
```

**修复：** TaskPool 内只做纯计算，回主线程操作单例。

参见 [async-taskpool.md](async-taskpool.md) 第二章

### Bug 8：@ObservedV2 字段未 @Trace

**症状：** 修改字段 UI 不更新

**根因：** @ObservedV2 类的可观察字段必须 @Trace

```typescript
// ❌ 错误
@ObservedV2
class UserModel {
  name: string = ''  // 不可观察
}

// ✅ 正确
@ObservedV2
class UserModel {
  @Trace name: string = ''
}
```

### Bug 9：await 无 try/catch

**症状：** 网络异常导致崩溃或未提示

**反例：**
```typescript
// ❌ 错误
async aboutToAppear() {
  this.data = await fetchData()  // 异常崩溃
}

// ✅ 正确
async aboutToAppear() {
  try {
    this.data = await fetchData()
  } catch (e) {
    hilog.error(0x0000, 'Tag', 'failed: %{private}s', String(e))
    promptAction.showToast({ message: $r('app.string.network_error') })
  }
}
```

### Bug 10：aboutToDisappear 未取消订阅

**症状：** 组件销毁后回调仍触发，导致 setState 在已销毁组件上执行

**反例：**
```typescript
// ❌ 错误
aboutToAppear() {
  EventBus.on('dataUpdate', this.handleData)
}
// 缺少 aboutToDisappear off
```

**修复：**
```typescript
aboutToAppear() {
  EventBus.on('dataUpdate', this.handleData)
}

aboutToDisappear() {
  EventBus.off('dataUpdate', this.handleData)
}
```

---

## 🟢 次要 Bug

### Bug 11：console.log 残留

**症状：** 生产环境日志泄露敏感信息

**检测命令：**
```bash
grep -rE "console\.log" --include="*.ets" entry/ | wc -l
```

**修复：**
```typescript
// ❌ 错误
console.log('user info:', userInfo)

// ✅ 正确
hilog.info(0x0000, 'Tag', 'user id: %{private}s', userInfo.id)
```

### Bug 12：@ohos.router 残留

**症状：** 旧代码使用标准 router，破坏统一导航

**检测命令：**
```bash
grep -rE "@ohos\.router" --include="*.ets" .
```

**修复：** 全部改 `tztZFRouter.callRoute`

### Bug 13：catch 子句带类型

**症状：** ArkTS 编译失败

**反例：**
```typescript
try { /* ... */ } catch (e: any) { /* ... */ }  // 编译失败
```

**修复：**
```typescript
try { /* ... */ } catch (e) { /* ... */ }
```

### Bug 14：动画改 width/height

**症状：** 动画卡顿、掉帧

**修复：** 改用 transform / scale / opacity

参见 [ui-arkui.md](ui-arkui.md) 第一章

### Bug 15：硬编码字符串/颜色/尺寸

**症状：** 国际化、暗色模式失效

**反例：**
```typescript
Text('登录').fontSize(16).fontColor('#333333')
```

**修复：**
```typescript
Text($r('app.string.login'))
  .fontSize($r('app.float.font_size_body'))
  .fontColor($r('app.color.text_primary'))
```

### Bug 16：ForEach 用于大数据集

**症状：** 10000+ 列表项首屏卡死

**修复：** 用 LazyForEach

### Bug 17：解构赋值/参数

**症状：** ArkTS 编译失败

**反例：**
```typescript
const { name, age } = user  // 编译失败
```

**修复：**
```typescript
const name = user.name
const age = user.age
```

### Bug 18：富文本 HTML 注入

**症状：** 用户提交 HTML 中含 `<script>` 标签

**修复：**
```typescript
function sanitizeHtml(input: string): string {
  return input.replace(/<script[^>]*>.*?<\/script>/gi, '')
              .replace(/on\w+="[^"]*"/g, '')
              .replace(/javascript:/gi, '')
}
```

---

## 审查检查清单

### 阻塞
- [ ] 无 V1 装饰器新增
- [ ] 无硬编码 URL / 密钥
- [ ] SDKRegister.setup() 由 hasUserAgreedPrivacy 守门
- [ ] 无明文 HTTP

### 重要
- [ ] @Link / @Prop 父组件已同步
- [ ] V2 组件不用 @StorageLink
- [ ] TaskPool 内不触碰单例
- [ ] @ObservedV2 字段都 @Trace
- [ ] await 都有 try/catch
- [ ] aboutToDisappear 取消订阅

### 次要
- [ ] 无 console.log
- [ ] 无 @ohos.router
- [ ] catch 无类型
- [ ] 动画不改 width/height
- [ ] 字符串/颜色/尺寸走 $r()
- [ ] 大数据集用 LazyForEach
- [ ] 无解构
- [ ] 富文本过滤 HTML
