import argparse
from datetime import datetime

from sqlmodel import Session

from app.core.db import engine, init_db
from app.domain.jobs import collect_before_15_targets, collect_after_10_targets, sweep_defaults


def main():
    parser = argparse.ArgumentParser(description="Run scheduled booking jobs")
    parser.add_argument("--mode", choices=["before15", "after10", "defaults"], required=True)
    args = parser.parse_args()

    init_db()
    now = datetime.now()

    with Session(engine) as session:
        if args.mode == "before15":
            targets = collect_before_15_targets(session, now)
            print(f"before15 targets={len(targets)} users={[t.user_id for t in targets]}")
        elif args.mode == "after10":
            targets = collect_after_10_targets(session, now)
            print(f"after10 targets={len(targets)} users={[t.user_id for t in targets]}")
        elif args.mode == "defaults":
            affected = sweep_defaults(session, now)
            print(f"defaults affected={affected}")


if __name__ == "__main__":
    main()
