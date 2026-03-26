---
site_slug: feishu
schema_version: 2
content_version: 1
verified_at: 2026-03-24
public_safe: true
access_mode: public
method_type: browser_har_signed_api
maintainer: bundled
example_search_url: https://nio.jobs.feishu.cn/intern/?keywords=大模型&category=&location=&project=&type=&job_hot_flag=&current=1&limit=10&functionCategory=&tag=
---

# 飞书招聘站数据获取方式

## 目标链接

- 页面链接：`https://nio.jobs.feishu.cn/intern/?keywords=大模型&category=&location=&project=&type=&job_hot_flag=&current=1&limit=10&functionCategory=&tag=`

## 结论

- 页面不能直接从初始 HTML 拿到职位正文，职位数据由前端动态请求公开 JSON 接口。
- 搜索结果接口和职位详情接口都在同域名下的 `/api/v1/`。
- 搜索结果接口需要 `_signature` 参数；首次请求若没有 `atsx-csrf-token`，通常会先返回 `405`，前端随后调用 CSRF 接口并重试成功。
- 对飞书招聘站，最稳妥的公开采集方式不是硬猜 `_signature` 生成逻辑，而是用无头浏览器打开搜索页或详情页，并从 HAR 中提取前端已经签好的请求与响应。

## 推荐做法

### 1. 最稳定的数据入口

- 接口地址：
  - 搜索：`https://<host>/api/v1/search/job/posts?...&_signature=...`
  - 详情：`https://<host>/api/v1/job/posts/<job_id>?portal_type=<n>&with_recommend=false&_signature=...`
  - CSRF：`POST https://<host>/api/v1/csrf/token`
- 请求方法：
  - 搜索：`POST`
  - 详情：`GET`
  - CSRF：`POST`
- 必要请求头：
  - 搜索重试成功时需要 `content-type: application/json`
  - 搜索重试成功时需要 `x-csrf-token: <atsx-csrf-token>`
  - 浏览器会同时带上 `atsx-csrf-token` Cookie
- 请求体或关键参数：

```json
{
  "keyword": "大模型",
  "limit": 100,
  "offset": 0,
  "job_category_id_list": [],
  "tag_id_list": [],
  "location_code_list": [],
  "subject_id_list": [],
  "recruitment_id_list": [],
  "portal_type": 6,
  "job_function_id_list": [],
  "storefront_id_list": [],
  "portal_entrance": 1
}
```

### 2. 职位详情获取方式

- 先打开详情页：
  - `https://<host>/<site_path>/position/detail/<job_id>`
- 然后从 HAR 中读取前端实际发出的详情接口：
  - `GET /api/v1/job/posts/<job_id>?portal_type=6&with_recommend=false&_signature=...`
- 详情响应里的 `data.job_post_detail` 就是完整 JD 主体。

### 3. 字段映射

- 搜索/详情响应里的 `id` -> `job_id`
- 搜索/详情响应里的 `title` -> `title`
- `https://<host>/<site_path>/position/detail/<id>` -> `detail_url`
- `job_function.name` / `job_category.name` -> `department`
- `city_list[].name` 或 `address_list[].name` -> `locations`
- `description` -> `job_duty`
- `requirement` -> `job_requirement`
- 整个原始职位对象 -> `raw`

## 成功请求样例

- 建议直接让前端自行完成签名与 CSRF 流程，再从 HAR 读取 JSON：

```bash
npx -y playwright@latest screenshot \
  --browser chromium \
  --wait-for-timeout 5000 \
  --save-har feishu.har \
  'https://nio.jobs.feishu.cn/intern/?keywords=大模型&current=1&limit=100' \
  feishu.png
```

- 之后解析 HAR，提取：
  - 成功的 `POST /api/v1/search/job/posts?...&_signature=...`
  - 成功的 `GET /api/v1/job/posts/<job_id>?...&_signature=...`
- 成功返回时的关键字段：
  - 搜索：`data.count`、`data.job_post_list`
  - 详情：`data.job_post_detail`

## 已知问题

- `_signature` 是前端生成的动态参数，不建议手工逆向后硬编码。
- 搜索接口首次请求可能返回 `405`；前端会先 `POST /api/v1/csrf/token`，拿到 `atsx-csrf-token` 后自动重试。
- 同一个站点的 `portal_type` 不是固定常数。对 `nio.jobs.feishu.cn/intern`，2026-03-23 抓到的是 `portal_type=6`。
- 页面路径里有 `/intern`，但 API 仍走根路径 `/api/v1/...`，不是 `/intern/api/v1/...`。

## 更新规则

- 只保留当前确认可用的方法。
- 若后续站点改签名、改 `portal_type`、或改 CSRF 逻辑，直接更新本文。
- 不记录 Cookie 原值、token 原值、dead ends 或调试日志。
