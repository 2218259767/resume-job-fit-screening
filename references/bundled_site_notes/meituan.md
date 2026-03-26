---
site_slug: meituan
schema_version: 2
content_version: 1
verified_at: 2026-03-24
public_safe: true
access_mode: public
method_type: official_json_api
maintainer: bundled
example_search_url: https://zhaopin.meituan.com/web/position?hiringType=4_2&keyword=%E5%A4%A7%E6%A8%A1%E5%9E%8B
---

# 美团招聘数据获取方式

## 目标链接

- 页面链接：`https://zhaopin.meituan.com/web/position?hiringType=4_2&keyword=%E5%A4%A7%E6%A8%A1%E5%9E%8B`

## 结论

- 页面不是服务端直接返回完整职位列表，而是前端动态渲染。
- 真实职位数据来自接口，不在初始 HTML 里。
- 最稳定的方案是直接还原职位列表接口和职位详情接口。

## 推荐做法

### 1. 最稳定的数据入口

- 列表接口：`POST https://zhaopin.meituan.com/api/official/job/getJobList`
- 详情接口：`POST https://zhaopin.meituan.com/api/official/job/getJobDetail`
- 请求头：

```http
Content-Type: application/json
```

### 2. 关键请求体

- URL 中的 `hiringType=4_2` 需要还原为：

```json
{
  "jobType": [
    {
      "code": "4",
      "subCode": ["2"]
    }
  ],
  "typeCode": ["2"]
}
```

- 一个可工作的列表请求体示例：

```json
{
  "page": {
    "pageNo": 1,
    "pageSize": 10
  },
  "jobShareType": "1",
  "keywords": "大模型",
  "cityList": [],
  "department": [],
  "jfJgList": [],
  "jobType": [
    {
      "code": "4",
      "subCode": ["2"]
    }
  ],
  "typeCode": ["2"],
  "specialCode": []
}
```

### 3. 数据来源确认方式

- 页面会加载前端 bundle，真实接口可从 bundle 和 sourcemap 反推出。
- 已确认前端 service 中存在这些接口：
  - `POST /api/official/job/getJobList`
  - `POST /api/official/job/getJobDetail`
  - `POST /api/official/city/search`
  - `POST /api/official/en/city/search`
  - `GET /api/official/job/search/enum?enumType=...`

### 4. 字段映射

- 职位唯一标识字段 -> `job_id`
- 职位标题字段 -> `title`
- 详情页链接 -> `detail_url`
- 部门字段 -> `department`
- 城市字段 -> `locations`
- 职责字段 -> `job_duty`
- 要求字段 -> `job_requirement`
- 完整返回体 -> `raw`

## 成功请求样例

- 请求成功时通常返回：
  - `status = 1`
  - `message = 成功`
  - `data.totalCount = 80`（示例搜索词为“大模型”时）

## 已知问题

- 搜索页本身只适合定位筛选条件，不适合直接解析职位正文。
- 应优先拉取详情接口，不要只靠列表摘要做匹配分析。

## 更新规则

- 只保留当前确认可用的方法。
- 如果参数结构变化，直接更新正文，不保留 dead ends。
- 不记录 Cookie、token 或任何个人请求头。
