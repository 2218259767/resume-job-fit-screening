---
site_slug: alibaba
schema_version: 2
content_version: 1
verified_at: 2026-03-24
public_safe: true
access_mode: public
method_type: session_bootstrap_api
maintainer: bundled
example_search_url: https://campus-talent.alibaba.com/campus/position?batchId=100000540002
---

# 阿里巴巴招聘数据获取方式

## 目标链接

- 页面链接：`https://campus-talent.alibaba.com/campus/position?batchId=100000540002`

## 结论

- 页面本身是前端壳页，HTML 不直接包含职位正文。
- 岗位列表和详情都来自同域官方 JSON 接口。
- 需要先访问页面拿到 `SESSION`、`XSRF-TOKEN` Cookie，并从 HTML 中解析 `window.__sysconfig.__token__`。
- 后续 POST 请求必须带上同一会话 Cookie，并在 query 中附带 `_csrf=<__token__>`，否则会返回 `403 Forbidden`。

## 推荐做法

### 1. 最稳定的数据入口

- 接口地址：`https://campus-talent.alibaba.com/position/search`
- 请求方法：`POST`
- 必要请求头：
  - `Content-Type: application/json`
  - `Referer: https://campus-talent.alibaba.com/campus/position?batchId=100000540002`
  - `Origin: https://campus-talent.alibaba.com`
- 必要前置步骤：
  1. `GET /campus/position?batchId=100000540002`
  2. 保留响应里的 `SESSION`、`XSRF-TOKEN`
  3. 从 HTML 中解析 `window.__sysconfig.__token__`
  4. 在后续接口 URL 上追加 `_csrf=<token>`
- 请求体或关键参数：

```json
{
  "batchId": 100000540002,
  "pageIndex": 1,
  "pageSize": 100,
  "channel": "new_campus_group_official_site",
  "language": "zh"
}
```

### 2. 职位详情获取方式

- 详情接口：`POST https://campus-talent.alibaba.com/position/detail?_csrf=<token>`
- 请求体：

```json
{
  "id": 199903480006,
  "channel": "new_campus_group_official_site",
  "language": "zh"
}
```

- 详情页可打开路径：`https://campus-talent.alibaba.com/campus/position/<job_id>`
- 实测列表接口已经返回 `description` 和 `requirement`；详情接口主要用于单岗位复核。

### 3. 其他辅助接口

- 检索条件：`POST /searchCondition/list?_csrf=<token>`

```json
{
  "batchId": 100000540002,
  "channel": "new_campus_group_official_site",
  "language": "zh"
}
```

- 批次列表：`POST /searchCondition/listBatch?_csrf=<token>`，请求体可为 `{}`

### 4. 字段映射

- `id` -> `job_id`
- `name` -> `title`
- `https://campus-talent.alibaba.com/campus/position/<id>` -> `detail_url`
- `circleNames` -> `department`
- `workLocations` -> `locations`
- `description` -> `job_duty`
- `requirement` -> `job_requirement`
- `campus-talent.alibaba.com` -> `source_site`
- 抓取日期 -> `captured_at`
- 原始对象 -> `raw`

## 成功请求样例

- 可复制的最小请求：

```bash
jar=$(mktemp)
html=$(mktemp)

curl -s -c "$jar" -b "$jar" \
  'https://campus-talent.alibaba.com/campus/position?batchId=100000540002' \
  -o "$html"

token=$(perl -ne 'print $1 if /__token__:\s*"([^"]+)"/' "$html")

curl -s -c "$jar" -b "$jar" \
  -X POST "https://campus-talent.alibaba.com/position/search?_csrf=$token" \
  -H 'Content-Type: application/json' \
  -H 'Referer: https://campus-talent.alibaba.com/campus/position?batchId=100000540002' \
  -H 'Origin: https://campus-talent.alibaba.com' \
  --data '{"batchId":100000540002,"pageIndex":1,"pageSize":100,"channel":"new_campus_group_official_site","language":"zh"}'
```

- 成功返回时的关键字段：
  - `content.datas`
  - `content.totalCount`
  - `datas[].id`
  - `datas[].name`
  - `datas[].description`
  - `datas[].requirement`
  - `datas[].circleNames`
  - `datas[].workLocations`

## 已知问题

- 直接请求接口而不先拿 Cookie 与 `_csrf`，会返回 `403 Forbidden`。
- `pageSize=100` 可用，但总数超过 100 时仍需翻页。
- 某些通用岗位的 `circleNames` 会同时返回多个业务集团，表示该 JD 被多个业务集团共用，不代表同一个团队。

## 更新规则

- 只保留当前确认可用的方法。
- 如果页面批次切换，只替换 `batchId` 与 `Referer`，其余流程保持不变。
- 不记录任何个人 Cookie、token、调试日志或失败探索。
