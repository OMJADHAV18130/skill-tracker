"""Run a local PostgreSQL server on a fixed port - no Docker required.

This is a convenience script for machines without Docker Desktop. It uses the
PostgreSQL binaries that ship with the ``pgserver`` dev dependency (or a system
PostgreSQL install) and manages a data directory at ``backend/.pgdata``.

    python -m scripts.dev_db            # start (idempotent) and print the URL
    python -m scripts.dev_db --status   # show whether it is running
    python -m scripts.dev_db --stop     # stop it

The default port is 55432; override with ``DEVPATH_DB_PORT``.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import subprocess
import sys

BACKEND_ROOT = pathlib.Path(__file__).resolve().parent.parent
PGDATA = BACKEND_ROOT / ".pgdata"
LOGFILE = BACKEND_ROOT / ".pgdata-server.log"
ROLE = "devpath"
PASSWORD = "devpath"
DATABASE = "devpath"
PORT = int(os.environ.get("DEVPATH_DB_PORT", "55432"))
HOST = "127.0.0.1"


# ---------------------------------------------------------------------------
# Locate the PostgreSQL binaries
# ---------------------------------------------------------------------------
def find_bin_dir() -> pathlib.Path:
    for candidate in (
        BACKEND_ROOT / ".venv" / "Lib" / "site-packages" / "pgserver" / "pginstall" / "bin",
        pathlib.Path(sys.prefix) / "Lib" / "site-packages" / "pgserver" / "pginstall" / "bin",
    ):
        if (candidate / "initdb.exe").exists() or (candidate / "initdb").exists():
            return candidate

    for name in ("pg_ctl", "pg_ctl.exe"):
        found = shutil.which(name)
        if found:
            return pathlib.Path(found).parent

    for base in (
        pathlib.Path("C:/Program Files/PostgreSQL"),
        pathlib.Path("/usr/lib/postgresql"),
    ):
        if base.exists():
            for child in sorted(base.iterdir(), reverse=True):
                for bin_dir in (child / "bin", child):
                    if (bin_dir / "initdb.exe").exists() or (bin_dir / "initdb").exists():
                        return bin_dir

    raise SystemExit(
        "Could not find PostgreSQL binaries.\n"
        "Install the dev dependencies (pip install -e .[dev]) or use Docker:\n"
        "    docker compose up -d db"
    )


def _exe(bin_dir: pathlib.Path, name: str) -> str:
    candidate = bin_dir / (name + (".exe" if os.name == "nt" else ""))
    return str(candidate) if candidate.exists() else str(bin_dir / name)


def run(cmd: list[str], *, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        check=check,
        capture_output=capture,
        text=True,
        input=None,
    )


def initialise(bin_dir: pathlib.Path) -> None:
    if (PGDATA / "PG_VERSION").exists():
        return
    PGDATA.mkdir(parents=True, exist_ok=True)
    print(f"Initialising PostgreSQL data directory at {PGDATA} ...")
    result = run(
        [
            _exe(bin_dir, "initdb"),
            "-D",
            str(PGDATA),
            "-U",
            "postgres",
            "--auth=trust",
            "--encoding=UTF8",
            "--locale=C",
        ],
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit("initdb failed")

    # Pin the port so the connection URL never changes between restarts.
    conf = PGDATA / "postgresql.conf"
    with conf.open("a", encoding="utf-8") as handle:
        handle.write(
            f"\n# DevPath local development settings\n"
            f"port = {PORT}\n"
            f"listen_addresses = '{HOST}'\n"
            f"max_connections = 100\n"
        )


def is_running(bin_dir: pathlib.Path) -> bool:
    result = run([_exe(bin_dir, "pg_ctl"), "-D", str(PGDATA), "status"], check=False)
    return result.returncode == 0


def start(bin_dir: pathlib.Path) -> None:
    initialise(bin_dir)
    if is_running(bin_dir):
        _ensure_role_and_database(bin_dir)
        return
    print(f"Starting PostgreSQL on {HOST}:{PORT} ...")
    result = run(
        [
            _exe(bin_dir, "pg_ctl"),
            "-D",
            str(PGDATA),
            "-l",
            str(LOGFILE),
            "-o",
            f'-p {PORT} -h "{HOST}"',
            "-w",
            "-t",
            "60",
            "start",
        ],
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        if LOGFILE.exists():
            print(LOGFILE.read_text(encoding="utf-8", errors="replace")[-2000:])
        raise SystemExit("Could not start PostgreSQL")
    _ensure_role_and_database(bin_dir)


def stop(bin_dir: pathlib.Path) -> None:
    if not is_running(bin_dir):
        print("PostgreSQL is not running.")
        return
    run([_exe(bin_dir, "pg_ctl"), "-D", str(PGDATA), "-m", "fast", "stop"], check=False)
    print("PostgreSQL stopped.")


def psql(bin_dir: pathlib.Path, statement: str, *, database: str = "postgres") -> str:
    result = subprocess.run(
        [
            _exe(bin_dir, "psql"),
            "-h",
            HOST,
            "-p",
            str(PORT),
            "-U",
            "postgres",
            "-d",
            database,
            "-v",
            "ON_ERROR_STOP=0",
            "-tAc",
            statement,
        ],
        capture_output=True,
        text=True,
    )
    return (result.stdout or "") + (result.stderr or "")


def _ensure_role_and_database(bin_dir: pathlib.Path) -> None:
    psql(
        bin_dir,
        f"DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{ROLE}') "
        f"THEN CREATE ROLE {ROLE} LOGIN PASSWORD '{PASSWORD}' CREATEDB; "
        f"ELSE ALTER ROLE {ROLE} WITH LOGIN PASSWORD '{PASSWORD}' CREATEDB; END IF; END $$;",
    )
    exists = psql(bin_dir, f"SELECT 1 FROM pg_database WHERE datname = '{DATABASE}'").strip()
    if exists != "1":
        psql(bin_dir, f"CREATE DATABASE {DATABASE} OWNER {ROLE}")
    psql(bin_dir, f"ALTER DATABASE {DATABASE} OWNER TO {ROLE}")


def database_url() -> str:
    return f"postgresql+psycopg://{ROLE}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stop", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    bin_dir = find_bin_dir()

    if args.stop:
        stop(bin_dir)
        return
    if args.status:
        print("running" if is_running(bin_dir) else "stopped")
        return

    start(bin_dir)
    url = database_url()
    (BACKEND_ROOT / ".env.local").write_text(f"DATABASE_URL={url}\n", encoding="utf-8")
    print(f"\nPostgreSQL ready.\nDATABASE_URL={url}\n\nWritten to backend/.env.local")


if __name__ == "__main__":
    main()
