# Test Plan: Single Bet Placement

**Application:** https://qae-assignment-tau.vercel.app/?user-id=candidate-tynWiuDmY7AR
**Source:** Feature Specification: Single Bet Placement (all expected results come from the spec)
**Scope:** Desktop web, football pre-match, single bet only. Live betting, accumulators, other sports and mobile are out of scope.

## Approach
Money correctness comes first (stake, balance, payout), then bet integrity (duplicate or failed submissions, request validation), then discovery features (filters and eligibility). The spec defines UI and API rules separately, so validation scenarios check both layers and compare them.

## Spec points that need clarification

- **Minimum stake:** Section 3 and the UI copy say €1.00, but the validation table (4.1) says €1.01. These tests treat €1.00 as valid (the OpenAPI `minimum: 1` agrees) and flag the conflict.
- **Payout rounding:** no rule is given, so expected payouts use stakes with exact results.
- **Failure trigger:** the spec does not say what makes a bet fail. TC-04 forces a failure by overriding `POST /api/place-bet` to return 500.
- **Kickoff time:** the UI should show a date/time label, but the API returns only `kickoffDate`.
- **Test data:** re-read `GET /api/balance` after any reset or bet and treat it as the source of truth. Upcoming match used below: Inter vs Napoli (`serie-a-inter-napoli-2026-10-06`), odds 1 = 2.05, X = 3.35, 2 = 3.65.

## Scenarios

### TC-01: Validate placement of a valid single bet End to End
- **Priority:** Critical
- **Risk rationale:** This is the core feature, and it is where customers see their money. A wrong deduction, payout, or receipt value is a direct financial and trust problem. The scenario compares the match list, bet slip, receipt, displayed balance, and API response, so any inconsistency between them is caught. It also covers "selecting a new odds button replaces the previous selection".
- **Preconditions:** Reset the balance and record `GET /api/balance` as B.
- **Steps:**
  1. Open the app and confirm the header balance equals B.
  2. Click the `1` odds button of Inter vs Napoli, then click `X` of the same match.
  3. Check the bet slip, enter stake `10`, and check the potential payout.
  4. Click `Place Bet` and observe the button.
  5. Read the receipt, then close it.
  6. Compare the header and slip balance with `GET /api/balance`.
- **Expected result:**
  - After step 2 only one selection exists: `Draw`, odds 3.35. The first selection is replaced.
  - The slip shows the entered stake, the available balance, and a potential payout of €33.50 (10 × 3.35).
  - The button shows `Placing...` and then the flow ends in a success.
  - The receipt shows Bet ID, match (`Inter vs Napoli`), selection (Draw), stake €10.00, odds at placement 3.35, potential payout €33.50, and a placement timestamp.
  - The stake is deducted: the displayed balance and `GET /api/balance` both equal B − 10.00.
  - After closing the receipt, the slip has no active selection.
  - The place-bet API response is consistent with the receipt (`odds` 3.35, `payout` 33.5, `currency` EUR).

### TC-02: Validate Stake limits and the precision
- **Priority:** Critical
- **Risk rationale:** Stake rules protect both the user and the operator. Boundaries (minimum, maximum), precision, and type are where validation most often breaks, and the spec requires the rules in both the UI and the API. A UI-only check can be bypassed, so every value is tested on both layers and the results are compared. Negative and zero stakes are included because they have the most severe effect on the balance.
- **Preconditions:** Balance of at least €110. An upcoming match is selected for the UI steps.
- **Steps:**
  1. In the UI, enter each stake and note the message and the `Place Bet` state: `-5`, `0`, `0.99`, `1.00`, `1.01`, `100.00`, `100.01`, `10.123`, `abc`, `1.2.3`, and empty.
  2. Send the same values to `POST /api/place-bet` (also `"10"` as a string, and a body without `stake`).
  3. Call `GET /api/balance` after each API call.
- **Expected result:**
  - UI: `-5`, `0` and `0.99` show "Minimum stake is €1.00". `100.01` shows "Maximum stake is €100.00". `Place Bet` is blocked for these and for an empty stake. The field accepts only numeric input with one decimal separator and at most 2 decimals. `1.00`, `1.01` and `100.00` are accepted.
  - API: `-5`, `0` and `0.99` are rejected as below minimum, `100.01` as above maximum, `10.123` as invalid precision, and `"abc"`, `"10"` and a missing stake as invalid type. All of these use a 422 response. `1.00`, `1.01` and `100.00` return 200.
  - The balance changes only for accepted bets and never increases because of a bet.
  - UI and API give the same verdict for every value.

### TC-03: Stake should not exceed available balance
- **Priority:** Critical
- **Risk rationale:** Letting a user bet more than they hold creates a negative balance and unrecoverable exposure for the operator. The spec requires the rule in both the UI and the API, and the API is the real control. The exact-balance boundary is included because "stake equal to balance" is a common off-by-one.
- **Preconditions:** Reduce the balance to a known value B below €100 (for example, place a €100 bet from a €120 balance, so B = 20).
- **Steps:**
  1. In the UI, select a match and enter stake `B + 0.01`.
  2. Enter stake `B` and place the bet.
  3. With the balance at `0.00`, send `POST /api/place-bet` with stake `1.00`.
  4. Reset to a balance B, then send `POST /api/place-bet` with stake `B + 0.01`.
  5. Call `GET /api/balance` after each step.
- **Expected result:**
  - Step 1: "Insufficient balance" is shown and placement is blocked.
  - Step 2: the bet is accepted and the balance becomes €0.00.
  - Steps 3 and 4: the API rejects the request, no bet is created, and the balance is unchanged.
  - The balance never goes below zero.

### TC-04: In-progress state, duplicate submission, failure and Rebet
- **Priority:** High
- **Risk rationale:** The spec requires an in-progress state that resolves to exactly one final outcome, and it forbids a second concurrent bet for the same user (409). Rapid clicks and the `Rebet` retry both submit again, so they carry a risk of charging the user twice for one intent. Failure handling also decides whether the user ends in a clean or stale state (selection, stake, balance).
- **Preconditions:** Balance B of at least €10. Inter vs Napoli `1` selected with stake `1`.
- **Steps:**
  1. Click `Place Bet` three times quickly and record the `POST /api/place-bet` requests.
  2. Close any dialogs and compare `GET /api/balance` with B.
  3. Select a match again with stake `5`. Override `POST /api/place-bet` to return 500 and click `Place Bet`.
  4. Check the error modal and the balance.
  5. Remove the override and click `Rebet`. Record the requests and the balance.
  6. Repeat step 3 and click `Close`. Repeat again and click the top-right `X`.
- **Expected result:**
  - Step 1: the button enters `Placing...` and cannot be triggered again. Exactly one request is sent and one outcome is shown.
  - Step 2: the balance is B − 1.00 and one receipt exists.
  - Step 4: the modal title is "Something went wrong", the body says the bet could not be processed and suggests trying again, and the balance is unchanged.
  - Step 5: `Rebet` closes the modal and retries once with the same data. The balance drops by exactly €5.00 and one receipt appears.
  - Step 6: `Close` and `X` close the modal and clear the selection and stake. The balance is unchanged.

### TC-05: API request validation (auth, payload, match, selection)
- **Priority:** High
- **Risk rationale:** The API is the enforcement point for every rule the UI shows, and it can be called without the UI. The spec lists specific error classes (400, 401, 405, 422), so wrong status codes or accepted bad input weaken monitoring and security. Missing user context is the only authentication in the system and must never be skipped.
- **Preconditions:** A valid `x-user-id`. Balance of at least €10.
- **Steps:**
  1. Call `GET /api/balance` and `POST /api/place-bet` without `x-user-id`, and with a blank one.
  2. Send `POST /api/place-bet` with body `{bad` and with `[1]`.
  3. Send `GET /api/place-bet` and `POST /api/balance`.
  4. Send valid bets with a missing, blank and unknown `matchId`.
  5. Send valid bets with `selection` missing, `home` (lowercase), and `WIN`.
  6. Send a valid bet with an extra field (`"foo":"bar"`).
  7. Call `GET /api/balance` after the set.
- **Expected result:**
  - Step 1: 401 for every call.
  - Step 2: 400 for malformed JSON and for a non-object body.
  - Step 3: 405 for both unsupported methods.
  - Steps 4 and 5: 422 for each invalid `matchId` or `selection`.
  - Step 6: the extra field is ignored and the bet succeeds (200).
  - The balance only changes for the one valid bet.

### TC-06: Upcoming-only events and filters
- **Priority:** High
- **Risk rationale:** The spec allows bets on upcoming matches only, and requires inclusive date and odds ranges with clear feedback on an invalid odds range. These do not move money directly, but a past match that can still be bet on is a business-rule violation, and filters decide which bets a user can find. Exact boundary values (the range ends themselves) expose off-by-one errors that mid-range values miss.
- **Preconditions:** Page loaded with no filters. Use `GET /api/matches` to compute the expected result for each filter (a match counts if any of its home/draw/away odds is in the range). App date is today date.
- **Steps:**
  1. Scroll the "Upcoming Football Matches" list and note any match marked `PAST`. Try to select its odds and place a bet (also via the API with its `matchId`).
  2. Open the odds filter, set MIN `5.00` and MAX `2.00`, and click `Apply`.
  3. Set MIN `2.00` and MAX `2.10` and click `Apply`. Compare the shown matches with the expected list, looking at matches with odds exactly 2.00 and 2.10.
  4. Open the date filter (Custom) and select a single day, then apply.
  5. Select the date range and apply. Then select the end date first.
  6. At each step, compare the "Showing N matches" text with the number of cards.
- **Expected result:**
  - Step 1: only upcoming matches are listed and bettable. A bet on a past match is blocked in the UI and rejected by the API, with the balance unchanged.
  - Step 2: the range is rejected with a clear message and is not applied as MIN cannot be more than MAX
  - Step 3: every match with odds from 2.00 to 2.10, boundaries included, is shown, with none missing or extra.
  - Step 4: only matches on that specific date appear.
  - Step 5: matches on date range selected (both end days included) appear, and the reversed selection gives the same range.
  - Step 6: the count equals the number of cards in every step.
