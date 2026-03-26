---
site_slug: bytedance
schema_version: 2
content_version: 1
verified_at: 2026-03-24
public_safe: true
access_mode: public
method_type: browser_rendered_search_plus_detail_page
maintainer: bundled
example_search_url: https://jobs.bytedance.com/campus/position/list?keywords=Agent&category=6704215956018694411&location=&project=7194661126919358757&type=&job_hot_flag=&current=1&limit=10&functionCategory=&tag=
---

# 字节跳动招聘数据获取方式

## 目标链接

- 页面链接：`https://jobs.bytedance.com/campus/position/list?keywords=Agent&category=6704215956018694411&location=&project=7194661126919358757&type=&job_hot_flag=&current=1&limit=10&functionCategory=&tag=`

## 结论

- 搜索结果页的初始 HTML 不直接暴露完整职位列表和详情链接。
- 浏览器渲染后，搜索结果卡片会出现在 DOM 中，且可直接拿到所有详情页链接。
- 页面背后存在官方接口：
  - `POST /api/v1/search/job/posts`
  - `POST /api/v1/csrf/token`
  - `GET /api/v1/config/job/filters/3`
- 但职位列表接口依赖运行时生成的 `_signature`；在无浏览器上下文的直接复原中，列表接口返回过 `405`。
- 职位详情页 `GET /campus/position/<job_id>/detail` 可直接访问，正文中包含完整 `职位描述` 与 `职位要求`。

## 推荐做法

### 1. 最稳定的数据入口

- 已验证的稳定入口：`浏览器渲染后的搜索结果页 DOM`
- 页面地址模式：

```text
https://jobs.bytedance.com/campus/position/list?keywords=<关键词>&category=<岗位类别>&project=<项目>&current=1&limit=200&functionCategory=&tag=
```

- 推荐参数：
  - `limit=200`
  - 这样可以在一个页面里拿到当前关键词下的全部职位卡片
- DOM 选择器：

```text
a[href*="/campus/position/"][href*="/detail"]
```

- 每个卡片锚点的 `innerText` 已包含：
  - 职位名称
  - 地点/类型/职位 ID
  - 团队介绍摘要
  - 职责摘要

### 2. 列表接口信息

- 观察到的列表接口：

```text
POST https://jobs.bytedance.com/api/v1/search/job/posts?...&_signature=<runtime-generated>
```

- 观察到的请求体示例：

```json
{
  "keyword": "Agent",
  "limit": 10,
  "offset": 0,
  "job_category_id_list": ["6704215956018694411"],
  "tag_id_list": [],
  "location_code_list": [],
  "subject_id_list": ["7194661126919358757"],
  "recruitment_id_list": [],
  "portal_type": 3,
  "job_function_id_list": [],
  "storefront_id_list": [],
  "portal_entrance": 1
}
```

- 相关接口：

```text
POST https://jobs.bytedance.com/api/v1/csrf/token
GET  https://jobs.bytedance.com/api/v1/config/job/filters/3?_signature=<runtime-generated>
```

- 已知情况：
  - `csrf/token` 可以正常返回 token
  - 但列表接口如果没有浏览器运行时生成的有效 `_signature`，直接复原不稳定
  - 因此当前不建议把 `search/job/posts` 作为首选离线抓取入口

### 3. 职位详情获取方式

- 详情页规则：

```text
GET https://jobs.bytedance.com/campus/position/<job_id>/detail
```

- 解析规则：
  - `职位描述` 与 `职位要求` 都在页面正文中
  - 可从页面文本中按下面边界切分：
    - `职位描述` 到 `职位要求` -> `job_duty`
    - `职位要求` 到 `投递相关职位` -> `job_requirement`

### 4. 字段映射

- 详情页 URL 中的 `<job_id>` -> `job_id`
- 详情页正文第一行标题 -> `title`
- 标题后紧随的地点/类型/职位 ID 行 -> `locations`、补充 `raw`
- `职位描述` 段 -> `job_duty`
- `职位要求` 段 -> `job_requirement`
- 详情页完整正文或列表卡片原文 -> `raw`

## 成功请求样例

- 搜索结果页在浏览器中使用 `limit=200` 时，可一次性拿到全部职位卡片。
- 例如：
  - 关键词 `Agent` 时，已验证页面可渲染 `141` 个岗位卡片
  - 每个卡片都带有可直接访问的详情页链接

## 已知问题

- 列表接口依赖浏览器运行时生成的 `_signature`，直接还原不稳定。
- 详情页可直接抓取，但列表页必须经过浏览器渲染后再拿链接更稳。
- 同标题岗位可能存在多个地点变体；做 JD 匹配时建议按 `标题级岗位` 先合并，再保留地点列表。

## 更新规则

- 优先保留当前确认可用的 `浏览器渲染搜索页 + 详情页直取` 方案。
- 如果后续确认 `_signature` 可稳定复原，再直接更新正文。
- 不记录 Cookie、token 或任何个人请求头。
