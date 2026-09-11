"""CLI: collect jobs from every source and store them in SQLite.

Examples::

    python -m vagas_br.scrape                       # core sources, default queries
    python -m vagas_br.scrape -s gupy,linkedin -p 3 # fewer pages
    python -m vagas_br.scrape -s all                # include LLM sources (needs key)
    python -m vagas_br.scrape -q "engenheiro de dados" -q devops
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import UTC, datetime

from . import storage
from .normalize import enrich, is_tech_job
from .sources import ALL_SOURCES, build, make_client
from .sources.base import dedupe, log

DEFAULT_QUERIES: list[str] = [
    "desenvolvedor",
    "developer",
    "programador",
    "engenheiro de software",
    "software engineer",
    "backend",
    "frontend",
    "full stack",
    "mobile",
    "devops",
    "sre",
    "cloud",
    "dados",
    "data engineer",
    "cientista de dados",
    "machine learning",
    "qa",
    "analista de sistemas",
    "arquiteto de software",
    "analista de suporte",
    "infraestrutura",
    "segurança da informação",
    "tech lead",
    "product owner",
]


def run(
    sources: list[str],
    queries: list[str],
    max_pages: int,
    db_path: str | None = None,
    deactivate_days: int = 0,
    tech_only: bool = True,
) -> int:
    """Collect and persist jobs. Returns the number of jobs stored."""
    conn = storage.connect(db_path or storage.DEFAULT_DB)
    http = make_client()
    total = 0
    for src in build(sources):
        run_id = storage.start_run(conn, src.name)
        started = datetime.now(UTC).isoformat(timespec="seconds")
        t0 = time.time()
        collected: list = []
        skipped = 0
        error: str | None = None
        try:
            for job in src.collect(queries, max_pages, http):
                if tech_only and not is_tech_job(job.title):
                    skipped += 1
                    continue
                collected.append(enrich(job))
                if len(collected) % 200 == 0:
                    log.info("%s: %d jobs so far", src.name, len(collected))
        except KeyboardInterrupt:
            log.warning("%s: interrupted, saving partial results", src.name)
            error = "interrupted"
        except Exception as exc:  # noqa: BLE001 - keep other sources running
            log.exception("%s: failed", src.name)
            error = str(exc)
        jobs = dedupe(collected)
        n = storage.upsert_jobs(conn, jobs)
        if deactivate_days and not error:
            stale = storage.deactivate_stale(conn, src.name, started)
            if stale:
                log.info("%s: %d stale jobs deactivated", src.name, stale)
        storage.finish_run(conn, run_id, n, error)
        total += n
        log.info(
            "%s: %d jobs stored, %d non-tech skipped, %.0fs",
            src.name,
            n,
            skipped,
            time.time() - t0,
        )
        if error == "interrupted":
            break
    http.close()
    conn.close()
    return total


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-s",
        "--sources",
        default="core",
        help=f"comma list of sources or core/llm/all (options: {', '.join(ALL_SOURCES)})",
    )
    parser.add_argument(
        "-q",
        "--query",
        action="append",
        dest="queries",
        help="search term (repeatable). Default: built-in tech term list",
    )
    parser.add_argument(
        "-p", "--pages", type=int, default=5, help="max pages per query/source"
    )
    parser.add_argument(
        "--db", default=None, help="SQLite path (default vagas_br/data/vagas.db)"
    )
    parser.add_argument(
        "--deactivate",
        action="store_true",
        help="mark jobs of a source not seen in this run as inactive",
    )
    parser.add_argument(
        "--all-titles",
        action="store_true",
        help="keep every result; by default titles that do not look like tech roles are skipped",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    queries = args.queries or DEFAULT_QUERIES
    n = run(
        args.sources.split(","),
        queries,
        args.pages,
        args.db,
        deactivate_days=1 if args.deactivate else 0,
        tech_only=not args.all_titles,
    )
    print(f"{n} vagas armazenadas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
