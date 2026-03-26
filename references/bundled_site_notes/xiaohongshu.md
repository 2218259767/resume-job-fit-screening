---
site_slug: xiaohongshu
schema_version: 2
content_version: 1
verified_at: 2026-03-24
public_safe: true
access_mode: public
method_type: official_json_api
maintainer: bundled
example_search_url: https://job.xiaohongshu.com/campus/position?positionName=%E5%A4%A7%E6%A8%A1%E5%9E%8B&campusRecruitTypes=term_intern
---

# 小红书招聘数据获取方式

## 目标链接

- 页面链接：`https://job.xiaohongshu.com/campus/position?positionName=%E5%A4%A7%E6%A8%A1%E5%9E%8B&campusRecruitTypes=term_intern`

## 结论

- 页面不是服务端直出完整职位数据，而是前端动态渲染的 SPA 壳页面。
- 真实职位列表来自官网接口 `POST /websiterecruit/position/pageQueryPosition`。
- 职位详情来自官网接口 `GET /websiterecruit/position/queryPositionDetail?positionId=<id>`。
- 校招实习检索使用 `recruitType: "campus"`；这个页面里的 `campusRecruitTypes=term_intern` 需要还原成数组字段 `["term_intern"]`。

## 推荐做法

### 1. 最稳定的数据入口

- 列表接口：`POST https://job.xiaohongshu.com/websiterecruit/position/pageQueryPosition`
- 请求头：

```http
Content-Type: application/json
User-Agent: Mozilla/5.0
```

- 一个可工作的列表请求体示例：

```json
{
  "pageNum": 1,
  "pageSize": 50,
  "recruitType": "campus",
  "positionName": "大模型",
  "campusRecruitTypes": ["term_intern"]
}
```

### 2. 职位详情获取方式

- 详情接口：`GET https://job.xiaohongshu.com/websiterecruit/position/queryPositionDetail?positionId=<positionId>`
- 可点击详情页规则：`https://job.xiaohongshu.com/campus/position/<positionId>`

### 3. 字段映射

- `positionId` -> `job_id`
- `positionName` -> `title`
- `https://job.xiaohongshu.com/campus/position/<positionId>` -> `detail_url`
- `positionType` / `jobType` -> `department`
- `workplace` -> `locations`
- `duty` -> `job_duty`
- `qualification` -> `job_requirement`
- 完整列表项和详情返回体 -> `raw`

## 成功请求样例

- 最小可复制请求：

```bash
curl -sS \
  -A 'Mozilla/5.0' \
  -H 'Content-Type: application/json' \
  --data '{"pageNum":1,"pageSize":50,"recruitType":"campus","positionName":"大模型","campusRecruitTypes":["term_intern"]}' \
  'https://job.xiaohongshu.com/websiterecruit/position/pageQueryPosition'
```

- 成功返回时的关键字段：
  - `success = true`
  - `data.total`
  - `data.list[*].positionId`
  - `data.list[*].publishTime`

## 已知问题

- `recruitType` 必须使用 `campus`，`school_recruit` 会返回参数异常。
- `campusRecruitTypes` 必须是数组；传成字符串会触发 `400 Bad Request`。
- `campusRecruitType` 这种单数字段不会生效。
- `publishTime` 在列表接口里可直接拿到，详情接口不一定返回该字段。
- 初始 HTML 只有前端壳，不适合直接解析职位正文。

## 更新规则

- 只保留当前确认可用的方法。
- 如果筛选字段或详情参数变化，直接更新正文。
- 不记录 Cookie、token、个人请求头或调试 dead ends。
