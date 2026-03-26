# 账户模板

账户文件保存在本地 runtime 目录下，不进入社区同步。

推荐格式：

```markdown
---
account_id: alice
schema_version: 1
display_name: Alice
created_at: 2026-03-24
updated_at: 2026-03-24
default_topk: 5
keyword_expansion: true
default_account: false
---

# Resume

<纯文本简历>

## Confirmed Preferences

## Hard Constraints

## Pending Preference Updates

## Feedback Summary

```

使用规则：

- 账户只保留长期有效的摘要，不存每次会话的完整日志。
- 新反馈先进入 `Pending Preference Updates`，确认后再移动到 `Confirmed Preferences`。
- 账户内容默认只存本地，不发布到公共仓库。
