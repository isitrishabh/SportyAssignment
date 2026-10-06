# Sports Betting QA Automation

Selenium + Pytest (UI) and `requests` (API) automation for the *Single Bet Placement* feature of
https://qae-assignment-tau.vercel.app.

## Requirements

- Python 3.10 or newer (tested on 3.14)
- Latest desktop Google Chrome (Selenium Manager downloads the matching driver automatically)

## Setup

Open a terminal in this folder (`PART-B-Automation`) and run these commands one by one:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

- Step 1 creates a `.venv` folder (only needed once).
- Step 2 installs Selenium, Pytest and requests into it.

## Run

Always call pytest through the venv's own Python, using the exact commands below. This works in
any terminal without activating anything first, and avoids accidentally running a different
`pytest` that may be on your system `PATH`:

```powershell
.\.venv\Scripts\python.exe -m pytest                 # run everything
.\.venv\Scripts\python.exe -m pytest -m api          # API tests only (fast, no browser)
.\.venv\Scripts\python.exe -m pytest -m ui           # the UI end-to-end test only
.\.venv\Scripts\python.exe -m pytest tests/api -v    # verbose output, one folder
```

If you prefer, activate the environment once per terminal with `.\.venv\Scripts\Activate.ps1`
(prompt starts with `(.venv)`) and then drop the `.\.venv\Scripts\python.exe -m` prefix. If
activation fails with a script-execution error, run
`Set-ExecutionPolicy -Scope Process RemoteSigned` first.

Tests run with a visible Chrome window by default. To run headless (no window, for example in CI):

```powershell
$env:HEADLESS = "true"
.\.venv\Scripts\python.exe -m pytest -m ui
```

### Troubleshooting

- **`pytest` is not found / runs the wrong tests / shows file paths from a different folder:**
  the environment was not activated, or a stale `__pycache__` was carried over from copying or
  renaming this project. Use the `.\.venv\Scripts\python.exe -m pytest` form above, and if the
  problem persists, delete the caches and retry:
  ```powershell
  Get-ChildItem -Recurse -Directory | Where-Object { $_.Name -eq '__pycache__' } | Remove-Item -Recurse -Force
  Remove-Item .pytest_cache -Recurse -Force -ErrorAction SilentlyContinue
  ```

### Configuration

All settings live in [config/settings.py](config/settings.py) and can be overridden by environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `BASE_URL` | `https://qae-assignment-tau.vercel.app` | Application under test |
| `USER_ID` | `candidate-tynWiuDmY7AR` | Sent as `x-user-id` (API) and `?user-id=` (UI). The backend rejects ids that are not in its expected format |
| `HEADLESS` | `false` | Set to `true` to run Chrome without a visible window |
| `UI_TIMEOUT` | `10` | Seconds for explicit Selenium waits |
| `API_TIMEOUT` | `10` | Seconds per HTTP request |

On a UI failure a screenshot is saved to `reports/screenshots/` and also attached to the reports.

## Reporting

Every run writes two reports automatically (configured in `pytest.ini`):

| Report | Location | Notes |
|---|---|---|
| pytest-html | `reports/report.html` | Single self-contained file, open in any browser |
| Allure results | `reports/allure-results/` | Raw data for the Allure dashboard (cleared on each run) |

Allure shows tests grouped by layer (UI / API), API steps with request and response bodies, and UI failures with a
screenshot and page source.

Open the pytest-html report (from `PART-B-Automation`):

```powershell
Invoke-Item reports/report.html
```

The Allure dashboard needs Java and Node.js (for `npx`). No separate install is required:

```powershell
npx --yes allure-commandline serve reports/allure-results                                       # open an interactive report
npx --yes allure-commandline generate reports/allure-results -o reports/allure-report --clean   # static report for CI
```

Run the tests first so `reports/allure-results` exists. `serve` keeps running until you press `Ctrl+C`.

## Project structure

```
PART-B-Automation/
├── conftest.py            # shared fixtures: API client, balance reset, upcoming match, soft asserts
├── pytest.ini             # test paths, markers (ui, api), strict markers
├── config/settings.py     # environment-driven configuration (no values hard-coded in tests)
├── api/betting_client.py  # API client: one method per endpoint
├── pages/
│   ├── base_page.py       # explicit-wait helpers shared by all page objects
│   ├── betting_page.py    # page object: navigation, header balance, composes components
│   └── components/        # match_list, bet_slip, receipt_modal
├── utils/                 # money helpers (Decimal), soft assertions
└── tests/
    ├── api/test_place_bet_validation.py
    └── ui/                # conftest.py (Chrome driver, screenshots), test_place_bet_e2e.py
```

### Design decisions

- **Page Object Model with components.** Locators and Selenium calls live only in `pages/`; tests read like the user
  journey. The bet slip, match list and receipt are separate components, so new areas (error modal, filters) are added
  as new files without touching existing ones.
- **API client separate from tests.** Tests call `api_client.place_bet(...)`, not `requests` directly. The same client
  provides test data and the backend source of truth for UI tests (balance, matches).
- **Independent tests.** An autouse fixture resets the balance before every test, and the upcoming match is read from
  the API, so tests do not depend on hard-coded fixtures or on each other.
- **Explicit waits only**, no `sleep`. Every locator is a stable element `id` exposed by the app.
- **Money as `Decimal`**, never `float`, so payout comparisons are exact.
- **Soft assertions** in the UI test. Steps the journey cannot continue without are hard asserts; independent
  display checks are collected and reported together at the end.
- **Fixtures over setup code.** Driver lifecycle and failure screenshots are handled in `tests/ui/conftest.py`.

## Tests and why they were chosen

| Test | Why |
|---|---|
| `tests/ui/test_place_bet_e2e.py` | Critical journey: select odds, enter stake, place bet, check the receipt, the backend deduction and the cleared slip. Money moves here, so slip, receipt and backend must agree. |
| `tests/api/test_place_bet_validation.py` | Business rule: stake limits and format are enforced by the API (parametrized: 0, 0.99, -5, 100.01, 3 decimals, non-numeric), and a rejected bet never changes the balance. A UI-only check can be bypassed. |

## Expected results on the current build

The tests assert the **specified** behaviour, so they fail where the application has known defects (details in
`Bug_Reports.md`). That is the intended outcome, not a framework problem:

| Failing check | Bug |
|---|---|
| API test, `negative` case: a stake of `-5` returns 200 and credits the balance | BUG-01 |
| UI test: receipt potential payout is `stake x 2` instead of `stake x odds` | BUG-03 |
| UI test: displayed balance is not updated after the bet | BUG-05 |
| UI test: receipt shows home and away teams swapped | BUG-07 |

The other five API cases pass. Once the defects are fixed, the same tests pass without any change.

## Limitations and next steps

- The `Placing...` loading state is not asserted, because it is too short-lived to check reliably without
  network interception.
- Not automated here: insufficient-balance rules, duplicate-submission protection, error modal / `Rebet`, filters.
  They need new page-object components (error modal, filters) and a way to force failures.
- The backend has a single configured user, so tests share state and cannot run in parallel. Parallel runs would
  need one user id per worker.
