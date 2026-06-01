import importlib.util
import inspect
import sys
import traceback
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent


def load_module(path):
    module_name = path.stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def iter_test_functions():
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        module = load_module(path)

        for name, func in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("test_"):
                yield path.name, name, func


def main():
    total = 0
    failures = []

    for filename, name, func in iter_test_functions():
        total += 1

        try:
            func()
        except Exception:
            failures.append((filename, name, traceback.format_exc()))
            print(f"FAIL {filename}::{name}")
        else:
            print(f"PASS {filename}::{name}")

    print()
    print(f"Ran {total} tests: {total - len(failures)} passed, {len(failures)} failed")

    if failures:
        print()
        for filename, name, trace in failures:
            print(f"--- {filename}::{name} ---")
            print(trace.rstrip())

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
