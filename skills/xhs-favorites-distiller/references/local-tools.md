# 本地原文队列

使用此技能目录内的 `scripts/inbox.py`。Python 3.10+，无第三方依赖、无网络、无定时器。它只记录原文和 Agent 的判断，不替 Agent 判断价值或激活。

```sh
python3 <skill-dir>/scripts/inbox.py ingest <获准的导出.json>
python3 <skill-dir>/scripts/inbox.py pending --limit 5
python3 <skill-dir>/scripts/inbox.py get <source> <id>
python3 <skill-dir>/scripts/inbox.py assess <source> <id> --revision <刚读取的版本> --decision <skip或candidate或needs-evidence> --reason '<实际判断理由>'
```

导入格式是 JSON 数组，每项包含字符串 `source,id,title,url,content` 与布尔 `complete`。`source + id` 唯一，不能用标题充当稳定 ID。`complete` 由采集者依据实际读取范围填写；工具不会判断图像/视频是否已读全。

首次导入进入待评；完全相同的条目不重复待评；同一 ID 的标题、链接、正文或完整性标记改变时递增 revision，自动再次待评。读取 pending 不会消费。使用读到的 revision 写判断，期间条目已变化会拒绝旧判断，先重读即可。

“needs-evidence”表示当时材料不足，不是永久跳过。新痛点/真实失败证据到来时按 `get` 重读已知候选，再记录新判断。同一事实没有变化不重复评测。

数据默认在 `~/.local/share/saved-to-practice/inbox.sqlite3`；`--data-dir`（置于子命令之前）或 `SAVED_TO_PRACTICE_DATA` 可改变根目录。该数据库是导入原文和逐条当前判断的唯一来源，使用工具后不再另写同一条目的 decisions.json。来源授权和日程仍在 profile.json；来源观察范围单独保留。

导出文件和数据库都属于私人资料，放仓库外；不要自动上传。用户要求公开技能时只导出提炼的方法和必要脱敏证据。
