# 鸿蒙代码审查技能（融e通专项版）

<p>
  <strong>适用于 Claude Code 的鸿蒙代码审查技能（融e通专项版）</strong>
</p>

---

## 简介

这是为东北证券融e通鸿蒙项目定制的代码审查技能，基于需求文档对 ArkTS 代码进行全面审查，整合 `/Users/ada/.claude/rules/arkts/` 和 `/Users/ada/.claude/rules/typescript/` 的全部规则条目，并结合项目实际技术栈（V1→V2 状态管理迁移、自定义路由、MMKV、CRH SDK）。

**特点：**
- 基于需求文档审查，确保功能完整实现
- 鸿蒙专项审查（V2 状态管理 / 路由 / ArkUI / TaskPool / HUKS）
- ArkTS 语言合规内置（编译期强约束）
- 项目特有约定（tztZF* 前缀、自定义路由、隐私合规守门）
- 结构化审查报告，清晰易懂
- 支持 Claude Code Skill 自动加载

---

## 快速开始

### 安装技能

技能已安装到用户级目录：

```bash
~/.claude/skills/harmonyos-code-review-skill-dbzq/
```

无需额外安装，Claude Code 启动时自动发现。

### 触发技能

**方式 1：手动调用**

```
/harmonyos-code-review
```

**方式 2：关键词触发**（在对话中提到以下任一关键词即可）

- 代码审查
- code review
- 审查 PR / 审查 commit
- review this
- 鸿蒙审查 / ArkTS 审查

**使用示例：**

```
请审查这个 PR，需求文档如下：
[需求内容]

代码变更：
[git diff 输出 / 文件路径列表 / PR 链接]
```

---

## 项目结构

```
harmonyos-code-review-skill-dbzq/
├── SKILL.md                            # 主技能文件（流程+检查项+报告模板）
├── README.md                           # 使用说明（本文件）
└── reference/                          # 11+1 份专项审查规范
    ├── arkts-language.md               # ArkTS 语言合规
    ├── state-mgmt-v2.md                # V2 状态管理
    ├── router-navigation.md            # 路由与 Navigation
    ├── ui-arkui.md                     # ArkUI 渲染与组件
    ├── async-taskpool.md               # 异步与 TaskPool
    ├── har-hsp-module.md               # HAR/HSP 模块边界
    ├── security.md                     # 鸿蒙安全审查
    ├── performance.md                  # 性能审查
    ├── architecture.md                 # 架构审查指南
    ├── common-bugs.md                  # 鸿蒙常见 Bug 清单
    ├── coding-style.md                 # 编码规范
    └── testing.md                      # 测试审查
```

---

## 技术栈

| 维度 | 实际配置 |
|------|---------|
| 主语言 | ArkTS（`.ets` 3360+） + 少量 TS（hvigor 脚本） |
| 状态管理 | V1 57 处 vs V2 112 处（V1→V2 渐进迁移中） |
| 路由方案 | 项目自定义 `tztZFRouter.callRoute`（非标准 `@ohos.router`） |
| 本地存储 | 腾讯 MMKV（取代 Preferences） |
| 网络层 | `@kit.RemoteCommunicationKit`（rcp）+ 拦截器 |
| 富文本 | `@ohasasugar/hp-richtext` |
| 启动框架 | `StartupConfigEntry` + `TaskPool` |
| 第三方 SDK | CRH（视频）/ BugLy / JGP Push / 微信 / QQ |
| 构建系统 | hvigor 5.0.0 |
| 鸿蒙 API | compatibleSdk 12 / target 22（API 5.0.0 ~ 6.0.2） |
| 多产物 | default / release / debug / abt / uat / sim / dev（共 11 个） |
| 模块划分 | entry（HAP）+ 20 个 HAR/HSP |

---

## 审查维度

| 维度 | 覆盖内容 |
|------|---------|
| ArkTS 语言合规 | 60+ 条编译期强约束（any/解构/for-in/function 表达式 等） |
| V2 状态管理 | 禁 V1 装饰器、@ComponentV2 规范、@Param 单向只读 |
| 路由 Navigation | 禁 @ohos.router、tztZFRouter、NavPathStack、deepLink 白名单 |
| ArkUI 渲染 | 动画属性红线、LazyForEach、renderGroup、$r() 资源引用 |
| 异步 TaskPool | UI 线程、TaskPool 禁单例、Promise 错误处理 |
| HAR/HSP 模块 | HSP 资源边界、HAR @Component 不可跨模块、ohpm 锁定 |
| 鸿蒙安全 | HUKS 加密、HTTPS 强制、权限运行时申请、日志脱敏 |
| 性能 | 动画 / 列表 / image 缓存 / 富文本复用 |
| 架构 | SOLID、MVVM 分层、模块边界、路由职责 |
| 测试 | 单元 + UI 测试、覆盖率 80%、边界场景 |

---

## 安全红线

以下问题直接**阻塞上线**：

1. 源码硬编码密钥 / token / 密码
2. 使用明文 HTTP（非 HTTPS）
3. module.json5 权限声明与代码不一致
4. 敏感数据未走 HUKS 加密
5. 隐私协议未同意时调用 `SDKRegister.setup()`

---

## 注意事项

1. **V1→V2 渐进迁移期**：新增代码必须 V2，存量 V1 临时允许维护但禁止扩增
2. **自定义路由 `tztZFRouter`**：项目特有，统一调用，禁止新增 `@ohos.router`
3. **隐私合规守门**：`PrivacyAgreementUtil.hasUserAgreedPrivacy` 守门所有 SDK 初始化
4. **单例线程安全**：`tztZFAppObj` / `tztZFNavigationController` 等单例禁止在 TaskPool 内访问
5. **多产物签名**：release/debug 凭据不应入仓，应通过 CI 环境变量注入
