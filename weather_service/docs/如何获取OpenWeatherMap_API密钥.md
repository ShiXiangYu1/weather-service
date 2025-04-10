# 如何获取OpenWeatherMap API密钥

## 简介

OpenWeatherMap是一个流行的气象数据服务提供商，提供当前天气数据、预报、历史数据等多种气象信息。要使用OpenWeatherMap的API服务，您需要注册一个免费账户并获取API密钥。本文档将指导您完成整个过程。

## 注册OpenWeatherMap账户

1. 访问OpenWeatherMap官方网站：[https://openweathermap.org/](https://openweathermap.org/)

2. 点击页面右上角的"Sign In"按钮

3. 在登录页面中，点击"Create an Account"链接

4. 填写注册表单，包括：
   - 用户名
   - 电子邮箱
   - 密码

5. 阅读并接受服务条款和隐私政策

6. 点击"Create Account"按钮完成注册

7. 检查您的电子邮箱，查收验证邮件并点击验证链接激活账户

## 获取API密钥

1. 登录您的OpenWeatherMap账户

2. 导航至API密钥页面
   - 您可以点击右上角的用户图标，然后选择"My API keys"
   - 或者直接访问：[https://home.openweathermap.org/api_keys](https://home.openweathermap.org/api_keys)

3. 在"Create Key"部分，您可以看到默认生成的API密钥，也可以为新密钥命名并点击"Generate"按钮创建新的API密钥

4. 生成的API密钥将显示在"Key"列表中，复制这个密钥

## 密钥激活等待时间

**重要提示**：新创建的API密钥通常需要几个小时（最多可能需要24小时）才能完全激活。在此期间，使用该密钥的API请求可能会收到"401 Unauthorized"错误。

## 配置API密钥到天气查询服务

获取API密钥后，您需要将其配置到天气查询服务中：

1. 打开项目根目录下的`.env`文件

2. 修改API密钥配置，确保格式正确：
   ```
   # 天气API设置 (以OpenWeatherMap为例)
   WEATHER_API_KEY=您的API密钥
   WEATHER_API_BASE_URL=https://api.openweathermap.org/data/2.5
   ```

3. 保存文件

## 验证API密钥是否有效

您可以通过以下命令验证API密钥是否有效：

```bash
curl "https://api.openweathermap.org/data/2.5/weather?q=Beijing&appid=您的API密钥"
```

如果返回正确的天气数据（而不是401错误），则表明API密钥配置正确且已激活。

## API使用限制

OpenWeatherMap提供不同层级的订阅计划，免费计划的主要限制是：

- 每分钟最多60次API调用
- 可访问当前天气数据和5天/3小时预报
- 只能访问近5天的历史数据
- 不支持某些高级功能（如分钟级预报）

如果您的应用需要更高的调用频率或更多功能，可以考虑升级到付费计划。

## 最佳实践

1. **保护您的API密钥**：不要在公开的代码库中暴露您的API密钥

2. **实现缓存机制**：减少不必要的API调用，节省配额（我们的应用已经实现了缓存功能）

3. **错误处理**：确保您的应用能够适当处理API限制和服务中断

4. **遵循API使用条款**：确保您的使用符合OpenWeatherMap的服务条款

## 故障排除

如果您在使用API密钥时遇到问题：

- 确认密钥已正确复制，没有多余的空格
- 检查密钥是否已经激活（等待足够的时间）
- 尝试在API密钥页面重新生成一个新的密钥
- 检查您是否已达到API调用限制

## 相关资源

- [OpenWeatherMap API文档](https://openweathermap.org/api)
- [API使用条款](https://openweathermap.org/terms)
- [常见问题解答](https://openweathermap.org/faq) 