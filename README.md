# resume-job-fit-screening

一个面向中文求职者的 Codex Skill。  
它的目标很直接：**把“海量、杂乱、看不完的官网 JD”压缩成一份真正值得投的岗位清单。**

## 这玩意为什么值得用

现在很多公司的官网招聘页都有几个共同问题：

- 岗位很多，但真正适合你的不多
- 搜索结果里混着大量“看起来相关，实际不该投”的 JD
- 一个个点开看职责、要求、部门、地点，特别耗时间
- 看完几十个 JD 之后，人会麻，判断标准也会越来越飘

这个 skill 干的事，就是把这段枯燥又重复的劳动接过去：

- 自动读取招聘搜索结果页
- 结合你的简历和偏好做严格筛选
- 给出 `推荐 / 备选 / 不建议 / 跳过`
- 生成一份证据充分、可回看的 Markdown 报告

一句话说：  
**别再把时间浪费在“逐个点开官网 JD 然后犹豫半小时”上。**

## 它到底能帮你做什么

你给它：

- 一个招聘搜索结果页链接
- 一份简历，或者一个已经保存好的本地账户
- 可选的偏好，比如想投什么方向、不想投什么方向

它返回给你：

- 一份岗位筛选报告
- Top-K 推荐岗位
- 每个岗位的核心匹配点和硬伤
- 为什么建议投、为什么不建议投
- 全量岗位的处理结论，方便你回头检查

## 安装非常简单

最省事的方式，不是自己手动折腾目录，而是**把仓库链接直接发给 Codex**。

把下面这段话复制给你的 Codex：

```text
请帮我安装这个 skill：
https://github.com/2218259767/resume-job-fit-screening

安装完成后，再帮我启用这个社区 site-notes 仓库：
https://github.com/2218259767/resume-job-fit-screening-site-notes
```

如果你愿意，也可以说得更直接一点：

```text
帮我安装这个 skill，并初始化到可用状态：
https://github.com/2218259767/resume-job-fit-screening
```

对于大多数用户，这已经够了。

### 手动安装方式

如果你就是想手动装，也可以：

```bash
git clone https://github.com/2218259767/resume-job-fit-screening.git \
  ~/.codex/skills/resume-job-fit-screening

python ~/.codex/skills/resume-job-fit-screening/scripts/init_runtime.py \
  --registry-enabled true \
  --registry-manifest-url https://raw.githubusercontent.com/2218259767/resume-job-fit-screening-site-notes/main/index.json \
  --registry-notes-base-url https://raw.githubusercontent.com/2218259767/resume-job-fit-screening-site-notes/main/
```

## 怎么使用

### 你至少需要给它两个东西

1. 招聘搜索结果页链接
2. 简历，或者一个本地账户

### 什么叫“招聘搜索结果页链接”

不是公司招聘首页，也不是随便一个职位详情页，  
而是**你已经带好关键词或筛选条件的搜索结果页**。

例如：

```text
https://zhaopin.meituan.com/web/position?hiringType=4_2&keyword=%E5%A4%A7%E6%A8%A1%E5%9E%8B
```

为什么这个链接很重要？

- 它决定了 skill 这次到底抓什么范围的岗位
- 它能保留你的关键词、校招/实习筛选、项目筛选等上下文
- 它能避免“把整个官网所有职位都拉下来再分析”这种低效操作

### 最容易理解的使用方式

#### 用现有账户直接筛选

```text
请用 resume-job-fit-screening 帮我看这个招聘搜索页：
<招聘搜索结果页链接>

使用我的账户：alice
重点找 AI 应用、Agent、RAG 相关岗位。
```

#### 没有账户，直接贴简历

```text
请用 resume-job-fit-screening 帮我筛这个招聘搜索页：
<招聘搜索结果页链接>

我先不给账户，下面是我的纯文本简历：
<你的简历文本>
```

#### 再加一些偏好

```text
请帮我筛这个招聘搜索页：
<招聘搜索结果页链接>

使用我的账户：alice
偏好：
- 优先：AI 应用、Agent、评测、RAG
- 避开：纯广告算法、纯推荐策略
- topk: 8
```

## 你会拿到什么结果

这个 skill 最后通常会生成一份 Markdown 报告，里面至少会有：

- 本次搜索范围和抓取日期
- 你的偏好摘要
- Top-K 推荐岗位表
- 每个重点岗位的详细分析
- 全部岗位的处理结果

而且它不是只会说“适合”或“不适合”，它会尽量说清楚：

- 哪些岗位确实吃到你的主线优势
- 哪些岗位是方向接近，但短板太明显
- 哪些岗位表面上像能投，实际上面试风险很高

## 这个 skill 的几个进阶特性

### 1. 多账户

你可以创建多个本地账户。

这很适合：

- 不同简历版本
- 不同求职方向
- 帮不同人一起筛岗位

例如：

- `alice-algorithm`
- `alice-ai-product`
- `bob-intern`

### 2. 持久化记忆简历和偏好

第一次建好账户后，后面就不用每次重新贴简历。

账户里可以长期保存：

- 简历文本
- 长期偏好
- 明确不投的方向
- 用户后续反馈沉淀出来的偏好

这意味着你可以越来越“像在用自己的求职助手”，而不是每次从零开始。

### 3. 社区共享 site-notes

招聘站点的抓取方式经常变，而且每个站都不一样。  
这个项目专门把 `site-notes` 拆成了独立仓库：

- skill 负责流程、脚本、评分逻辑
- site-notes 负责共享站点接入知识

好处很直接：

- 别人踩过的坑，你不用再踩一遍
- 某个站点一旦有人修好，大家都能同步受益
- skill 主体不用为了更新某个站点方法频繁发版

社区 site-notes 仓库在这里：

- `https://github.com/2218259767/resume-job-fit-screening-site-notes`

### 4. 本地优先，隐私友好

这个 skill 会把私有数据和公开数据分开：

- 你的账户、简历、偏好都保存在本地 runtime
- 社区共享的只是公开可复用的站点接入说明
- 本地修复过的 note 会优先于社区同步 note

当前优先级是：

1. `local`
2. `synced`
3. `bundled`

## 当前已支持的站点

目前仓库里已经内置或提供了这些站点的 site-notes：

- 美团 `meituan`
- 快手 `kuaishou`
- 飞书招聘站 `feishu`
- 字节跳动 `bytedance`
- 小红书 `xiaohongshu`
- 阿里巴巴 `alibaba`

这意味着你开箱就能在这些站点上复用已有经验，而不是每次重新从抓包开始。

## 这个项目适合谁

- 官网岗位很多、懒得一个个点开的人
- 想把投递时间花在高概率岗位上的人
- 有明确技术主线，希望严格筛岗位的人
- 想把“简历 + 偏好 + 筛选方法”沉淀下来长期复用的人
- 愿意给社区补站点说明、一起把工具做得更好的人

## 仓库结构

```text
.
├── SKILL.md
├── agents/openai.yaml
├── scripts/
├── references/
│   ├── bundled_site_notes/
│   ├── account_template.md
│   ├── site_note_template.md
│   ├── jd_matching_methodology.md
│   ├── strict_reviewer_prompt.md
│   └── output_format.md
├── README.md
├── LICENSE
└── .gitignore
```

## 隐私与安全

请不要把这些内容提交到公开仓库：

- `~/.codex/data/resume-job-fit-screening/accounts/`
- `~/.codex/data/resume-job-fit-screening/site_notes/local/`
- `~/.codex/data/resume-job-fit-screening/publish_queue/`
- 任何带 Cookie、token、私有 header 的抓取记录

## 相关仓库

- Skill 本体：
  - `https://github.com/2218259767/resume-job-fit-screening`
- 社区共享站点说明：
  - `https://github.com/2218259767/resume-job-fit-screening-site-notes`
