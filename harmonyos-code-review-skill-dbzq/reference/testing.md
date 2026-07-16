# 测试 审查

## 基本原则

1. **覆盖率 ≥ 80%** —— 核心模块（网络/路由/状态）必须 90%+
2. **TDD 优先** —— 先写 RED 测试，再写 GREEN 实现
3. **单元 + 集成 + UI 三层** —— 缺一不可
4. **AAA 模式** —— Arrange / Act / Assert 清晰
5. **边界场景必测** —— 权限拒绝 / 网络错误 / 空数据 / 极值
6. **测试文件就近** —— `src/test/` 目录与源码并列

---

## 一、测试类型

### 1.1 单元测试

```typescript
// UserService.test.ets
import { describe, it, expect } from '@ohos/hypium'
import { UserService } from '../main/ets/service/UserService'

describe('UserService', () => {
  it('should_load_user_by_id', 0, async () => {
    // Arrange
    const service = new UserService()

    // Act
    const user = await service.loadUser('user_001')

    // Assert
    expect(user.id).assertEqual('user_001')
    expect(user.name).assertEqual('Tom')
  })

  it('should_return_null_when_user_not_found', 0, async () => {
    const service = new UserService()
    const user = await service.loadUser('not_exist')
    expect(user).assertNull()
  })
})
```

### 1.2 集成测试

```typescript
// NetworkService.test.ets
describe('NetworkService', () => {
  it('should_send_request_with_token', 0, async () => {
    const network = new NetworkService()
    const resp = await network.get('/user/info', { token: 'xxx' })
    expect(resp.status).assertEqual(200)
    expect(resp.data).assertNotNull()
  })

  it('should_retry_on_500_error', 0, async () => {
    // 测试重试逻辑
  })
})
```

### 1.3 UI 测试

```typescript
// UserProfileView.test.ets
import { describe, it, expect } from '@ohos/hypium'
import { Driver, ON } from '@ohos.UiTest'

describe('UserProfileView', () => {
  it('should_display_user_name_on_appear', 0, async () => {
    const driver = Driver.create()
    await driver.delay(1000)

    const nameText = await driver.findComponent(ON.text('Tom'))
    expect(nameText).assertNotNull()
  })

  it('should_navigate_to_edit_on_button_click', 0, async () => {
    const driver = Driver.create()
    const editBtn = await driver.findComponent(ON.id('editBtn'))
    await editBtn.click()
    await driver.delay(500)

    const title = await driver.findComponent(ON.text('编辑用户'))
    expect(title).assertNotNull()
  })
})
```

---

## 二、覆盖率要求

### 2.1 模块分级

| 模块 | 覆盖率要求 |
|------|-----------|
| RetUtils（网络 / 加密） | ≥ 90% |
| tztZFUI（路由 / 通用组件） | ≥ 90% |
| tztZFResource（路由路径 / 常量） | ≥ 85% |
| 业务模块（tztZFJY / tztZFHQ） | ≥ 80% |
| entry 入口 | ≥ 70% |
| Widget / UI 装饰组件 | ≥ 50% |

### 2.2 覆盖率检测

```bash
# DevEco Studio 自带覆盖率
# 或通过 hvigor test
hvigor test --coverage

# 检查覆盖率输出
cat entry/build/coverage/report.json
```

### 2.3 覆盖率不达标处理

```
覆盖率 < 80% → 阻塞合并
覆盖率 80-90% → 警告，建议补充
覆盖率 ≥ 90% → 通过
```

---

## 三、文件组织

### 3.1 测试文件命名

```
// ✅ 与被测文件同名 + .test
src/
  main/ets/
    service/
      UserService.ets
  test/
    service/
      UserService.test.ets

// ✅ 或 __tests__ 目录
src/
  main/ets/
    service/
      UserService.ets
      __tests__/
        UserService.test.ts
```

### 3.2 测试目录结构

```
entry/
  src/
    main/ets/
      pages/
        HomePage.ets
    test/
      LocalUnit.test.ets            # 本地单元测试
      ListLocalUnit.test.ets        # 测试入口列表
    ohosTest/
      ListNetwork.test.ets          # 设备端集成测试
      ListBackground.test.ets       # 后台任务测试
```

---

## 四、TDD 流程

### 4.1 RED → GREEN → IMPROVE

```typescript
// Step 1: RED（先写失败的测试）
describe('PriceCalculator', () => {
  it('should_apply_vip_discount', 0, () => {
    const calc = new PriceCalculator()
    const result = calc.calculate(100, 'vip')
    expect(result).assertEqual(80)  // 失败：方法不存在
  })
})

// Step 2: GREEN（写最小实现）
class PriceCalculator {
  calculate(amount: number, type: string): number {
    if (type === 'vip') return amount * 0.8
    return amount
  }
}

// Step 3: IMPROVE（重构 + 扩展测试）
describe('PriceCalculator', () => {
  it('should_apply_vip_discount', 0, /* ... */)
  it('should_apply_discount_90', 0, /* ... */)
  it('should_handle_unknown_type', 0, /* ... */)
})
```

### 4.2 tdd-guide agent

```
/tdd-guide  // 强制 TDD 流程
```

---

## 五、AAA 模式

### 5.1 标准结构

```typescript
it('should_calculate_total_price', 0, () => {
  // Arrange（准备）
  const items = [
    new Item('a', 10),
    new Item('b', 20),
    new Item('c', 30)
  ]
  const cart = new Cart(items)

  // Act（执行）
  const total = cart.total

  // Assert（断言）
  expect(total).assertEqual(60)
})
```

### 5.2 异步 AAA

```typescript
it('should_load_user_async', 0, async () => {
  // Arrange
  const service = new UserService()

  // Act
  const user = await service.loadUser('001')

  // Assert
  expect(user).assertNotNull()
  expect(user.id).assertEqual('001')
})
```

---

## 六、测试命名

### 6.1 描述性命名

```typescript
// ✅ 描述行为
it('should_return_empty_array_when_no_markets_match_query', 0, () => {})
it('should_throw_error_when_api_key_is_missing', 0, () => {})
it('should_fallback_to_substring_search_when_redis_unavailable', 0, () => {})

// ❌ 反例：编号 / 无意义名
it('test1', 0, () => {})
it('should_work', 0, () => {})
```

### 6.2 中文测试名

```typescript
// ✅ 中文（项目允许）
it('加载用户_已存在_返回用户信息', 0, async () => {})
it('加载用户_不存在_返回null', 0, async () => {})

// ✅ 英文 snake_case
it('should_load_user_when_exists', 0, () => {})
it('should_return_null_when_not_exists', 0, () => {})
```

---

## 七、Mock 策略

### 7.1 Mock 网络

```typescript
// Mock 整个网络层
import { NetworkService } from 'RetUtils'

class MockNetworkService implements NetworkService {
  async get(path: string): Promise<any> {
    if (path === '/user/info') {
      return { id: '001', name: 'Tom' }
    }
    if (path === '/user/not_exist') {
      return null
    }
    throw new Error('Network error')
  }
}

// 在测试中使用 Mock
it('should_handle_user_loading', 0, async () => {
  const mockNetwork = new MockNetworkService()
  const service = new UserService(mockNetwork)

  const user = await service.loadUser('001')
  expect(user.name).assertEqual('Tom')
})
```

### 7.2 Mock MMKV

```typescript
// 用内存 Map 模拟 MMKV
class MockMMKV {
  private store: Map<string, string> = new Map()

  setString(key: string, value: string): void {
    this.store.set(key, value)
  }
  getString(key: string): string {
    return this.store.get(key) ?? ''
  }
}
```

### 7.3 Mock 时间

```typescript
// Mock setTimeout / Date
it('should_expire_after_timeout', 0, async () => {
  const now = Date.now()
  // Mock Date.now 返回 +1000ms 之后
  jest.spyOn(Date, 'now').mockReturnValue(now + 1000)
  
  const isExpired = tokenService.isExpired(token)
  expect(isExpired).assertTrue()
})
```

---

## 八、边界场景

### 8.1 必测边界

```typescript
describe('StringUtil', () => {
  it('should_handle_empty_string', 0, () => {
    expect(StringUtil.trim('')).assertEqual('')
  })
  
  it('should_handle_whitespace_only', 0, () => {
    expect(StringUtil.trim('   ')).assertEqual('')
  })
  
  it('should_handle_null', 0, () => {
    expect(StringUtil.trim(null as any)).assertEqual('')
  })
  
  it('should_handle_very_long_string', 0, () => {
    const long = 'a'.repeat(10000)
    expect(StringUtil.trim(long).length).assertEqual(10000)
  })
  
  it('should_handle_unicode', 0, () => {
    expect(StringUtil.trim('  中文  ')).assertEqual('中文')
  })
})
```

### 8.2 异步错误场景

```typescript
describe('NetworkService', () => {
  it('should_throw_on_network_error', 0, async () => {
    const service = new NetworkService()
    try {
      await service.get('/offline')
      expect().assertFail()  // 不应到达
    } catch (e) {
      expect(String(e)).assertContain('network')
    }
  })
  
  it('should_retry_on_timeout', 0, async () => {
    const service = new NetworkService({ retries: 3 })
    // 模拟前两次超时，第三次成功
    let attempts = 0
    service.hook = () => { attempts++; return attempts >= 3 }
    
    const resp = await service.get('/slow')
    expect(attempts).assertEqual(3)
  })
  
  it('should_timeout_after_configured_duration', 0, async () => {
    const service = new NetworkService({ timeout: 100 })
    try {
      await service.get('/hang')
      expect().assertFail()
    } catch (e) {
      expect(String(e)).assertContain('timeout')
    }
  })
})
```

### 8.3 权限场景

```typescript
describe('LocationService', () => {
  it('should_return_error_when_permission_denied', 0, async () => {
    const service = new LocationService({ hasPermission: false })
    try {
      await service.getCurrentLocation()
      expect().assertFail()
    } catch (e) {
      expect(String(e)).assertContain('permission denied')
    }
  })
  
  it('should_return_location_when_granted', 0, async () => {
    const service = new LocationService({ hasPermission: true })
    const loc = await service.getCurrentLocation()
    expect(loc).assertNotNull()
  })
})
```

---

## 九、UI 测试

### 9.1 @ohos.UiTest

```typescript
import { describe, it, expect } from '@ohos/hypium'
import { Driver, ON } from '@ohos.UiTest'

describe('HomePage', () => {
  it('should_show_welcome_text', 0, async () => {
    const driver = Driver.create()
    await driver.delay(1000)
    
    const welcome = await driver.findComponent(ON.text('欢迎使用'))
    expect(welcome).assertNotNull()
  })
  
  it('should_navigate_to_detail_on_click', 0, async () => {
    const driver = Driver.create()
    const item = await driver.findComponent(ON.id('listItem_0'))
    await item.click()
    await driver.delay(500)
    
    // 断言导航成功
    const title = await driver.findComponent(ON.id('detailTitle'))
    expect(title).assertNotNull()
  })
  
  it('should_show_loading_then_data', 0, async () => {
    const driver = Driver.create()
    await driver.delay(100)
    
    const loading = await driver.findComponent(ON.id('loadingView'))
    expect(loading).assertNotNull()  // 初始有 loading
    
    await driver.delay(2000)  // 等待加载完成
    
    const loadingGone = await driver.findComponent(ON.id('loadingView'))
    expect(loadingGone).assertNull()  // loading 消失
  })
})
```

### 9.2 关键页面必测

- 启动页 → 首屏跳转
- 登录页 → 成功 / 失败 / 取消
- 主页 Tab 切换
- 列表 → 下拉刷新 / 上拉加载
- 详情页 → 进入 / 返回
- 表单 → 提交成功 / 失败 / 校验

---

## 十、断言

### 10.1 常用断言

```typescript
// 基础
expect(value).assertEqual(expected)
expect(value).assertNotEqual(expected)
expect(value).assertStrictlyEqual(expected)  // ===
expect(value).assertNull()
expect(value).assertNotNull()
expect(value).assertUndefined()
expect(value).assertDefined()
expect(value).assertTrue()
expect(value).assertFalse()

// 数值
expect(value).assertGreaterThan(target)
expect(value).assertLessThan(target)
expect(value).assertCloseTo(target, precision)

// 字符串
expect(str).assertContain(substr)
expect(str).assertMatch(regex)

// 数组
expect(arr).assertContain(item)
expect(arr).assertLength(length)
```

### 10.2 失败用例

```typescript
// ❌ 反例：无断言
it('should_load_user', 0, async () => {
  await service.loadUser('001')
  // 缺断言，测试无意义
})

// ✅ 正确：每个 it 都有断言
it('should_load_user', 0, async () => {
  const user = await service.loadUser('001')
  expect(user).assertNotNull()
  expect(user.id).assertEqual('001')
})
```

---

## 十一、运行测试

### 11.1 命令

```bash
# DevEco Studio 中
# 右键 test/LocalUnit.test.ets → Run

# 命令行
hvigor test

# 指定模块
hvigor --module entry test

# 监听模式
hvigor test --watch
```

### 11.2 测试报告

```
test-results/
  LocalUnit.test.ets-result/
    result.html    # HTML 报告
    coverage/      # 覆盖率报告
```

---

## 十二、反模式

### 12.1 测实现而非行为

```typescript
// ❌ 反例：测私有字段
it('should_have_internal_counter', 0, () => {
  const service = new Service()
  expect((service as any)._counter).assertEqual(0)  // ❌
})

// ✅ 正确：测公开行为
it('should_return_count_zero_initially', 0, () => {
  const service = new Service()
  expect(service.getCount()).assertEqual(0)
})
```

### 12.2 测试间相互依赖

```typescript
// ❌ 反例：测试 A 改全局，测试 B 依赖
let sharedData: any

it('test_a', 0, () => {
  sharedData = { count: 1 }
})

it('test_b', 0, () => {
  expect(sharedData.count).assertEqual(1)  // 依赖 test_a
})

// ✅ 正确：每个测试独立
it('test_b', 0, () => {
  const data = { count: 1 }  // 独立准备
  expect(data.count).assertEqual(1)
})
```

### 12.3 慢测试

```typescript
// ❌ 反例：测试中真实等待 5s
it('should_wait_for_5_seconds', 0, async () => {
  await delay(5000)
  // ...
})

// ✅ 正确：Mock 时间
it('should_complete_after_5_seconds', 0, async () => {
  jest.useFakeTimers()
  // ...
  jest.advanceTimersByTime(5000)
  // ...
})
```

---

## 审查检查清单

### 覆盖率
- [ ] 整体覆盖率 ≥ 80%
- [ ] 核心模块 ≥ 90%
- [ ] 无未覆盖的关键路径

### 文件组织
- [ ] 测试文件命名 `.test.ets`
- [ ] 测试目录 `src/test/` 就近
- [ ] 测试与源码 1:1 对应

### 单元测试
- [ ] 公共函数都有测试
- [ ] Mock 网络 / 存储 / 时间
- [ ] 边界场景（空 / null / 极值 / Unicode）

### 集成测试
- [ ] 关键 API 调用有集成测试
- [ ] 错误码都有覆盖
- [ ] 超时 / 重试逻辑有测试

### UI 测试
- [ ] 关键页面有 @ohos.UiTest
- [ ] 核心交互（点击 / 滑动 / 输入）有覆盖
- [ ] 加载状态 / 错误状态有断言

### 断言
- [ ] 每个 it 都有断言
- [ ] 测行为而非实现
- [ ] 测试命名描述行为
- [ ] 测试相互独立

### TDD
- [ ] 新功能遵循 RED → GREEN → IMPROVE
- [ ] 使用 tdd-guide agent
