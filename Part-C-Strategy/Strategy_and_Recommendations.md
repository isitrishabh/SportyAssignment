# Part C: Strategy & Recommendations

## 1. Why these 2 tests for automation

These were chosen over the other candidates in the test plan (insufficient balance, duplicate submission/Rebet, upcoming-only eligibility, filters) for three reasons:

- **Coverage per test.** The UI test covers selection, quoted payout, receipt fields, backend deduction, displayed balance, and slip cleanup in one journey. Soft assertions collect the known receipt and balance discrepancies (BUG-03, BUG-05, and BUG-07) together, provided the earlier hard assertions pass. The API test is parametrized across six boundary and type values in one function, giving broad validation coverage within the two-test budget.
- **Layer separation proves a real gap.** Running the same boundary values through both the UI and the API in the manual pass showed the UI blocks invalid stakes correctly while the API does not (BUG-01: negative stake). An API-only automated test demonstrates that this control must live server-side and would catch a regression even if the UI were rewritten or bypassed.
- **Stability vs. the other candidates.** Duplicate-submission and Rebet UI scenarios need controlled timing or forced network failures to be repeatable. Filters are lower financial risk. Insufficient-balance testing protects a distinct business rule, but was deferred within the two-test budget in favor of demonstrating the UI/API validation gap. The chosen pair balances financial risk, coverage, and implementation cost.

## 2. What was intentionally left manual-only

| Duplicate submission / `Rebet` retry (BUG-06) | Needs precise timing (clicking before the button disables) or request interception to force a 500. Worth automating next, but higher setup cost than the first two tests for a 2-test budget. |
| Insufficient balance, including the exact-balance boundary | Requires controlled starting balances to distinguish a valid stake from an unaffordable one. This is a separate financial-integrity rule and a high-priority next API test. |
| Upcoming-only eligibility (BUG-04) | Needs fixtures on both sides of the eligibility cutoff. The current `upcoming_match` fixture skips dependent tests when no future match remains, so fixed catalogue dates can remove coverage over time. Seeded date-relative fixtures and an agreed cutoff/timezone are needed for repeatable checks. |
| Error modal, `Close`/`X`, `Remove All` | Pure UI state, lower financial risk, and partially exercised already (closing the receipt clears the slip in the UI test). |
| Filters (date range, odds range, inclusive boundaries) | No money moves; defects here affect discovery, not correctness of a placed bet. Good next candidates once the two highest-risk tests are in place. |
| Layout / fixed right-side slip, visual design | Out of scope for functional automation; needs visual or layout-specific tooling. |

The guiding rule: automate what protects money and data integrity first; state-dependent UI polish and discovery features wait.

## 3. Recommendations if this project scaled

The following three recommendations are ordered by implementation priority. They extend the current framework rather than requiring a rewrite.

1. **Establish a CI feedback loop with useful failure evidence.** Run `python -m pytest -m api` on each push or pull request, and `python -m pytest -m ui` with `HEADLESS=true` before merge; use a scheduled run for broader browser coverage as the suite grows. Install dependencies from the existing requirements file and supply `BASE_URL` and `USER_ID` through CI configuration (see [config/settings.py](../PART-B-Automation/config/settings.py)). Use a dedicated test environment. Until user isolation is available, serialize API and UI runs, including overlapping pipelines that share the same account. Publish pytest-html, Allure results, and UI failure screenshots even when tests fail. Give separate test invocations distinct report directories: the current defaults overwrite the HTML report and clear previous Allure results. Keep known product failures visible and linked to defects; do not use blanket retries or ignored exit codes to obtain a green build. **Success criterion:** every failed CI run retains diagnostic artifacts, and unresolved financial-integrity failures prevent release.

2. **Make test data deterministic before enabling parallel execution.** The autouse fixture resets the balance, but all tests still use one account, so concurrent resets and bets can interfere with each other. Introduce disposable users or an exclusively leased account per worker, with controlled balances and cleanup in an isolated test environment.

3. **Agree financial rules, then expand API-first coverage and contracts.** Confirm the minimum stake (1.00 versus 1.01), currency precision and payout rounding, match eligibility cutoff, and retry/idempotency behavior with the product and backend owners. Turn those decisions into explicit expected results. Prioritize insufficient/exact-balance boundaries, past-match rejection, and duplicate requests, asserting both the response and the resulting balance or bet records. Use controlled network failures for UI retry and error-state tests rather than relying on click timing. Adopt an agreed OpenAPI or JSON Schema contract if one is not already available, and validate success and error response structures in CI. Schema validation detects structural drift; it does not prove correct deductions, payouts, or duplicate protection, which need behavioral assertions. **Success criterion:** every agreed financial rule has a repeatable regression check, and rejected or duplicate operations cannot alter balances or create unintended bets.
