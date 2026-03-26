---
site_slug: kuaishou
schema_version: 2
content_version: 1
verified_at: 2026-03-24
public_safe: true
access_mode: public
method_type: official_json_api
maintainer: bundled
example_search_url: https://campus.kuaishou.cn/recruit/campus/e/#/campus/jobs?name=%E5%A4%A7%E6%A8%A1%E5%9E%8B&pageNum=1&positionCategoryCodes=algorithm,J1001,J1002,J1003,J1004,J1005,J1006,J1007,J1010,J1011,J1012,J1013,engeering,J1014,J1015,J1016,J1017,J1018,J1019,J1020&positionNatureCode=intern
---

# 快手招聘数据获取方式

## 目标链接

- 页面链接：`https://campus.kuaishou.cn/recruit/campus/e/#/campus/jobs?name=%E5%A4%A7%E6%A8%A1%E5%9E%8B&pageNum=1&positionCategoryCodes=algorithm,J1001,J1002,J1003,J1004,J1005,J1006,J1007,J1010,J1011,J1012,J1013,engeering,J1014,J1015,J1016,J1017,J1018,J1019,J1020&positionNatureCode=intern`

## 结论

- 页面是前端动态渲染，初始 HTML 不包含完整职位列表或详情正文。
- 最稳定的数据入口是官方开放接口，不需要 Cookie、token 或个人请求头。
- 列表接口是 `POST /recruit/campus/e/api/v1/open/positions/simple`。
- 详情接口是 `GET /recruit/campus/e/api/v1/open/positions/find?id=<position_id>`。

## 推荐做法

### 1. 最稳定的数据入口

- 列表接口：`https://campus.kuaishou.cn/recruit/campus/e/api/v1/open/positions/simple`
- 请求方法：`POST`
- 必要请求头：

```http
Content-Type: application/json
```

- 最小可工作请求体：

```json
{
  "pageNum": 1,
  "pageSize": 500,
  "positionNatureCode": "intern"
}
```

- 常用可选字段：
  - `name`
  - `positionLabel`
  - `positionCategoryCodes`
  - `workLocationCodes`
  - `recruitSubProjectCodes`

- 前端 bundle 中的默认子项目常量为：

```json
[
  "20261749721165",
  "20271772783534"
]
```

### 2. 职位详情获取方式

- 详情接口：`GET https://campus.kuaishou.cn/recruit/campus/e/api/v1/open/positions/find?id=<position_id>`
- 可打开的职位详情页规则：

```text
https://campus.kuaishou.cn/recruit/campus/e/#/campus/job-info/<position_id>
```

### 3. 字段映射

- `id` -> `job_id`
- `name` -> `title`
- `https://campus.kuaishou.cn/recruit/campus/e/#/campus/job-info/<id>` -> `detail_url`
- `departmentName` -> `department`
- `workLocationDicts[].name` -> `locations`
- `description` -> `job_duty`
- `positionDemand` -> `job_requirement`
- 完整返回体 -> `raw`

## 成功请求样例

- 全量留用实习岗位列表：

```bash
curl 'https://campus.kuaishou.cn/recruit/campus/e/api/v1/open/positions/simple' \
  -H 'Content-Type: application/json' \
  --data '{"pageNum":1,"pageSize":500,"positionNatureCode":"intern"}'
```

- 单个职位详情：

```bash
curl 'https://campus.kuaishou.cn/recruit/campus/e/api/v1/open/positions/find?id=11339'
```

- 成功返回时的关键字段：
  - `code = 0`
  - `result.total`
  - `result.list[].id`
  - `result.list[].name`
  - `result.list[].description`
  - `result.list[].positionDemand`

## 已知问题

- 搜索页本身只适合承载筛选条件，不适合直接抓正文。
- `pageSize=500` 在 `2026-03-23` 可一次拿全 `intern` 列表，但总量变化后仍建议按 `result.pages` 做分页兜底。
- 部分字段如 `departmentName` 可能为 `null`，需要接受空值。
- 职位总数会随发布时间实时变化，报告里应写抓取日期。

## 更新规则

- 只保留当前确认可用的方法。
- 如果接口路径、分页或字段发生变化，直接更新正文。
- 不记录 Cookie、token、个人 Header 或调试死路。
