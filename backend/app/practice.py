"""Phase 11 — CA / accountant workspace: clients, tasks, doc requests, reviews."""
from datetime import datetime

REVIEW_FLOW = {"auto": {"needs_review"}, "needs_review": {"accountant", "ca"},
               "accountant": {"ca", "approved"}, "ca": {"approved"},
               "approved": set()}

TASK_STATES = {"open", "in_progress", "done", "cancelled"}
DOCREQ_STATES = {"requested", "uploaded", "verified", "rejected"}


def _r(x) -> float:
    return round(float(x or 0), 2)


def review_transition(state: str, to: str) -> str:
    if to not in REVIEW_FLOW.get(state, set()):
        raise ValueError(f"Illegal review {state} -> {to}. Complex matters escalate to a professional.")
    return to


def check_task(state: str) -> str:
    if state not in TASK_STATES:
        raise ValueError(f"Bad task state {state}")
    return state


def check_docreq(state: str) -> str:
    if state not in DOCREQ_STATES:
        raise ValueError(f"Bad doc-request state {state}")
    return state


def practice_overview(clients: list, tasks: list, reviews: list) -> dict:
    open_tasks = sum(1 for t in tasks if t.get("status") in ("open", "in_progress"))
    pending_reviews = sum(1 for r in reviews if r.get("state") not in ("approved",))
    return {"clients": len(clients), "open_tasks": open_tasks,
            "pending_reviews": pending_reviews,
            "note": "Routine work automated; disputes/audits/litigation escalate to a qualified professional."}
