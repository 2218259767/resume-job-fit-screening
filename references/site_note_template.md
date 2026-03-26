# 招聘站数据接入记录模板

只记录最终可复用的方法，不记录探索过程。

```markdown
---
site_slug: meituan
schema_version: 2
content_version: 1
verified_at: 2026-03-24
public_safe: true
access_mode: public
method_type: official_json_api
maintainer: bundled
example_search_url: https://example.com/jobs?q=llm
---

# <站点名>招聘数据获取方式

## 目标链接

- 页面链接：`<搜索结果页 URL>`

## 结论

- 页面是否可直接从 HTML 拿到职位正文
- 是否为前端动态渲染
- 真实职位数据来自哪里

## 推荐做法

### 1. 最稳定的数据入口

- 接口地址：
- 请求方法：
- 必要请求头：
- 请求体或关键参数：

```json
{}
```

### 2. 职位详情获取方式

- 详情接口或详情页规则：

### 3. 字段映射

- 原始字段 -> 统一 schema 字段

## 成功请求样例

- 可复制的最小请求
- 成功返回时的关键字段

## 已知问题

- 分页限制
- 反爬限制
- 需要额外修复的参数

## 更新规则

- 只保留当前确认可用的方法
- 修复后直接更新正文
- 不保留 dead ends、调试日志、Cookie、token 或个人信息
```

额外要求：

- `site_slug` 要与文件名一致。
- `verified_at` 必须使用 `YYYY-MM-DD`。
- 只有公开可复现的方法才能写成 `public_safe: true`。
- 如果方法依赖登录态或私人凭证，只能保留在本地 note，不进入公共共享流程。
