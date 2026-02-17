# Claude issues status (from `claude issues.txt`)

This file tracks the concrete requests/complaints extracted from the Claude chatlog and whether they are resolved.

## Status legend
- ✅ Resolved (verified in generated `site/` output)
- ⚠️ Partially resolved / needs decision
- ❌ Not resolved

## Items (checked bottom → top)

### 1) Wiki redirects
**Complaint:** `/wiki/*` gave 404, and language wiki paths were inconsistent.

**Current behavior:**
- `/wiki/<Title>/` exists as a static HTML redirect page.
- `/{lang}/wiki/<Title>/` exists as a static HTML redirect page.
- All languages currently redirect to the same wiki base: `https://lifeism.miraheze.org/wiki/<Title>`.

**Verification:**
- `site/wiki/Sagittarius_1/index.html` redirects to `https://lifeism.miraheze.org/wiki/Sagittarius_1`
- `site/wiki/Main_Page/index.html` redirects to `https://lifeism.miraheze.org/wiki/Main_Page`

✅ Resolved.

### 2) Datepicker not implemented
**Complaint:** datepicker page did not seem to work.

**Verification:**
- `site/en/calendar/datepicker/index.html` contains interactive picker JS (year input, month selector toggle, day selection handlers).

✅ Resolved.

### 3) Calendar day pages conflated with Gaiad pages
**Complaint:** `/calendar/<month>/<dd>/` should not show full Gaiad chapter content; it should show day info + link to the corresponding chapter.

**Current behavior:**
- Day pages include day info + wiki intro/overview (from XML export), plus a link to the corresponding chapter page.
- Day pages may include a short **chapter summary** section.
- Day pages do **not** embed the full chapter text.

**Verification:**
- `site/en/calendar/sagittarius/01/index.html` links to `/en/gaiad/001/` and includes `Chapter summary`, but not full chapter body.

✅ Resolved per latest requirement: *summary ok; full chapters not on day pages*.

### 4) `/calendar/gaian-era` missing
**Complaint:** `/en/calendar/gaian-era` did not exist.

**Verification:**
- `site/en/calendar/gaian-era/index.html` exists.

✅ Resolved.

### 5) Weekday pages requested
**Complaint:** sacred weekday pages needed.

**Verification:**
- Week index exists at `site/en/calendar/week/index.html`
- Individual weekday pages exist under `site/en/calendar/week/<weekday>/index.html`

✅ Resolved.

## Notes
- `claude issues.txt` is a chatlog and includes duplicated blocks due to compaction; this status file is the canonical checklist.
