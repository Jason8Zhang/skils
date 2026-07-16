# HAR / HSP 模块边界 审查

## 基本原则

1. **模块划分清晰** —— entry（HAP）+ 20 个 HAR/HSP（共享库）
2. **HSP 不可写资源** —— 只能 `ResourceManager.getStringSync` 读
3. **HAR 内 @Component 不可跨模块引用** —— 跨模块组件需在 entry 中包装
4. **`oh-package.json5` 锁定版本** —— 禁止 `^` / `~` 通配
5. **`overrides` 字段同步** —— CRH SDK 等二进制 har 升级
6. **多产物签名凭据走 CI 环境变量** —— 不入仓

---

## 一、项目模块结构

| 模块 | 类型 | 用途 |
|------|------|------|
| `entry` | HAP | 主应用程序（EntryAbility、pages、widgets） |
| `tztZFJY` | HAR | 交易业务 |
| `tztZFJYUI` | HAR | 交易 UI 组件 |
| `tztZFJYLogin` | HAR | 交易登录流程 |
| `tztZFHQ` | HAR | 行情数据服务 |
| `tztZFHQUI` | HAR | 行情 UI |
| `tztZFLogin` | HAR | 通用登录模块 |
| `tztZFSys` | HAR | 系统设置、隐私、权限、服务器配置 |
| `tztZFSysService` | HAR | 系统服务 |
| `tztZFUI` | HAR | 共享 UI 组件（含 tztZFRouter） |
| `tztZFWeb` | HAR | Web/H5 功能 |
| `tztZFResource` | HAR | 应用资源、路由路径、主题 |
| `tztZFShare` | HAR | 分享功能 |
| `tztZFMsgPush` | HAR | 推送通知 |
| `tztZFSpeechInfo` | HAR | 语音/信息服务 |
| `tztZFCrhSDK` | HAR | CRH SDK 集成（视频咨询） |
| `RetUtils` | HAR | 工具类（网络、加密、UI 辅助、数据采集） |
| `RetBusiness` | HAR | 业务工具类 |

`entry` 是唯一可执行模块，其他均为共享库，被 entry 依赖。

---

## 二、HSP vs HAR 区别

| 维度 | HSP（Harmony Shared Package）| HAR（Harmony Archive）|
|------|------------------------------|------------------------|
| 资源 | 只读（`getStringSync`）| 可写（直接 R 文件）|
| 组件跨模块 | 不可见 | 不可见 |
| 性能 | 共享内存、按需加载 | 静态打包 |
| 适用场景 | 跨 entry 共享基础库 | 单一 entry 内部模块 |

> 项目中除 `entry` 外都是 HAR（非 HSP），但很多模块的代码模式类似 HSP —— 资源统一从 tztZFResource 取。

---

## 三、跨模块组件（红线）

### 3.1 HAR 内 @Component 不可跨模块

```typescript
// ❌ 错误：在 tztZFUI 内定义 @ComponentV2，期望 entry 直接使用
// tztZFUI/src/main/ets/components/MyButton.ets
@ComponentV2
export struct MyButton {  // 跨模块不可见
  @Param label: string = ''
  build() { Button(this.label) }
}

// entry 引用会失败
// entry/src/main/ets/pages/Home.ets
import { MyButton } from 'tztZFUI'  // ❌ 编译错误或运行时空对象
```

### 3.2 正确做法

```typescript
// 方案 1：entry 包装组件
// entry/src/main/ets/components/MyButton.ets
import { tztZFMyButtonHelper } from 'tztZFUI'

@ComponentV2
export struct MyButton {
  @Param label: string = ''
  build() {
    Button(this.label)
      .onClick(() => tztZFMyButtonHelper.handleClick())
  }
}

// 方案 2：tztZFUI 暴露 builder 函数，entry 内嵌
// tztZFUI/src/main/ets/builder.ets
@Builder
export function tztZFMyButton(label: string, onClick: () => void) {
  Button(label).onClick(onClick)
}

// entry 引用
import { tztZFMyButton } from 'tztZFUI'
Column() {
  tztZFMyButton('click me', () => { /* ... */ })
}
```

---

## 四、模块依赖规范

### 4.1 oh-package.json5 锁定

```json5
// ❌ 错误：通配版本
{
  "dependencies": {
    "@ohos/kit": "^1.0.0"  // ❌ 通配
  }
}

// ✅ 正确：固定版本
{
  "dependencies": {
    "@ohos/kit": "1.0.5"  // ✅ 锁定
  }
}
```

### 4.2 overrides 同步（CRH SDK 等二进制 har）

```json5
// entry/oh-package.json5
{
  "overrides": {
    "@crh/video-sdk": "1.2.3",
    "@crh/anychat": "2.0.1"
  }
}
```

**升级 CRH SDK 时必须同步所有依赖模块的 `overrides`。**

### 4.3 循环依赖禁止

```
tztZFJY → tztZFJYUI → tztZFJY  // ❌ 循环
```

**检测命令：**
```bash
# 用 madge 或自定义脚本检查循环依赖
# entry 不应被其他模块依赖
```

---

## 五、HSP 资源访问

### 5.1 getStringSync

```typescript
// ✅ 正确：HSP 内访问资源
import { resourceManager } from '@kit.LocalizationKit'

const ctx = getContext()
const resMgr = ctx.resourceManager
const title = await resMgr.getStringValue($r('app.string.title'))
```

### 5.2 资源跨模块共享

```typescript
// ❌ 错误：HSP 内不能写资源
// HSP/src/main/resources/string.json
// 此文件被忽略，资源只属于 entry

// ✅ 正确：资源在 tztZFResource 集中管理
// tztZFResource/src/main/resources/base/element/string.json
{
  "string": [
    { "name": "login_title", "value": "登录" }
  ]
}

// 各模块通过 $r() 引用
Text($r('app.string.login_title'))
```

---

## 六、多产物签名

### 6.1 build-profile.json5 多产物

```json5
{
  "app": {
    "products": [
      { "name": "default", "signingConfig": "default" },
      { "name": "release", "signingConfig": "release" },
      { "name": "debug", "signingConfig": "debug" },
      { "name": "abt", "signingConfig": "abt" },
      { "name": "uat", "signingConfig": "uat" },
      { "name": "sim", "signingConfig": "sim" },
      { "name": "dev", "signingConfig": "dev" }
    ],
    "signingConfigs": {
      "release": {
        "material": {
          "storePassword": "${env.RELEASE_STORE_PASSWORD}",
          "keyPassword": "${env.RELEASE_KEY_PASSWORD}",
          "certPath": "./tztsign-release/release.p12",
          "keyAlias": "release",
          "profile": "./tztsign-release/release.p7b"
        }
      }
    }
  }
}
```

### 6.2 CI 注入凭据

```bash
# CI 环境变量
export RELEASE_STORE_PASSWORD=xxx
export RELEASE_KEY_PASSWORD=xxx

# hvigorw 引用
hvigorw assembleRelease --password-env=RELEASE
```

> 凭据**不应入仓**。本地 DevEco Studio 兼容的 `build-profile.json5` 需保持未暂存（见 CLAUDE.md "本地专用修改" 章节）。

---

## 七、模块间通信

### 7.1 通过公共模块

```typescript
// 错误：模块 A 直接 import 模块 B 的内部类
// tztZFJY/src/main/ets/.../X.ets
import { InternalService } from 'tztZFHQ/src/.../InternalService'  // ❌

// 正确：通过 tztZFResource 或公共 HAR 中转
import { HQPublicService } from 'tztZFHQ'  // ✅
```

### 7.2 事件总线

```typescript
// 共享事件总线（建议放 tztZFResource）
// tztZFResource/src/main/ets/eventbus/EventBus.ets
class EventBus {
  private static listeners: Map<string, Array<(data: ESObject) => void>> = new Map()

  static on(event: string, listener: (data: ESObject) => void): void { /* ... */ }
  static off(event: string, listener: (data: ESObject) => void): void { /* ... */ }
  static emit(event: string, data: ESObject): void { /* ... */ }
}
```

---

## 八、构建产物

### 8.1 hvigor 任务

```bash
# 整个 entry
hvigorw assembleHap

# 指定模块
hvigorw --module tztZFJY assembleHap

# 指定产物
hvigorw assembleProduct --product=uatDebug
```

### 8.2 产物输出

```
entry/build/default/outputs/default/entry-default-signed.hap
```

---

## 审查检查清单

### 模块划分
- [ ] 模块边界清晰（无跨模块强耦合）
- [ ] entry 不被其他模块依赖
- [ ] 无循环依赖
- [ ] HAR 内 @ComponentV2 未被跨模块直接引用

### 资源
- [ ] HSP 资源只读
- [ ] 跨模块资源集中在 tztZFResource
- [ ] $r() 引用而非硬编码

### 依赖管理
- [ ] oh-package.json5 版本锁定
- [ ] overrides 同步（CRH SDK 等二进制 har）
- [ ] 无通配版本

### 多产物
- [ ] build-profile.json5 凭据走环境变量
- [ ] CI 注入 RELEASE_STORE_PASSWORD 等
- [ ] 本地 build-profile.json5 不入仓

### 通信
- [ ] 模块间通过公共 HAR 通信
- [ ] 事件总线放共享模块
- [ ] 无直接 import 其他模块的内部类
