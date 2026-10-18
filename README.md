# AI-Powered Self-Healing Test Automation Framework

A Python-based Web UI Test Automation Framework built with Playwright and Pytest. It combines conventional Page Object Model (POM) tests with **rule-based locator recovery** and an optional **Google Gemini fallback** when a Playwright locator stops matching an element.

The healing logic is independent of the website under test. The current suite demonstrates it on **SauceDemo** and **Expand Testing**.

## Features

- **Page Object Model:** Separates page actions, locators, and tests.
- **Rule-based locator recovery:** Compares candidate element attributes with a failed selector and applies confidence and target-matching checks.
- **Gemini-assisted fallback:** Requests a suggested CSS selector when rule-based recovery cannot find a suitable match.
- **Selector safety checks:** Checks uniqueness, visibility, enabled state, element type, DOM candidate evidence, and target-token alignment before accepting Gemini suggestions.
- **Click and fill recovery:** Supports self-healing for button/link interactions and text input actions.
- **Cross-website tests:** Reuses the same `LocatorHealer` implementation on two separate demo websites.
- **Failure screenshots:** Captures full-page screenshots for test-execution failures.
- **HTML reports:** Generates a self-contained pytest-html report with embedded failure screenshots.
- **Test shortcuts:** Provides reusable commands via `tasks.py`.



## Getting Started

Clone the repository and install dependencies:

```powershell
# 1. Clone the GitHub repository to your local machine.
git clone https://github.com/fizza-mumtaz/AI-Self-Healing-Test-Automation.git

# 2. Navigate to the project directory.
cd AI-Self-Healing-Test-Automation

# 3. Create a Python virtual environment.
python -m venv .venv

# 4. Activate the virtual environment (Windows PowerShell).
.\.venv\Scripts\Activate.ps1

# 5. Install the required Python dependencies.
python -m pip install -r requirements.txt

# 6. Install the Chromium browser for Playwright.
python -m playwright install chromium
```

Create a local environment file:

```powershell
Copy-Item .env.example .env
```

Set the demo-site credentials and URLs in `.env` using `.env.example` as a reference. A Gemini API key is needed only for the optional live API test. **Do not commit** `.env` **or API keys.**

## Run Tests

Run the commands from the project root:


| Command                        | Runs                                                |
| ------------------------------ | --------------------------------------------------- |
| `python tasks.py test`         | All E2E tests except the live Gemini API test       |
| `python tasks.py test:login`   | SauceDemo login tests                               |
| `python tasks.py test:healing` | SauceDemo healing tests (excluding live API)        |
| `python tasks.py test:cross`   | Cross-website healing tests                         |
| `python tasks.py test:wrong`   | Negative test for a wrong Gemini locator suggestion |
| `python tasks.py test:report`  | E2E suite plus an HTML report                       |


The task runner prints detailed output and the five slowest test durations. It excludes tests marked `live_api` by default.

To run the **optional real Gemini API test** explicitly:

```powershell
python -m pytest tests/e2e/test_healing.py -m live_api -v -s
```

The optional live API test requires a valid `GEMINI_API_KEY`, access to the configured model, and an active API connection. Execution is subject to API availability and usage limits.

## How Self-Healing Works

```text
Playwright action with original locator
                |
        Locator available?
          /           \
        Yes            No
         |              |
   Perform action    Rule-based candidate search
                        |
                Safe match found?
                   /          \
                 Yes           No
                  |             |
            Validate and    Gemini suggests CSS selector
            perform action         |
                              Validate against DOM,
                              target and action checks
                                    |
                           Accept or reject suggestion
```

**Example: rule-based input recovery**

```python
from healing.locatorHealer import LocatorHealer

healer = LocatorHealer(page)
healer.fillWithHealing("#username-old", "practice")
```

If `#username-old` is missing, the engine can identify the existing `#username` field and fill it if the recovery checks pass.

The fallback is deliberately conservative: an ambiguous, unrelated, hidden, disabled, or otherwise invalid suggestion can be rejected instead of interacting with the wrong element.

## Testing Strategy

**SauceDemo:** Login, product/cart, checkout, and healing tests for click and input actions.

**Expand Testing:** Cross-website tests for rule-based input recovery, mocked Gemini fallback, validation of a mocked Gemini suggestion through the real validation logic, and rejection of a wrong suggested field.

**Mocking vs. live Gemini:** Most Gemini-related tests mock the AI suggestion or fallback method. This makes the suite repeatable without real API calls. A separate `live_api`-marked test exercises the configured Gemini API when explicitly requested.

## HTML Reports and Failure Screenshots

Generate a report:

```powershell
python tasks.py test:report
```

Open it on Windows:

```powershell
start reports/test_report.html
```

For **test-execution failures**, `conftest.py` captures a full-page screenshot in `reports/screenshots/` and embeds it in the HTML test report. Screenshots are not generated for passing tests.

Reports and screenshots are generated locally and intentionally excluded from Git.

## Security Notes

- Credentials and API keys belong in `.env`, **not** in source files.
- Keep `.env` ignored by Git; commit only `.env.example` with placeholders.
- Gemini receives information about candidate page elements. Use appropriate care before running against applications that display sensitive or private data.



## Author

Developed by [fizza-mumtaz](https://github.com/fizza-mumtaz) as a software testing and automation portfolio project.