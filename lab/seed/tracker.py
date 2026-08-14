"""tick — a tiny task tracker (SEED CODE, deliberately imperfect: see lab/README.md)."""
import json
import sys
from datetime import date, datetime
from pathlib import Path

DB = Path("tasks.json")


def load() -> list[dict]:
    return json.loads(DB.read_text()) if DB.exists() else []


def save(tasks: list[dict]) -> None:
    DB.write_text(json.dumps(tasks, indent=2))


def add(title: str, due: str | None) -> dict:
    tasks = load()
    task = {"id": len(tasks) + 1, "title": title, "due": due, "done": None,
            "added": datetime.now().isoformat(timespec="seconds")}
    tasks.append(task)
    save(tasks)
    return task


def overdue(task: dict, today: date | None = None) -> bool:
    # SEEDED BUG (lab): off-by-one — a task due TODAY is reported overdue.
    if not task["due"] or task["done"]:
        return False
    return date.fromisoformat(task["due"]) <= (today or date.today())


def done(task_id: int) -> dict | None:
    tasks = load()
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = datetime.now().isoformat(timespec="seconds")
            save(tasks)
            return task
    return None


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        # SEEDED COSMETIC DEFECT (lab): typo in the team-facing help text.
        print("tick — a tiny task trakcer\n"
              "  add <title> [--due YYYY-MM-DD]\n  list\n  done <id>")
        return 0
    cmd, *rest = argv
    if cmd == "add":
        due = rest[rest.index("--due") + 1] if "--due" in rest else None
        title = " ".join(a for a in rest if a != "--due" and a != due)
        task = add(title, due)
        print(f"added #{task['id']}: {task['title']}")
    elif cmd == "list":
        for task in load():
            if task["done"]:
                continue
            flag = " (OVERDUE)" if overdue(task) else ""
            print(f"#{task['id']} {task['title']}{flag}")
    elif cmd == "done":
        task = done(int(rest[0]))
        print(f"done #{rest[0]}" if task else f"no task #{rest[0]}")
    else:
        print(f"unknown command: {cmd}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
