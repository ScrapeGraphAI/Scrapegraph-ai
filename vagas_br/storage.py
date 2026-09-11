"""SQLite persistence and query helpers."""

from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import Job

DEFAULT_DB = Path(
    os.getenv("VAGAS_DB", Path(__file__).resolve().parent / "data" / "vagas.db")
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source        TEXT NOT NULL,
    external_id   TEXT NOT NULL,
    title         TEXT NOT NULL,
    url           TEXT NOT NULL,
    company       TEXT,
    location_raw  TEXT,
    city          TEXT,
    uf            TEXT,
    region        TEXT,
    workplace     TEXT,
    contract      TEXT,
    seniority     TEXT,
    area          TEXT,
    tags          TEXT NOT NULL DEFAULT '[]',
    salary        TEXT,
    published_at  TEXT,
    description   TEXT,
    query         TEXT,
    first_seen    TEXT NOT NULL,
    last_seen     TEXT NOT NULL,
    active        INTEGER NOT NULL DEFAULT 1,
    UNIQUE(source, external_id)
);
CREATE INDEX IF NOT EXISTS idx_jobs_uf ON jobs(uf);
CREATE INDEX IF NOT EXISTS idx_jobs_region ON jobs(region);
CREATE INDEX IF NOT EXISTS idx_jobs_contract ON jobs(contract);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_active ON jobs(active);
CREATE TABLE IF NOT EXISTS runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source      TEXT NOT NULL,
    started_at  TEXT NOT NULL,
    finished_at TEXT,
    collected   INTEGER NOT NULL DEFAULT 0,
    error       TEXT
);
"""

_UPSERT_COLUMNS = [
    "title",
    "url",
    "company",
    "location_raw",
    "city",
    "uf",
    "region",
    "workplace",
    "contract",
    "seniority",
    "area",
    "tags",
    "salary",
    "published_at",
    "description",
    "query",
]


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def connect(path: Path | str = DEFAULT_DB) -> sqlite3.Connection:
    """Open (and initialise) the SQLite database."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def upsert_jobs(conn: sqlite3.Connection, jobs: Iterable[Job]) -> int:
    """Insert new jobs or refresh existing ones. Returns number processed."""
    now = _now()
    n = 0
    set_clause = ", ".join(f"{c}=excluded.{c}" for c in _UPSERT_COLUMNS)
    sql = f"""
        INSERT INTO jobs (source, external_id, {", ".join(_UPSERT_COLUMNS)},
                          first_seen, last_seen, active)
        VALUES (?, ?, {", ".join("?" for _ in _UPSERT_COLUMNS)}, ?, ?, 1)
        ON CONFLICT(source, external_id) DO UPDATE SET
            {set_clause}, last_seen=excluded.last_seen, active=1
    """
    with conn:
        for job in jobs:
            d = job.to_dict()
            d["tags"] = json.dumps(d["tags"], ensure_ascii=False)
            row = [job.source, job.external_id] + [d[c] for c in _UPSERT_COLUMNS]
            row += [now, now]
            conn.execute(sql, row)
            n += 1
    return n


def deactivate_stale(conn: sqlite3.Connection, source: str, older_than: str) -> int:
    """Mark jobs of ``source`` not seen since ``older_than`` (ISO) as inactive."""
    with conn:
        cur = conn.execute(
            "UPDATE jobs SET active=0 WHERE source=? AND last_seen<? AND active=1",
            (source, older_than),
        )
    return cur.rowcount


def start_run(conn: sqlite3.Connection, source: str) -> int:
    with conn:
        cur = conn.execute(
            "INSERT INTO runs (source, started_at) VALUES (?, ?)", (source, _now())
        )
    return int(cur.lastrowid)


def finish_run(
    conn: sqlite3.Connection, run_id: int, collected: int, error: str | None = None
) -> None:
    with conn:
        conn.execute(
            "UPDATE runs SET finished_at=?, collected=?, error=? WHERE id=?",
            (_now(), collected, error, run_id),
        )


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    d["tags"] = json.loads(d.get("tags") or "[]")
    return d


def _build_where(f: dict[str, Any]) -> tuple[str, list[Any]]:
    where = ["1=1"]
    params: list[Any] = []
    if not f.get("include_inactive"):
        where.append("active=1")
    for col in ("uf", "region", "contract", "workplace", "seniority", "area", "source"):
        vals = f.get(col)
        if vals:
            vals = [v for v in (vals if isinstance(vals, list) else [vals]) if v]
            if vals:
                where.append(f"{col} IN ({', '.join('?' for _ in vals)})")
                params.extend(vals)
    if f.get("city"):
        where.append("city LIKE ?")
        params.append(f"%{f['city']}%")
    if f.get("q"):
        for term in str(f["q"]).split():
            where.append(
                "(title LIKE ? OR company LIKE ? OR description LIKE ? OR tags LIKE ?)"
            )
            params.extend([f"%{term}%"] * 4)
    if f.get("tag"):
        tags = f["tag"] if isinstance(f["tag"], list) else [f["tag"]]
        for t in tags:
            where.append("tags LIKE ?")
            params.append(f'%"{t}"%')
    if f.get("days"):
        where.append("(published_at IS NULL OR published_at >= date('now', ?))")
        params.append(f"-{int(f['days'])} days")
    return " AND ".join(where), params


def query_jobs(
    conn: sqlite3.Connection,
    filters: dict[str, Any],
    page: int = 1,
    per_page: int = 50,
    order: str = "recent",
) -> dict[str, Any]:
    """Return a page of jobs matching ``filters`` plus the total count."""
    where, params = _build_where(filters)
    total = conn.execute(f"SELECT COUNT(*) FROM jobs WHERE {where}", params).fetchone()[
        0
    ]
    order_sql = {
        "recent": "COALESCE(published_at, first_seen) DESC, id DESC",
        "title": "title COLLATE NOCASE ASC",
        "company": "company COLLATE NOCASE ASC",
    }.get(order, "COALESCE(published_at, first_seen) DESC, id DESC")
    per_page = max(1, min(per_page, 200))
    page = max(1, page)
    rows = conn.execute(
        f"SELECT * FROM jobs WHERE {where} ORDER BY {order_sql} LIMIT ? OFFSET ?",
        params + [per_page, (page - 1) * per_page],
    ).fetchall()
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
        "items": [_row_to_dict(r) for r in rows],
    }


def facets(conn: sqlite3.Connection, filters: dict[str, Any]) -> dict[str, list[dict]]:
    """Count jobs per filter value (for the UI side bar)."""
    where, params = _build_where(filters)
    out: dict[str, list[dict]] = {}
    for col in ("uf", "region", "contract", "workplace", "seniority", "area", "source"):
        rows = conn.execute(
            f"SELECT {col} AS value, COUNT(*) AS n FROM jobs WHERE {where} "
            f"GROUP BY {col} ORDER BY n DESC",
            params,
        ).fetchall()
        out[col] = [{"value": r["value"], "count": r["n"]} for r in rows]
    tag_counts: dict[str, int] = {}
    for (tags_json,) in conn.execute(f"SELECT tags FROM jobs WHERE {where}", params):
        for t in json.loads(tags_json or "[]"):
            tag_counts[t] = tag_counts.get(t, 0) + 1
    out["tag"] = [
        {"value": t, "count": n}
        for t, n in sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:60]
    ]
    return out


def stats(conn: sqlite3.Connection) -> dict[str, Any]:
    """Overall numbers for the UI header."""
    total = conn.execute("SELECT COUNT(*) FROM jobs WHERE active=1").fetchone()[0]
    last = conn.execute(
        "SELECT MAX(finished_at) FROM runs WHERE finished_at IS NOT NULL"
    ).fetchone()[0]
    runs = conn.execute(
        "SELECT source, MAX(finished_at) AS finished_at, collected, error FROM runs "
        "GROUP BY source ORDER BY source"
    ).fetchall()
    return {
        "total_active": total,
        "last_run": last,
        "runs": [dict(r) for r in runs],
    }
