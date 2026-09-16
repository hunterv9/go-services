# Task Tracker

> Team-lead cập nhật file này sau MỖI task. Mọi agent đều đọc được.

## Active Tasks

_(Không có task đang chạy)_

## Completed Tasks

### [Todo List App] — Status: DONE
- **Date**: 2026-09-15
- **Agents**: pm, ux-ui, devops, architect, dev, test-runner, qc, security
- **Summary**: Todo app HTML/CSS/JS + core logic tách riêng, dark glassmorphism, 43 tests, QC CONDITIONAL (SPEC placeholder đã fix), Security Low (thiếu CSP)
- **Files**: `projects/todo-app/todo-app.html`, `todo-app.css`, `todo-app.js`, `todo-app-core.js`, `todo-app.test.js`, `SPEC.md`, `README.md`

| # | Agent | Task | Status | Output |
|---|-------|------|--------|--------|
| 1 | pm | SPEC.md | DONE | 7 acceptance criteria |
| 2 | ux-ui | HTML+CSS | DONE | dark theme, responsive |
| 3 | devops | scaffold | DONE | 7 files |
| 4 | architect | review kiến trúc | DONE | pattern tách core |
| 5 | dev | JS logic | DONE | core + DOM, XSS-safe |
| 6 | test-runner | tests | DONE | 43 assertions |
| 7 | qc | review | DONE | CONDITIONAL |
| 8 | security | audit | DONE | 1 Low (CSP) |

### [Login Form] — Status: DONE
- **Date**: 2026-09-14
- **Agents**: pm, dev, ux-ui, qc, test-runner
- **Summary**: Form login HTML/CSS/JS với validation, dark theme
- **Files**: `apps/go-viet/src/components/login/login.html`, `login.css`, `login.js`

### [User Card Component] — Status: DONE
- **Date**: 2026-09-14
- **Agents**: pm, dev, ux-ui, qc, test-runner
- **Summary**: Glassmorphism card component với inline edit form
- **Files**: `apps/go-viet/src/components/user-card/user-card.html`, `user-card.css`, `user-card.js`

### [Calculator App] — Status: DONE
- **Date**: 2026-09-14
- **Agents**: dev, ux-ui, test-runner
- **Summary**: Calculator HTML/CSS/JS, dark/light theme, keyboard support, 8/8 tests pass
- **Files**: `projects/calculator/calculator.html`, `calculator.css`, `calculator.js`, `calculator-core.js`, `calculator.test.js`

### [Utils Library] — Status: DONE
- **Date**: 2026-09-14
- **Agents**: dev, opencode-dev, cline-dev, test-runner
- **Summary**: 3 coders song song — string-helpers, array-helpers, date-helpers. Syntax PASS.
- **Files**: `projects/utils/string-helpers.js`, `array-helpers.js`, `date-helpers.js`

### [Test Gate (math + string)] — Status: DONE
- **Date**: 2026-09-14
- **Agents**: dev, opencode-dev, test-runner
- **Summary**: Test wave gate rule — 2 coders tuần tự, 12/12 tests pass
- **Files**: `projects/test-gate2/math.js`, `string.js`

---

## Format cho task mới

```markdown
## [Task Name] — Status: [DONE / IN_PROGRESS / BLOCKED]
- **Date**: YYYY-MM-DD
- **Agents**: dev, test-runner, ...
- **Summary**: Mô tả ngắn
- **Files**: paths

| # | Agent | Task | Status | Output |
|---|-------|------|--------|--------|
```
