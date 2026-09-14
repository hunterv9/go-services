# Technical Debt Tracker

> Ghi lại mọi vấn đề kỹ thuật tìm thấy bởi qc, security, hoặc team-lead.

## Active Debt

### [TD-001] Hardcoded demo credentials in login.js
- **Priority**: HIGH
- **Found by**: qc
- **Date**: 2026-09-14
- **Files**: `apps/go-viet/src/components/login/login.js:73`
- **Description**: `admin@goviet.vn` / `123456` hardcoded. Phải thay bằng API call sang server auth.
- **Status**: OPEN

### [TD-002] Missing empty-input validation in user-card
- **Priority**: MEDIUM
- **Found by**: qc
- **Date**: 2026-09-14
- **Files**: `apps/go-viet/src/components/user-card/user-card.js:37-42`
- **Description**: Form submit không validate empty/whitespace-only input. Cần trim + empty check trước khi update DOM.
- **Status**: OPEN

### [TD-003] Memory leak — dangling keydown listener
- **Priority**: MEDIUM
- **Found by**: qc
- **Date**: 2026-09-14
- **Files**: `apps/go-viet/src/components/user-card/user-card.js:45-47`
- **Description**: `document.addEventListener('keydown', ...)` không bao giờ remove. Nếu `.user-card` detach khỏi DOM → memory leak. Cần cleanup hoặc AbortController.
- **Status**: OPEN

### [TD-004] Missing aria-label on edit/save/cancel buttons
- **Priority**: LOW
- **Found by**: qc
- **Date**: 2026-09-14
- **Files**: `apps/go-viet/src/components/user-card/user-card.html`
- **Description**: Edit/Save/Cancel buttons thiếu aria-label cho screen readers.
- **Status**: OPEN

---

## Resolved Debt

_(Chưa có debt nào được resolve)_

---

## Format cho debt mới

```markdown
### [TD-XXX] Tiêu đề
- **Priority**: CRITICAL / HIGH / MEDIUM / LOW
- **Found by**: agent name
- **Date**: YYYY-MM-DD
- **Files**: path/to/file.ext
- **Description**: Mô tả vấn đề
- **Status**: OPEN / IN_PROGRESS / RESOLVED
```
