"""Run tests and capture output."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, '-m', 'pytest', 'tests/test_auth_integration.py', '-v', '--tb=short', '-x'],
    capture_output=True,
    text=True,
    cwd='.'
)

print("=== STDOUT ===")
print(result.stdout)
print("\n=== STDERR ===")
print(result.stderr)
print(f"\n=== Exit Code: {result.returncode} ===")
