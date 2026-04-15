"""Run all Res-GeoAI tests; saved_models/ weights are loaded where present."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def run_module(module_path: str, module_name: str):
    # Import and execute a test module, reporting pass/fail summary
    import importlib.util
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        print(f"\n{'='*50}")
        print(f"[SUITE DONE] {module_name}")
    except Exception as e:
        print(f"\n[SUITE ERROR] {module_name}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Discover and run all test_*.py files in this directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = sorted([
        f for f in os.listdir(test_dir)
        if f.startswith("test_") and f.endswith(".py")
    ])

    print("=" * 60)
    print("  Res-GeoAI Test Suite")
    print("  Note: Tests calling saved_models/ skip if weights absent")
    print("=" * 60)

    for fname in test_files:
        fpath = os.path.join(test_dir, fname)
        module_name = fname.replace(".py", "")
        print(f"\n>>> Running: {fname}")
        run_module(fpath, module_name)

    print("\n" + "=" * 60)
    print("  All test suites completed.")
    print("=" * 60)
