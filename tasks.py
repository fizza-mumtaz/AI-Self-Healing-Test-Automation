import sys
import subprocess
from pathlib import Path

TEST_PATH = "tests/e2e"

tasks = {
    "test": [TEST_PATH],
    "test:login": [f"{TEST_PATH}/test_login.py"],
    "test:healing": [f"{TEST_PATH}/test_healing.py"],
    "test:cross": [f"{TEST_PATH}/test_cross_website_healing.py"],
    "test:wrong": [
        f"{TEST_PATH}/test_cross_website_healing.py::test_gemini_rejects_wrong_locator"
    ],
    "test:report": [
        TEST_PATH,
        "--html=reports/test_report.html",
        "--self-contained-html",
    ],
}

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in tasks:
        print("Available commands:")
        for name in tasks:
            print(f"  python tasks.py {name}")
        sys.exit(1)

    command = sys.argv[1]

    if command == "test:report":
        Path("reports").mkdir(exist_ok=True)

    pytest_command = [
        sys.executable,
        "-m",
        "pytest",
        *tasks[command],
        "-m",
        "not live_api",
        "-v",
        "-s",
        "--durations=5",
    ]

    sys.exit(subprocess.run(pytest_command).returncode)


if __name__ == "__main__":
    main()