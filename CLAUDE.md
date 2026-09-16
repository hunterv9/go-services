# Virtual Dev Team — go-services

Bộ agent đa-nhiệm vụ nằm ở `.claude/agents/`. `team-lead` điều phối, các specialist thực thi.

## Cách chạy

- Với mọi yêu cầu build feature / fix bug / refactor: delegate cho subagent `team-lead` (hoặc dùng lệnh `/team`), không code trực tiếp ở thread chính.
- Với câu hỏi nhỏ / đọc code / giải thích: trả lời trực tiếp, không cần team.

## Quy ước

- Mọi report của agent: tiếng Việt, ≤400 token (analyst ≤600 token).
- Tracking: `TASKS.md` (task) + `TECH_DEBT.md` (nợ kỹ thuật) ở repo root. Chỉ agent `dev` được sửa 2 file này, theo lệnh của team-lead.
- Làm việc từ repo root, dùng đường dẫn tương đối.
- Không đọc/ghi trong `.claude/worktrees/` — đó là worktree tạm, nội dung không phải state hiện tại.
