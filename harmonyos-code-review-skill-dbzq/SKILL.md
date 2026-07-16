---
name: harmonyos-code-review-skill-dbzq
description: 鸿蒙代码审查技能（融e通专项版）。基于需求文档对鸿蒙 ArkTS 代码进行系统化审查，覆盖 V2 状态管理、自定义路由、ArkUI 渲染、TaskPool 并发、HUKS 安全等鸿蒙特有审查点。触发关键词：代码审查、code review、审查 PR、审查 commit、review this、鸿蒙审查、ArkTS 审查。
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# 鸿蒙代码审查技能（融e通专项版）

## 技能概述

本技能针对东北证券融e通鸿蒙项目（ArkTS 为主 + 少量 TS）定制，基于需求文档对代码进行全面审查，确保功能完整实现且代码质量达标。覆盖 V1→V2 状态管理迁移期、自定义路由 `tztZFRouter`、MMKV 本地存储、CRH SDK 集成等融e通特有技术栈。

**何时使用：**
- 提供需求文档和代码变更时
- 验证功能实现完整性时
- 上线前综合代码审查
- 生成结构化审查报告
- V1→V2 装饰器迁移把关

**审查维度：**
1. ArkTS 语言合规（编译期强约束）
2. V2 状态管理（架构级强制）
3. 路由与 Navigation（自定义 vs 标准）
4. ArkUI 渲染与组件（性能与规范）
5. 异步与 TaskPool（线程与生命周期）
6. HAR/HSP 模块边界
7. 鸿蒙安全审查（HUKS / HTTPS / 隐私）
8. 性能审查（动画 / 列表 / 资源）
9. 测试完整性验证

---

## 审查流程

### 阶段 1：需求理解（3-5 分钟）

**输入：** 需求文档、PR 描述、关联 Issue

**行动：**
1. 阅读并理解需求文档
2. 提取关键功能点
3. 识别技术要求和约束
4. 标记关键风险点（V1→V2 兼容性、隐私合规、性能红线）

**输出：** 需求功能清单

### 阶段 2：代码变更分析（5 分钟）

**行动：**
1. 查看变更文件列表
2. 评估变更规模
3. 识别核心修改文件
4. 检查是否有测试文件
5. **识别鸿蒙技术栈**

**技术栈识别：**

| 检测文件 / 信号 | 技术栈 |
|---------|--------|
| `build-profile.json5` + `hvigorfile.ts` | hvigor 5.0.0 + 鸿蒙构建系统 |
| `oh-package.json5` + `oh_modules/` | ohpm 依赖管理 |
| `*.ets` 大量 + `*.ts` 少量 | ArkTS 主语言 |
| `@ComponentV2` 多于 `@Component` | 处于 V2 迁移中或已完成 |
| `tztZFRouter.callRoute` 或 `tztZFNavigationController` | 项目自定义路由（非标准 Navigation） |
| `@tencent/mmkv` 引用 | MMKV 取代 Preferences |
| `tztZFCrhSDK` / `@crh/*` | CRH 视频 SDK 集成 |
| `rcp.Session` + `GatewayRequester` | 自研网络层（@kit.RemoteCommunicationKit） |
| `StartupConfigEntry` + `TaskPool` | 鸿蒙启动框架 + TaskPool 并发 |

**工具：**
```bash
# 查看变更统计
git diff --stat

# 识别技术栈
cat build-profile.json5 | grep -E "compatibleSdk|target"
cat oh-package.json5 | grep -E "@tencent|@crh|@ohos"

# V1/V2 装饰器使用统计
grep -rE "@(State|Prop|Link|ObjectLink|Provide|Consume|Watch|Observed|Component)\b" --include="*.ets" | wc -l
grep -rE "@(ComponentV2|Local|Param|Event|Provider|Consumer|Monitor|Computed|ObservedV2|Trace)\b" --include="*.ets" | wc -l

# 检测红线反模式
grep -rE "@ohos.router" --include="*.ets"
grep -rE "http://" --include="*.ets" | grep -v "//"
grep -rE "console\.log" --include="*.ets" entry/ | wc -l
```

**输出：** 技术栈识别结果（V1/V2 比例、路由方案、依赖 SDK 列表）

### 阶段 3：功能实现验证（10-15 分钟）

**对照需求检查代码：**

1. **功能完整性检查**
   - 每个需求点是否有对应实现？
   - 边界情况是否处理？（空数据、网络错误、权限拒绝）
   - 错误处理是否完整？（try/catch + 友好提示）

2. **代码追踪**
   - 从入口追踪到实现（EntryAbility → ViewController → Service）
   - 验证数据流是否正确
   - 检查接口定义与实现一致性
   - 特别关注：隐私协议守门是否到位（`SDKRegister.hasInitAfterPrivacyAgreed()`）

### 阶段 4：架构审查（10 分钟）

参考 [architecture.md](reference/architecture.md)

**检查项：**

1. **SOLID 原则**
   - 单一职责：类/模块职责是否清晰？
   - 开闭原则：是否易于扩展？
   - 依赖注入：是否合理？
   - 接口隔离：接口是否精简？
   - 依赖倒置：是否依赖抽象？

2. **MVVM 架构（项目实际变体）**
   - View：仅渲染逻辑，不在 `build()` 内放业务逻辑
   - ViewModel：所有业务逻辑封装（Controller 持 page 生命周期）
   - Model：纯数据类，@ObservedV2 + @Trace
   - Service：网络请求、数据库、文件 IO

3. **模块化（HSP / HAR）**
   - 模块边界是否清晰？（entry / tztZFJY / tztZFHQ / RetUtils / ...）
   - 是否存在跨模块强耦合？
   - HAR 内 @Component 跨模块不可见 —— 是否误用？

4. **自定义路由 `tztZFRouter`**
   - 路由职责是否单一（path 解析 + 步骤观察 + 跨模块传参 + deepLink）？
   - 多 Tab 栈隔离是否正确（`dictMap: Map<number, NavPathStack>`）？

### 阶段 5：专项审查（15-20 分钟）

**根据文件类型，参考对应的 reference 文档。**

#### 5.1 ArkTS 语言合规审查
参考 [arkts-language.md](reference/arkts-language.md)

- [ ] 是否使用 `any` / `unknown` / `Object` / `as const`？
- [ ] 是否有解构赋值 / 解构参数声明？
- [ ] 是否使用 `for...in` / `delete` / `in` 操作符？
- [ ] 是否使用 `function` 表达式（非箭头）？
- [ ] 是否调用 `apply` / `call` / `bind`？
- [ ] catch 子句是否带类型标注？
- [ ] 是否使用 `require()` / `export = ...` / UMD？
- [ ] 是否使用 `var` / `with` / JSX / `#` 私有字段？
- [ ] 是否使用 `Record` / `Partial` / `Required` / `Readonly` 之外的工具类型？

#### 5.2 V2 状态管理审查
参考 [state-mgmt-v2.md](reference/state-mgmt-v2.md)

- [ ] 是否误用 V1 装饰器（@State / @Prop / @Link / @ObjectLink / @Watch / @Observed / @Provide / @Consume / @Component）？
- [ ] @ComponentV2 文件是否一个组件一个文件？
- [ ] @ObservedV2 类的可观察字段是否 @Trace 标注？
- [ ] @Param 是否单向只读、且不在子组件直接修改？
- [ ] @Provider / @Consumer 键名是否配对一致？
- [ ] @Computed 是否包含副作用？
- [ ] @Monitor 是否替代 @Watch 正确使用？

#### 5.3 路由与 Navigation 审查
参考 [router-navigation.md](reference/router-navigation.md)

- [ ] 是否新增 `@ohos.router` 引用？
- [ ] Navigation 组件是否绑定 NavPathStack？
- [ ] NavDestination 子页是否在 `navDestination` 中注册？
- [ ] 是否统一走 `tztZFRouter.callRoute`？
- [ ] deep link 参数是否经过白名单校验？
- [ ] 多 Tab 栈 push 是否走 `dictMap` 索引隔离？

#### 5.4 ArkUI 渲染与组件审查
参考 [ui-arkui.md](reference/ui-arkui.md)

- [ ] 动画中是否改动 `width` / `height` / `padding` / `margin`？（红线）
- [ ] 大数据集是否使用 LazyForEach？
- [ ] 复杂动画子组件是否设 `renderGroup(true)`？
- [ ] 是否优先使用 `transform` / `opacity`？
- [ ] 字符串/颜色/尺寸是否使用 `$r('app.string/...')` 引用？
- [ ] 组件文件是否 < 400 行、接近 800 行是否拆分？

#### 5.5 异步与 TaskPool 审查
参考 [async-taskpool.md](reference/async-taskpool.md)

- [ ] UI 操作是否在主线程？
- [ ] TaskPool 内是否触碰单例（如 `tztZFAppObj` / `tztZFNavigationController`）？
- [ ] Promise/await 异步错误处理是否完整？
- [ ] aboutToAppear 内的异步逻辑是否有竞态风险？
- [ ] 网络 IO 是否正确使用 `rcp.Session` 拦截器？

#### 5.6 HAR / HSP 模块边界审查
参考 [har-hsp-module.md](reference/har-hsp-module.md)

- [ ] HSP 模块内是否尝试写资源？
- [ ] HAR 内 @Component 是否被跨模块引用？
- [ ] `oh-package.json5` 是否锁定版本？
- [ ] `overrides` 字段（如 CRH SDK）是否同步？
- [ ] 多产物签名（default / release / debug / abt / uat / sim / dev）是否在 CI 环境变量注入？

#### 5.7 鸿蒙安全审查
参考 [security.md](reference/security.md)

**🚨 安全红线（一票否决）：**
- [ ] 源码中是否硬编码密钥 / token / 密码？
- [ ] 是否使用明文 HTTP（非 HTTPS）？
- [ ] module.json5 权限声明与代码调用是否一致？
- [ ] 敏感数据是否走 HUKS 加密？
- [ ] 日志是否泄露敏感信息（`%{public}s` vs `%{private}s`）？
- [ ] 隐私协议未同意时是否调用了 `SDKRegister.setup()`？

> 若触发任何安全红线，直接标记为 **阻塞性问题**。

#### 5.8 性能审查
参考 [performance.md](reference/performance.md)

- [ ] 动画属性红线（width/height/padding/margin 改动）？
- [ ] List/Grid 大数据集使用 LazyForEach？
- [ ] 复杂动画设 `renderGroup(true)`？
- [ ] image 是否有缓存策略？
- [ ] 是否有冗余 rebuild（@Local 拆分过粗）？
- [ ] 富文本（`@ohasasugar/hp-richtext`）是否有复用？

#### 5.9 编码规范审查
参考 [coding-style.md](reference/coding-style.md)

- [ ] 命名规范是否符合项目标准（`tztZF*` 前缀、PascalCase 文件、camelCase 工具）？
- [ ] 行宽是否 ≤ 100？
- [ ] 公共方法是否有 JSDoc 中文注释？
- [ ] 是否有 `console.log` 残留（应改 hilog）？
- [ ] import 顺序是否规范（import 在最前）？
- [ ] 单例模式是否避免可变全局状态？

#### 5.10 鸿蒙常见 Bug 检查
参考 [common-bugs.md](reference/common-bugs.md)

- [ ] V1 装饰器在 6.0 之后 API 失效
- [ ] @Link / @Prop 父组件未同步导致 UI 不更新
- [ ] 单例跨线程 race 条件
- [ ] 硬编码 URL（应走 BuildProfile 配置）
- [ ] @StorageLink 在 V2 环境下应改 @Provider/@Consumer
- [ ] await 错误处理缺失

### 阶段 6：测试审查（5 分钟）

参考 [testing.md](reference/testing.md)

- [ ] 是否有单元测试（`src/ohosTest/ets/test/`）？
- [ ] 是否有 UI 测试（@ohos.UiTest）？
- [ ] 测试覆盖率是否 ≥ 80%？
- [ ] 边界情况是否测试（空数据、权限拒绝、网络错误）？
- [ ] V2 状态变更是否触发 UI 重新渲染（集成测试）？
- [ ] NavPathStack push/pop 流程是否被覆盖？

---

## 审查报告模板

```markdown
# 鸿蒙代码审查报告

**审查日期：** YYYY-MM-DD
**审查人：** [姓名/AI]
**PR/Commit：** [链接/哈希]
**审查时长：** X 分钟

---

## 技术栈识别

**自动识别结果：**
- 主语言：ArkTS（占 X%）+ TS（hvigor 脚本）
- 状态管理：V1 X 处 vs V2 X 处（迁移期）
- 路由方案：自定义 `tztZFRouter` / 标准 Navigation
- 本地存储：MMKV
- 网络层：`@kit.RemoteCommunicationKit` + 拦截器
- 第三方 SDK：CRH / BugLy / 推送

**识别依据：**
- 检测到 `build-profile.json5` → hvigor 5.0.0
- 检测到 `@ComponentV2` 112 处 vs `@Component` 18 处 → 处于 V1→V2 迁移期
- 检测到 `tztZFNavigationController` → 项目自定义路由
- 检测到 `@tencent/mmkv` → MMKV 取代 Preferences

---

## 一、本次需求内容

### 需求概述
[简要描述需求内容]

### 需求文档
[需求文档链接或关键内容]

---

## 二、本次改动范围

### 变更文件统计
- 修改文件数：X
- 新增代码行数：+X
- 删除代码行数：-X
- 新增 .ets 文件：X
- 新增 .test.ets 文件：X

### 核心变更文件
1. `entry/src/main/ets/.../File.ets` - [变更说明]
2. `tztZFJY/src/main/ets/.../File.ets` - [变更说明]

### 影响范围
- 影响模块：[entry / tztZFJY / tztZFHQ / ...]
- 影响界面：[UI 列表]
- 数据库变更：[是/否，说明]
- 权限变更：[是/否，说明]

---

## 三、需求实现情况

### 功能覆盖度

| 需求点 | 实现状态 | 实现位置 | 验证结果 |
|--------|---------|---------|---------|
| [需求 1] | ✅ 已实现 | `File.ets:50-120` | ✅ 通过 |
| [需求 2] | ⚠️ 部分实现 | `File.ets:30` | ⚠️ 缺少边界处理 |
| [需求 3] | ❌ 未实现 | - | ❌ 缺失 |

---

## 四、架构合理性评估

| 原则 | 评估 | 说明 |
|------|------|------|
| 单一职责 | ✅/⚠️/❌ | [说明] |
| MVVM 分层 | ✅/⚠️/❌ | [说明] |
| 模块划分 | ✅/⚠️/❌ | [说明] |
| 路由职责 | ✅/⚠️/❌ | [说明] |
| 依赖倒置 | ✅/⚠️/❌ | [说明] |

---

## 五、代码质量审查

### 5.1 ArkTS 语言合规 📐

**评估：** ✅ 优秀 / 🟡 良好 / 🟠 合格 / 🔴 需改进

**发现的问题：**
1. 🟡 [问题描述]
   - 位置：`File.ets:123`
   - 建议：[改进建议]

### 5.2 V2 状态管理 🎛️

**评估：** ✅ 优秀 / 🟡 良好 / 🟠 合格 / 🔴 需改进

**发现的问题：**
1. 🔴 新增代码误用 V1 装饰器
   - 位置：`File.ets:50`
   - 建议：改为 @ComponentV2 + @Local

### 5.3 路由与 Navigation 🧭

**评估：** ✅ 优秀 / 🟡 良好 / 🟠 合格 / 🔴 需改进

**发现的问题：**
- 无重大问题

### 5.4 ArkUI 渲染 🎨

**评估：** ✅ 优秀 / 🟡 良好 / 🟠 合格 / 🔴 需改进

**发现的问题：**
- 无重大问题

### 5.5 异步与 TaskPool ⚡

**评估：** ✅ 优秀 / 🟡 良好 / 🟠 合格 / 🔴 需改进

**发现的问题：**
1. 🟡 TaskPool 内调用 `tztZFAppObj` 单例
   - 位置：`File.ets:80`
   - 建议：参考 `tztZFStartupTaskAsync.ets` 注释，避免在 TaskPool 中调用单例方法

### 5.6 HAR / HSP 模块边界 📦

**评估：** ✅ 优秀 / 🟡 良好 / 🟠 合格 / 🔴 需改进

**发现的问题：**
- 无重大问题

### 5.7 鸿蒙安全 🔒

**评估：** ✅ 优秀 / 🟡 良好 / 🟠 合格 / 🔴 需改进

**🚨 安全红线：**
- [✅] 无硬编码密钥
- [✅] HTTPS 强制
- [✅] 隐私合规守门到位

### 5.8 性能 ⚡

**评估：** ✅ 优秀 / 🟡 良好 / 🟠 合格 / 🔴 需改进

**发现的问题：**
- 无重大问题

### 5.9 编码规范 ✏️

**评估：** ✅ 符合 / 🟡 部分符合 / ❌ 不符合

- [✅] 命名规范（tztZF* 前缀）
- [✅] 缩进格式
- [⚠️] console.log 残留

### 5.10 鸿蒙常见 Bug 🐛

**评估：** ✅ 优秀 / 🟡 良好 / 🟠 合格 / 🔴 需改进

**发现的问题：**
- 无重大问题

---

## 六、问题汇总

### 🔴 阻塞性问题（必须修复）
1. [问题描述]

### 🟡 重要问题（应该修复）
1. [问题描述]

### 🟢 次要问题（建议改进）
1. [改进建议]

---

## 七、总体评价

综合评分：⭐⭐⭐⭐☆ (4.5/5)

---

## 八、上线建议

### 🚨 安全红线检查
- [✅] 无安全红线问题
- [❌] 存在安全红线，必须修复

### ✅ 建议上线 / ⚠️ 有条件上线 / 🛑 不建议上线

**下一步：** [具体行动建议]
```

---

## 参考文档

### 鸿蒙专项规范
- [arkts-language.md](reference/arkts-language.md) — ArkTS 语言合规审查
- [state-mgmt-v2.md](reference/state-mgmt-v2.md) — V2 状态管理审查
- [router-navigation.md](reference/router-navigation.md) — 路由与 Navigation 审查
- [ui-arkui.md](reference/ui-arkui.md) — ArkUI 渲染与组件审查
- [async-taskpool.md](reference/async-taskpool.md) — 异步与 TaskPool 审查
- [har-hsp-module.md](reference/har-hsp-module.md) — HAR/HSP 模块边界审查
- [security.md](reference/security.md) — 鸿蒙安全审查
- [performance.md](reference/performance.md) — 性能审查
- [common-bugs.md](reference/common-bugs.md) — 鸿蒙常见 Bug 清单
- [coding-style.md](reference/coding-style.md) — 编码规范
- [testing.md](reference/testing.md) — 测试审查

### 通用指南
- [architecture.md](reference/architecture.md) — 架构审查指南

---

## 使用示例

### 完整审查

```
请审查这个 PR，需求文档如下：
[需求内容]

代码变更：
[git diff 或文件列表]
```

### 快速审查

```
快速审查这个功能实现
需求：[简要需求]
代码：[文件路径]
```

### 专项审查

```
请对 File.ets 做 V2 状态管理专项审查
```

```
请检查 entry 模块是否有硬编码密钥
```

---

## 注意事项

1. **V1→V2 渐进迁移期** — 新增代码必须使用 V2（@ComponentV2 / @Local / @Param / @Event），存量 V1 代码（@Component / @State / @Link / @Watch）临时允许维护但禁止扩增
2. **自定义路由 `tztZFRouter`** — 项目特有的路由封装，统一通过 `tztZFRouter.callRoute` 跳转，禁止新增 `@ohos.router` 引用
3. **隐私合规守门** — `SDKRegister.setup()` 必须在 `PrivacyAgreementUtil.hasUserAgreedPrivacy` 为 true 后才执行；MMKV / 数据采集 / 推送初始化必须延后到隐私同意之后
4. **单例线程安全** — `tztZFAppObj` / `tztZFNavigationController` 等单例禁止在 TaskPool 内访问，避免 race 条件
5. **多产物签名** — release/debug 凭据不应入仓，应通过 CI 环境变量注入
6. **鸿蒙安全红线** — 硬编码密钥、明文 HTTP、隐私协议未守门直接否决上线
