# 鸿蒙安全 审查

## 基本原则

1. **无硬编码密钥** —— API key / token / 密码必须走 BuildProfile 或 HUKS
2. **HTTPS 强制** —— 禁止明文 HTTP
3. **HUKS 加密** —— 敏感数据走 `@kit.UniversalKeystoreKit`
4. **权限运行时申请** —— 敏感权限（相机/位置/通讯录）必须用户授权
5. **日志脱敏** —— `hilog` 用 `%{private}s` 包裹敏感字段
6. **隐私合规守门** —— 所有 SDK 初始化由 `PrivacyAgreementUtil.hasUserAgreedPrivacy` 守门

---

## 🚨 安全红线（一票否决）

| # | 红线 | 检测方式 |
|---|------|---------|
| 1 | 源码硬编码密钥 / token / 密码 | `grep -rE "['\"](sk-\|Bearer\|token\|api_key)\\s*[:=]\\s*['\"]" --include="*.ets"` |
| 2 | 明文 HTTP（`http://`） | `grep -rE "http://" --include="*.ets" \| grep -v "//"` |
| 3 | module.json5 权限与代码不一致 | 人工对照 |
| 4 | 敏感数据未走 HUKS 加密 | 人工对照 |
| 5 | 隐私协议未同意时调用 `SDKRegister.setup()` | 人工对照 |

> 任何一项触发直接标记**阻塞性问题**。

---

## 一、密钥管理

### 1.1 硬编码密钥（红线）

```typescript
// ❌ 错误：硬编码 API key
const API_KEY: string = 'sk-xxxxxxxxxxxxxxxx'

// ❌ 错误：硬编码 token
const TOKEN: string = 'eyJhbGciOiJIUzI1NiJ9.xxx'

// ❌ 错误：URL 中嵌入密钥
const url = `https://api.example.com/data?key=sk-xxxxx`
```

### 1.2 正确做法

```typescript
// ✅ 正确：非敏感配置走 BuildProfile
import { BuildProfile } from 'BuildProfile'
const endpoint = BuildProfile.API_ENDPOINT

// ✅ 正确：敏感数据走 HUKS 加密存储
import { huks } from '@kit.UniversalKeystoreKit'

async function decryptSecret(alias: string, nonce: Uint8Array,
                            aad: Uint8Array, cipherData: Uint8Array): Promise<Uint8Array> {
  const options: huks.HuksOptions = {
    properties: [
      { tag: huks.HuksTag.HUKS_TAG_ALGORITHM, value: huks.HuksKeyAlg.HUKS_ALG_AES },
      { tag: huks.HuksTag.HUKS_TAG_PURPOSE, value: huks.HuksKeyPurpose.HUKS_KEY_PURPOSE_DECRYPT },
      { tag: huks.HuksTag.HUKS_TAG_BLOCK_MODE, value: huks.HuksCipherMode.HUKS_MODE_GCM },
      { tag: huks.HuksTag.HUKS_TAG_PADDING, value: huks.HuksKeyPadding.HUKS_PADDING_NONE },
      { tag: huks.HuksTag.HUKS_TAG_NONCE, value: nonce },
      { tag: huks.HuksTag.HUKS_TAG_ASSOCIATED_DATA, value: aad }
    ],
    inData: cipherData
  }
  const handle = await huks.initSession(alias, options)
  const result = await huks.finishSession(handle.handle, options)
  return result.outData
}
```

### 1.3 多产物签名管理

```json5
// build-profile.json5 - 凭据走环境变量
{
  "app": {
    "signingConfigs": {
      "release": {
        "storePassword": "${env.RELEASE_STORE_PASSWORD}",
        "keyPassword": "${env.RELEASE_KEY_PASSWORD}"
      }
    }
  }
}
```

> release/debug 凭据**不应入仓**，应通过 CI 环境变量注入。

---

## 二、网络安全

### 2.1 HTTPS 强制（红线）

```typescript
// ❌ 错误：明文 HTTP
const url = 'http://api.example.com/data'

// ✅ 正确：HTTPS
const url = 'https://api.example.com/data'

// ✅ 正确：拦截器统一升级
class RequestHeaderEncoder implements Interceptor {
  intercept(context: RequestContext, next: RequestHandler): Promise<Response> {
    const req = context.request
    if (req.url.startsWith('http://')) {
      req.url = req.url.replace('http://', 'https://')
    }
    return next.handle(context)
  }
}
```

### 2.2 证书校验

```typescript
// ✅ 正确：rcp.Session 配置证书
import { rcp } from '@kit.RemoteCommunicationKit'

const session = rcp.createSession({
  tlsOptions: {
    certificatePinning: [
      { publicKeyHash: 'sha256/xxxxx=' }
    ]
  }
})
```

### 2.3 拦截器日志脱敏

```typescript
class ResponseDecoder implements Interceptor {
  intercept(context: RequestContext, next: RequestHandler): Promise<Response> {
    return next.handle(context).then((resp) => {
      // ❌ 错误：打印完整 header
      hilog.info(0x0000, 'Net', 'response header: %{public}s', JSON.stringify(resp.headers))

      // ✅ 正确：脱敏
      const safeHeaders = this.sanitizeHeaders(resp.headers)
      hilog.info(0x0000, 'Net', 'response header: %{public}s', JSON.stringify(safeHeaders))
      return resp
    })
  }

  private sanitizeHeaders(headers: object): object {
    const sensitiveKeys = ['authorization', 'cookie', 'token']
    const safe: Record<string, string> = {}
    Object.keys(headers).forEach((k) => {
      if (sensitiveKeys.includes(k.toLowerCase())) {
        safe[k] = '***'
      } else {
        safe[k] = String(headers[k])
      }
    })
    return safe
  }
}
```

---

## 三、权限管理

### 3.1 module.json5 声明

```json5
{
  "module": {
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET",
        "reason": "$string:internet_permission_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "always"
        }
      },
      {
        "name": "ohos.permission.CAMERA",
        "reason": "$string:camera_permission_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "inuse"
        }
      }
    ]
  }
}
```

### 3.2 运行时申请

```typescript
import { abilityAccessCtrl, bundleManager, Permissions } from '@kit.AbilityKit'

async function checkAndRequestPermission(permission: Permissions): Promise<boolean> {
  const atManager = abilityAccessCtrl.createAtManager()
  const bundleInfo = await bundleManager.getBundleInfoForSelf(
    bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_APPLICATION
  )
  const tokenId = bundleInfo.appInfo.accessTokenId
  const grantStatus = await atManager.checkAccessToken(tokenId, permission)

  if (grantStatus === abilityAccessCtrl.GrantStatus.PERMISSION_GRANTED) {
    return true
  }

  const result = await atManager.requestPermissionsFromUser(getContext(), [permission])
  return result.authResults[0] === abilityAccessCtrl.GrantStatus.PERMISSION_GRANTED
}
```

### 3.3 权限使用前检查

```typescript
// ✅ 正确
async function takePhoto(): Promise<void> {
  const granted = await checkAndRequestPermission('ohos.permission.CAMERA')
  if (!granted) {
    promptAction.showToast({ message: $r('app.string.camera_denied') })
    return
  }
  // 拍照逻辑
}

// ❌ 错误：未检查直接调用
async function takePhoto(): Promise<void> {
  cameraApi.takePicture()  // 用户拒绝时崩溃
}
```

---

## 四、隐私合规守门（红线）

### 4.1 SDKRegister.setup() 守门

```typescript
// entry/src/main/ets/entryability/EntryAbility.ets
onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
  // ✅ 正确：先检查隐私同意
  if (PrivacyAgreementUtil.hasUserAgreedPrivacy()) {
    SDKRegister.setup()
  }
}

// ❌ 错误：无条件初始化（违规）
onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
  SDKRegister.setup()  // 用户未同意隐私时已采集数据
}
```

### 4.2 MMKV / 推送 / 数据采集 守门

```typescript
// SDKRegister.ets
class SDKRegister {
  static setup(): void {
    // MMKV
    MMKV.initialize(this.context)

    // BugLy
    BugLy.init(this.context)

    // 推送
    PushService.register()

    // 数据采集
    DataCollection.start()
  }
}

// 调用方必须守门
if (PrivacyAgreementUtil.hasUserAgreedPrivacy()) {
  SDKRegister.setup()
}
```

---

## 五、日志脱敏

### 5.1 %{public}s vs %{private}s

```typescript
// ❌ 错误：用 %{public}s 输出敏感信息
hilog.info(0x0000, 'User', 'login: %{public}s', JSON.stringify(userInfo))

// ✅ 正确：敏感字段用 %{private}s
hilog.info(0x0000, 'User', 'login: name=%{public}s id=%{private}s', userInfo.name, userInfo.idCard)
```

**规则：**
- `%{public}s` —— 公开信息，发布版本仍可见
- `%{private}s` —— 私有信息，发布版本自动脱敏为 `***`

### 5.2 console.log 禁用

```typescript
// ❌ 错误
console.log('user info:', userInfo)
console.log('token:', token)

// ✅ 正确
hilog.info(0x0000, 'Tag', 'user id: %{private}s', userInfo.id)
```

---

## 六、输入校验

### 6.1 deepLink 参数校验

参见 [router-navigation.md](router-navigation.md) 第四章。

### 6.2 用户输入校验

```typescript
// ✅ 正确：白名单校验
function parseStockCode(input: string): string | null {
  const cleaned = input.trim().toUpperCase()
  if (!/^[0-9]{6}$/.test(cleaned)) {
    return null
  }
  return cleaned
}

// ❌ 错误：直接信任输入
function parseStockCode(input: string): string {
  return input  // SQL/命令注入风险
}
```

### 6.3 富文本注入防护

```typescript
// ❌ 错误：直接渲染用户内容
hpRichText(source: userInputHtml)

// ✅ 正确：过滤危险标签
function sanitizeHtml(input: string): string {
  return input.replace(/<script[^>]*>.*?<\/script>/gi, '')
              .replace(/on\w+="[^"]*"/g, '')
              .replace(/javascript:/gi, '')
}
```

---

## 七、本地存储安全

### 7.1 MMKV 敏感数据加密

```typescript
// ✅ 正确：敏感字段用加密 ID
const mmkv = MMKV.defaultMMKV({ cryptKey: 'aes-key-from-huks' })
mmkv.encodeString('user_token', token)

// ❌ 错误：明文存储 token
const mmkv = MMKV.defaultMMKV()
mmkv.encodeString('user_token', token)
```

### 7.2 内存清理

```typescript
// ✅ 正确：使用后清理
function handleLogin(): void {
  const password = inputPassword.text
  // ... 业务逻辑
  inputPassword.text = ''  // 清理 UI
  // 局部变量由 GC 自动清理，长生命周期变量需显式置空
}
```

---

## 审查检查清单

### 密钥
- [ ] 源码无硬编码密钥 / token / 密码
- [ ] URL 无嵌入密钥
- [ ] 敏感数据走 HUKS
- [ ] 多产物签名凭据走环境变量

### 网络
- [ ] 无明文 HTTP
- [ ] rcp.Session 证书校验
- [ ] 拦截器日志脱敏
- [ ] 网络请求有超时与重试

### 权限
- [ ] module.json5 权限声明完整
- [ ] 敏感权限运行时申请
- [ ] 权限拒绝时有 graceful fallback
- [ ] 权限 reason 字符串有资源文件

### 隐私合规
- [ ] `SDKRegister.setup()` 由 `hasUserAgreedPrivacy` 守门
- [ ] MMKV / 推送 / 数据采集延后到隐私同意后
- [ ] 无条件初始化数据采集

### 日志
- [ ] 敏感字段用 `%{private}s`
- [ ] 无 `console.log` 残留
- [ ] 拦截器日志脱敏

### 输入
- [ ] deepLink 参数白名单校验
- [ ] 用户输入白名单正则校验
- [ ] 富文本 HTML 过滤
