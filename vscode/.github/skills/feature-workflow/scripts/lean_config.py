"""
lean_config.py - shared plan.md, request.md, and review.md parsers for feature-workflow scripts.

Adapted from tlc-spec-lean 3.2.0 (CC-BY-4.0). Pure standard library, zero dependencies.
"""

from datetime import date
import os
import re

BINDING_RE = re.compile(r"(?<![-\w])binding\b", re.IGNORECASE)
NOT_BINDING_RE = re.compile(r"\b(non|not)[- ]binding\b", re.IGNORECASE)
IMAGE_EXT_RE = re.compile(r"\.(?:png|jpe?g|webp|gif)\b", re.IGNORECASE)
CAPTURE_REF_RE = re.compile(r"(?:captures/|[\w./-]+\.(?:png|jpe?g|webp|gif))", re.IGNORECASE)
CAPTURE_FILE_RE = re.compile(r"([A-Za-z0-9._-]+\.(?:png|jpe?g|webp|gif))", re.IGNORECASE)
CRITERION_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
# CommonMark 0.31.2 §4.5: fenced code blocks allow 0-3 ASCII spaces of indentation (never a tab).
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")

APPROVED_FULL_RE = re.compile(
    r"^\**\s*Approved\s*:?\s*\**\s*:?\s*(\d{4}-\d{2}-\d{2})\b.*\buser\s*:\s*[\"“][^\"”]*\S[^\"”]*[\"”]",
    re.IGNORECASE,
)
APPROVED_ANY_RE = re.compile(r"^\**\s*Approved\s*:?\s*\**\s*:\s*\S", re.IGNORECASE)
SMALL_CHANGE_RE = re.compile(r"^\**\s*Small change\s*:?\s*\**\s*:?\s*yes\b", re.IGNORECASE)
REVIEW_SKIPPED_RE = re.compile(r"^\**\s*Review\s*:?\s*\**\s*:?\s*skipped\b", re.IGNORECASE)
REVIEW_SENT_RE = re.compile(r"^\**\s*Review\s*:?\s*\**\s*:?\s*sent at\s+`?([0-9a-f]{4,40})`?", re.IGNORECASE)
FIX_ROUND2_DONE_RE = re.compile(r"^\**\s*Fix pass\s*:?\s*\**\s*:?\s*round\s*2\s+done\b", re.IGNORECASE)
FIX_DONE_RE = re.compile(r"^\**\s*Fix pass\s*:?\s*\**\s*:?\s*(?:round\s*1\s+)?done\b", re.IGNORECASE)
RECHECK_ROUND3_SENT_RE = re.compile(
    r"^\**\s*Re-check\s*:?\s*\**\s*:?\s*round\s*3\s+sent at\s+`?([0-9a-f]{4,40})`?",
    re.IGNORECASE,
)
RECHECK_SENT_RE = re.compile(
    r"^\**\s*Re-check\s*:?\s*\**\s*:?\s*(?:round\s*2\s+)?sent at\s+`?([0-9a-f]{4,40})`?",
    re.IGNORECASE,
)
RECHECK_NOT_NEEDED_RE = re.compile(r"^\**\s*Re-check\s*:?\s*\**\s*:?\s*not needed\b", re.IGNORECASE)
RECHECK_PASS_RE = re.compile(r"^\**\s*Re-check\s*:?\s*\**\s*:?\s*pass\b", re.IGNORECASE)
RECHECK_ROUND2_OPEN_RE = re.compile(r"^\**\s*Re-check\s*:?\s*\**\s*:?\s*round\s*2\s+open\b", re.IGNORECASE)
RECHECK_ESCALATED_RE = re.compile(
    r"^\**\s*Re-check\s*:?\s*\**\s*:?\s*(?:open\s*-\s*escalated|escalated|round\s*3\s+open)\b",
    re.IGNORECASE,
)
RECHECK_OPEN_RE = re.compile(r"^\**\s*Re-check\s*:?\s*\**\s*:?\s*open\b", re.IGNORECASE)
ANY_STATE_RE = re.compile(
    r"^\**\s*(Small change|Approved|Settled mid-build|Gates|Review|Fix pass|Re-check)\s*:?\s*\**\s*:",
    re.IGNORECASE,
)

ROUND1_VERDICT_RE = re.compile(r"^\s*-\s*\*\*Verdict:\*\*\s*`?(PASS|CHANGES_REQUIRED|BLOCKED)`?\b", re.IGNORECASE)
RECHECK_HEADING_RE = re.compile(r"^##\s+Re-check\b(?:\s*\(\s*Round\s*(\d+)\s*\))?", re.IGNORECASE)
RECHECK_VERDICT_RE = re.compile(r"^\s*-\s*\*\*Re-check verdict:\*\*\s*`?(PASS|OPEN)`?\b", re.IGNORECASE)


def update_fence(line, fence):
    """Track CommonMark 0.31.2 §4.5 fenced code blocks (0-3 ASCII spaces, backtick or tilde).

    Returns (is_fence_line, new_fence, info_string_or_None).
    """
    m = FENCE_RE.match(line)
    if not m:
        return False, fence, None
    marker, tail = m.groups()
    if fence is None:
        # Backtick code block info strings may not contain backticks (CommonMark §4.5).
        if marker[0] == "`" and "`" in tail:
            return False, None, None
        info = tail.strip().split()[0].lower() if tail.strip() else ""
        return True, marker, info
    if marker[0] == fence[0] and len(marker) >= len(fence) and not tail.strip(" \t\r"):
        return True, None, None
    return False, fence, None


def strip_all_fences(lines):
    """Return lines outside CommonMark fenced code blocks (backtick or tilde)."""
    out, fence = [], None
    for ln in lines:
        is_fence, fence, _ = update_fence(ln, fence)
        if not is_fence and fence is None:
            out.append(ln)
    return out


def header_lines(raw_lines):
    """Return non-fenced lines in the leading metadata block before the first `## ` heading."""
    out, fence = [], None
    for ln in raw_lines:
        is_fence, fence, _ = update_fence(ln, fence)
        if is_fence or fence is not None:
            continue
        s = ln.strip()
        if re.match(r"^##\s+\S", s):
            break
        out.append(s)
    return out


def _valid_iso_date(text):
    try:
        date.fromisoformat(text)
        return True
    except ValueError:
        return False


def parse_header_state(raw_lines):
    """Parse workflow state strictly from the leading metadata block (above first `## `, outside fences)."""
    hlines = header_lines(raw_lines)
    approved = False
    approved_malformed = False
    small_change = False
    review_skipped = False
    review_sent = None
    fix_round = 0
    recheck_sent = None
    recheck_sent_round = 0
    recheck_closed = None
    recheck_round2_open = False
    recheck_escalated = False
    recheck_open = False
    has_any_state = False

    for s in hlines:
        if ANY_STATE_RE.match(s):
            has_any_state = True
        if SMALL_CHANGE_RE.match(s):
            small_change = True
        m_app = APPROVED_FULL_RE.match(s)
        if m_app and _valid_iso_date(m_app.group(1)):
            approved = True
        elif APPROVED_ANY_RE.match(s) and "<written" not in s.lower():
            approved_malformed = True
        if REVIEW_SKIPPED_RE.match(s):
            review_skipped = True
        m_rev = REVIEW_SENT_RE.match(s)
        if m_rev:
            review_sent = m_rev.group(1)
        if FIX_ROUND2_DONE_RE.match(s):
            fix_round = max(fix_round, 2)
        elif FIX_DONE_RE.match(s):
            fix_round = max(fix_round, 1)
        m_rc3 = RECHECK_ROUND3_SENT_RE.match(s)
        if m_rc3:
            recheck_sent = m_rc3.group(1)
            recheck_sent_round = 3
        else:
            m_rc2 = RECHECK_SENT_RE.match(s)
            if m_rc2:
                recheck_sent = m_rc2.group(1)
                recheck_sent_round = 2
        if RECHECK_NOT_NEEDED_RE.match(s):
            recheck_closed = "not needed"
        elif RECHECK_PASS_RE.match(s):
            recheck_closed = "pass"
        if RECHECK_ESCALATED_RE.match(s):
            recheck_escalated = True
            recheck_open = True
        elif RECHECK_ROUND2_OPEN_RE.match(s):
            recheck_round2_open = True
            recheck_open = True
        elif RECHECK_OPEN_RE.match(s):
            recheck_open = True

    return {
        "has_any_state": has_any_state,
        "small_change": small_change,
        "approved": approved,
        "approved_malformed": approved_malformed and not approved,
        "review_skipped": review_skipped,
        "review_sent": review_sent,
        "fix_done": fix_round >= 1,
        "fix_round": fix_round,
        "recheck_sent": recheck_sent,
        "recheck_sent_round": recheck_sent_round,
        "recheck_closed": recheck_closed,
        "recheck_round2_open": recheck_round2_open,
        "recheck_escalated": recheck_escalated,
        "recheck_open": recheck_open,
    }


def parse_review_state(review_path):
    """Inspect review.md for Audit Header Round 1 verdict and ## Re-check verdicts (outside fences).

    Round 1 `- **Verdict:**` is read only from the Audit Header (above the first `## ` heading).
    `## Re-check` verdicts are read only inside each `## Re-check` section (up to the next `## `).
    """
    if not os.path.isfile(review_path):
        return {
            "exists": False,
            "round1_verdict": None,
            "rechecks": [],
            "recheck_count": 0,
            "has_recheck": False,
            "recheck_verdict": None,
        }
    with open(review_path, encoding="utf-8", errors="replace") as f:
        lines = strip_all_fences(f.read().splitlines())
    round1_verdict = None
    rechecks = []
    section = "header"
    for ln in lines:
        s = ln.strip()
        m_rh = RECHECK_HEADING_RE.match(s)
        if m_rh:
            section = "recheck"
            declared = int(m_rh.group(1)) if m_rh.group(1) else None
            rechecks.append({"round": declared, "verdict": None})
            continue
        if re.match(r"^##\s+\S", s):
            section = "other"
            continue
        if section == "header":
            m = ROUND1_VERDICT_RE.match(s)
            if m:
                round1_verdict = m.group(1).upper()
        elif section == "recheck" and rechecks:
            m = RECHECK_VERDICT_RE.match(s)
            if m:
                rechecks[-1]["verdict"] = m.group(1).upper()
    return {
        "exists": True,
        "round1_verdict": round1_verdict,
        "rechecks": rechecks,
        "recheck_count": len(rechecks),
        "has_recheck": bool(rechecks),
        "recheck_verdict": rechecks[-1]["verdict"] if rechecks else None,
    }


def recheck_pass_error(st, rev):
    """Return None if `**Re-check:** PASS` is legitimately backed by review.md (max 3 rounds), else reason."""
    rechecks = rev["rechecks"]
    if not rechecks:
        return "review.md has no `## Re-check` section"
    if len(rechecks) > 2 or any(r["round"] is not None and r["round"] >= 4 for r in rechecks):
        return "review.md exceeds the 3-round review cap (no 4th review round allowed; escalate to the user)"
    if len(rechecks) == 1:
        r2 = rechecks[0]
        if r2["round"] not in (None, 2):
            return f"review.md has Round {r2['round']} re-check without Round 2"
        if r2["verdict"] != "PASS":
            return "review.md Round 2 `## Re-check` verdict is not PASS"
        if st["fix_round"] < 1:
            return "Round 2 PASS requires Fix pass 1 (`**Fix pass:** done`) to be recorded"
        return None
    # len(rechecks) == 2: Round 2 must have been OPEN, Fix pass 2 done, and Round 3 PASS.
    r2, r3 = rechecks[0], rechecks[1]
    if r2["round"] not in (None, 2):
        return f"review.md first re-check declares Round {r2['round']} instead of Round 2"
    if r2["verdict"] != "OPEN":
        return "Round 3 re-check requires Round 2 to have returned OPEN"
    if r3["round"] not in (None, 3):
        return f"review.md second re-check declares Round {r3['round']} instead of Round 3"
    if r3["verdict"] != "PASS":
        return "review.md Round 3 `## Re-check` verdict is not PASS"
    if st["fix_round"] < 2:
        return "Round 3 PASS requires Fix pass 2 (`**Fix pass:** round 2 done`) to be recorded"
    return None


def plan_approved(raw_lines):
    """True when leading metadata holds a valid date and verbatim `user: "..."` quote."""
    return parse_header_state(raw_lines)["approved"]


def _section(lines, name):
    """Return lines under a `#`/`##` heading named `name`, up to the next `#`/`##` heading."""
    out, inside = [], False
    for ln in lines:
        s = ln.strip()
        if re.match(r"^#{1,2}\s+\S", s):
            inside = re.match(r"^#{1,2}\s+" + re.escape(name) + r"\b", s, re.IGNORECASE) is not None
            continue
        if inside:
            out.append(s)
    return out


def plan_criteria(plan_lines):
    """Return the text of every numbered criterion under `## Criteria`."""
    out = []
    for s in _section(plan_lines, "Criteria"):
        m = CRITERION_RE.match(s)
        if m:
            out.append(m.group(1))
    return out


def plan_marks_binding(plan_lines):
    """True when plan.md's `## Sources` marks any source binding."""
    return any(BINDING_RE.search(s) and not NOT_BINDING_RE.search(s) for s in _section(plan_lines, "Sources"))


def plan_marks_binding_visual(plan_lines):
    """True when `## Sources` marks a visual capture/image source as binding (not a non-visual ticket)."""
    for s in _section(plan_lines, "Sources"):
        if BINDING_RE.search(s) and not NOT_BINDING_RE.search(s):
            if CAPTURE_REF_RE.search(s) or "![" in s:
                return True
    return False


def capture_binding_sets(plan_lines):
    """Return (explicit_binding_files, explicit_non_binding_files) cited under `## Sources`."""
    binding_files, non_binding_files = set(), set()
    for s in _section(plan_lines, "Sources"):
        files = {m.lower() for m in CAPTURE_FILE_RE.findall(s)}
        if not files:
            continue
        if NOT_BINDING_RE.search(s):
            non_binding_files.update(files)
        elif BINDING_RE.search(s):
            binding_files.update(files)
    return binding_files, non_binding_files
