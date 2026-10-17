"""Apply SQL migrations in filename order."""
import os
from pathlib import Path
import time

import psycopg


def main():
    database_url = os.environ.get("DATABASE_URL", "")
    migrations = sorted(Path(__file__).parent.parent.joinpath("migrations").glob("*.sql"))

    for attempt in range(30):
        try:
            with psycopg.connect(database_url) as conn:
                for migration in migrations:
                    print("Applying %s" % migration.name, flush=True)
                    conn.execute(migration.read_text(encoding="utf-8"), prepare=False)
            return
        except psycopg.OperationalError:
            if attempt == 29:
                raise
            time.sleep(2)


if __name__ == "__main__":
    main()
