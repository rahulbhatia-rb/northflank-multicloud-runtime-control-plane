import json
import sys
from pathlib import Path

from .validator import validate


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python -m northflank_control_plane.cli <spec.json>")
        return 2

    spec = json.loads(Path(sys.argv[1]).read_text())
    result = validate(spec)

    if result.ok:
        print("ALLOW: workload contract is production-ready")
        return 0

    print("DENY: workload contract needs changes")
    for message in result.messages:
        print(f"- {message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
