from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

def _configure_stdio() -> None:
    """
    Windows PowerShell에서 콘솔 코드페이지/인코딩 불일치로 한글이 깨지거나
    특수문자 출력이 실패(UnicodeEncodeError)할 수 있어, 콘솔을 UTF-8로 맞춥니다.
    (프로세스 내부에서만 best-effort로 적용)
    """

    if sys.platform == "win32":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            # 65001 = UTF-8 code page
            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)
        except Exception:
            pass

    for s in (sys.stdout, sys.stderr):
        if s is None:
            continue
        reconfigure = getattr(s, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _repo_root() -> Path:
    # tools/devlog.py -> repo root is parent of tools/
    return Path(__file__).resolve().parents[1]


def _devlog_dir(root: Path) -> Path:
    return root / "devlog"


def _state_path(root: Path) -> Path:
    return _devlog_dir(root) / "state.json"


def _log_path(root: Path) -> Path:
    return _devlog_dir(root) / "DEVELOPMENT_LOG.md"


def _context_path(root: Path) -> Path:
    # This is the file the next cycle should read first.
    return _devlog_dir(root) / "CONTEXT.md"


def _today_iso() -> str:
    return date.today().isoformat()


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _normalize_state(state: dict) -> dict:
    # Backward compatible defaults
    if "enforce_context_before_start" not in state:
        state["enforce_context_before_start"] = True
    if "context_generated_at" not in state:
        state["context_generated_at"] = None
    if "context_from_log_mtime_ns" not in state:
        state["context_from_log_mtime_ns"] = None
    return state


def read_state(root: Path) -> dict:
    p = _state_path(root)
    if not p.exists():
        raise FileNotFoundError(f"state file not found: {p}")
    return _normalize_state(json.loads(p.read_text(encoding="utf-8")))


def write_state(root: Path, state: dict) -> None:
    p = _state_path(root)
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


_CURRENT_STATUS_RE = re.compile(
    r"(^## 현재 상태\s*$)(?P<body>[\s\S]*?)(^\s*##\s)",
    re.MULTILINE,
)


def _render_current_status_block(step: int, status: str, last_updated: str) -> str:
    return (
        "## 현재 상태\n\n"
        f"- **현재 Step**: {step}\n"
        f"- **상태**: {status}\n"
        f"- **마지막 업데이트**: {last_updated}\n\n"
    )


def update_log_current_status(root: Path, *, step: int, status: str, last_updated: str) -> None:
    p = _log_path(root)
    if not p.exists():
        raise FileNotFoundError(f"development log not found: {p}")

    text = p.read_text(encoding="utf-8")
    m = _CURRENT_STATUS_RE.search(text)
    if not m:
        raise ValueError("could not locate '## 현재 상태' block in DEVELOPMENT_LOG.md")

    replacement = _render_current_status_block(step=step, status=status, last_updated=last_updated)
    new_text = _CURRENT_STATUS_RE.sub(replacement + "## ", text, count=1)
    p.write_text(new_text, encoding="utf-8")


def cmd_status(root: Path) -> int:
    state = read_state(root)
    log = _log_path(root)
    ctx = _context_path(root)
    print(f"current_step: {state.get('current_step')}")
    print(f"status: {state.get('status')}")
    print(f"last_updated: {state.get('last_updated')}")
    print(f"enforce_context_before_start: {state.get('enforce_context_before_start')}")
    print(f"context_generated_at: {state.get('context_generated_at')}")
    print(f"context_from_log_mtime_ns: {state.get('context_from_log_mtime_ns')}")
    print(f"log: {log}")
    print(f"context: {ctx}")
    return 0


def cmd_load(root: Path, *, stdout: bool) -> int:
    state = read_state(root)
    log = _log_path(root)
    if not log.exists():
        raise FileNotFoundError(f"development log not found: {log}")
    text = log.read_text(encoding="utf-8")
    ctx = _context_path(root)
    ctx.write_text(text, encoding="utf-8")
    state["context_generated_at"] = _now_iso()
    state["context_from_log_mtime_ns"] = log.stat().st_mtime_ns
    write_state(root, state)
    print(f"wrote: {ctx}")
    if stdout:
        sys.stdout.write(text)
    return 0


def _is_context_fresh(root: Path, state: dict) -> bool:
    log = _log_path(root)
    try:
        current_mtime = log.stat().st_mtime_ns
    except FileNotFoundError:
        return False
    return state.get("context_from_log_mtime_ns") == current_mtime


def cmd_check(root: Path) -> int:
    state = read_state(root)
    if _is_context_fresh(root, state):
        print("ok: context is fresh (CONTEXT.md matches current DEVELOPMENT_LOG.md)")
        return 0
    print("stale: run `python tools/devlog.py load` before starting the next step")
    return 2


def cmd_start(root: Path, step: int) -> int:
    state = read_state(root)
    if state.get("enforce_context_before_start") and not _is_context_fresh(root, state):
        raise ValueError("context is stale: run `python tools/devlog.py load` first")
    state["current_step"] = step
    state["status"] = "in_progress"
    state["last_updated"] = _today_iso()
    write_state(root, state)
    update_log_current_status(root, step=step, status="in_progress", last_updated=state["last_updated"])
    return 0


def cmd_complete(root: Path, step: int) -> int:
    state = read_state(root)
    current = int(state.get("current_step"))
    if step != current:
        raise ValueError(f"can only complete current_step={current} (requested: {step})")
    state["status"] = "completed"
    state["last_updated"] = _today_iso()
    write_state(root, state)
    update_log_current_status(root, step=step, status="completed", last_updated=state["last_updated"])
    return 0


def cmd_next(root: Path) -> int:
    state = read_state(root)
    if state.get("status") != "completed":
        raise ValueError("current step is not completed; complete it before running next")
    next_step = int(state.get("current_step")) + 1
    cmd_load(root, stdout=False)
    cmd_start(root, next_step)
    print(f"started: step {next_step}")
    return 0


def cmd_enforce(root: Path, mode: str) -> int:
    state = read_state(root)
    if mode not in {"on", "off"}:
        raise ValueError("mode must be 'on' or 'off'")
    state["enforce_context_before_start"] = mode == "on"
    write_state(root, state)
    print(f"enforce_context_before_start: {state['enforce_context_before_start']}")
    return 0


def cmd_validate(root: Path) -> int:
    state = read_state(root)
    # Minimal validation: files exist & keys present
    required = {"current_step", "status", "last_updated", "source_of_truth"}
    missing = sorted(required - set(state.keys()))
    if missing:
        raise ValueError(f"state.json missing keys: {', '.join(missing)}")
    if not _log_path(root).exists():
        raise FileNotFoundError("DEVELOPMENT_LOG.md not found")
    print("ok")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="devlog",
        description="Structured development log helper (status/load/check/start/complete/next/enforce/validate).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Print current step/status.")
    s_load = sub.add_parser("load", help="Write CONTEXT.md from DEVELOPMENT_LOG.md (for context reset).")
    s_load.add_argument("--stdout", action="store_true", help="Also print the log to stdout.")
    sub.add_parser("check", help="Check whether CONTEXT.md is fresh for starting a step.")

    s_start = sub.add_parser("start", help="Start a step (updates state + log header).")
    s_start.add_argument("step", type=int)

    s_complete = sub.add_parser("complete", help="Complete the current step (updates state + log header).")
    s_complete.add_argument("step", type=int)

    sub.add_parser("next", help="Run load and start the next step (current must be completed).")

    s_enforce = sub.add_parser("enforce", help="Toggle enforcing context load before start.")
    s_enforce.add_argument("mode", choices=["on", "off"])

    sub.add_parser("validate", help="Validate state/log presence and minimal shape.")
    return p


def main(argv: list[str]) -> int:
    _configure_stdio()
    root = _repo_root()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "status":
        return cmd_status(root)
    if args.cmd == "load":
        return cmd_load(root, stdout=bool(getattr(args, "stdout", False)))
    if args.cmd == "check":
        return cmd_check(root)
    if args.cmd == "start":
        return cmd_start(root, args.step)
    if args.cmd == "complete":
        return cmd_complete(root, args.step)
    if args.cmd == "next":
        return cmd_next(root)
    if args.cmd == "enforce":
        return cmd_enforce(root, args.mode)
    if args.cmd == "validate":
        return cmd_validate(root)

    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

