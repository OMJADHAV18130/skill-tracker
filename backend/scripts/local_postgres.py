"""Start a local PostgreSQL server without Docker.

Docker is the recommended way to run PostgreSQL (``docker compose up -d db``),
but on machines where Docker is not installed this script starts a bundled
PostgreSQL 16 server via the ``pgserver`` package instead.

Usage
-----
    python -m scripts.local_postgres          # start and print the DATABASE_URL
    python -m scripts.local_postgres --stop   # stop a running server

The data directory is stored in ``backend/.pgdata`` so the database survives
restarts.
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

BACKEND_ROOT = pathlib.Path(__file__).resolve().parent.parent
PGDATA = BACKEND_ROOT / ".pgdata"
ROLE = "devpath"
PASSWORD = "devpath"
DATABASE = "devpath"


def _run(server, statement: str) -> str:
    """Run a single SQL statement, tolerating errors."""
    try:
        return server.psql(statement)
    except subprocess.CalledProcessError as exc:  # pragma: no cover
        return (exc.output or b"").decode("utf-8", errors="replace")


def start() -> str:
    try:
        import pgserver
    except ImportError:  # pragma: no cover
        print(
            "pgserver is not installed. Install the dev dependencies with:\n"
            "    pip install -e .[dev]\n"
            "or start PostgreSQL with: docker compose up -d db",
            file=sys.stderr,
        )
        raise SystemExit(2) from None

    PGDATA.mkdir(parents=True, exist_ok=True)
    # cleanup_mode=None keeps the server running after this process exits so
    # that the API, the tests and psql can all connect to it.
    server = pgserver.get_server(PGDATA, cleanup_mode=None)
    uri = server.get_uri()  # postgresql://postgres:@127.0.0.1:<port>/postgres

    # --- application role --------------------------------------------------
    _run(
        server,
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{ROLE}') THEN
                CREATE ROLE {ROLE} LOGIN PASSWORD '{PASSWORD}' CREATEDB;
            ELSE
                ALTER ROLE {ROLE} WITH LOGIN PASSWORD '{PASSWORD}' CREATEDB;
            END IF;
        END
        $$;
        """,
    )

    # --- application database ---------------------------------------------
    exists = server.psql(
        f"SELECT 1 FROM pg_database WHERE datname = '{DATABASE}'"
    )
    if "(0 rows)" in exists or not exists.strip():
        _run(server, f"CREATE DATABASE {DATABASE} OWNER {ROLE}")

    host = uri.split("@", 1)[1].split("/", 1)[0]
    hostname, _, port = host.partition(":")
    return f"postgresql+psycopg://{ROLE}:{PASSWORD}@{hostname}:{port}/{DATABASE}"


def stop() -> None:
    import pgserver

    pgserver.get_server(PGDATA, cleanup_mode=None).cleanup()
    print("Local PostgreSQL stopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stop", action="store_true", help="Stop the local server")
    args = parser.parse_args()

    if args.stop:
        stop()
        return

    url = start()
    env_file = BACKEND_ROOT / ".env.local"
    env_file.write_text(f"DATABASE_URL={url}\n", encoding="utf-8")
    print(url)
    print(f"\nWritten to {env_file}. Use it with:")
    print(f'    $env:DATABASE_URL="{url}"')


if __name__ == "__main__":
    main()
