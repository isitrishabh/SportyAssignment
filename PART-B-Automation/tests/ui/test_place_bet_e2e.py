"""E2E UI test for the core betting journey."""
from decimal import Decimal

import pytest

from utils.money import potential_payout, to_decimal


@pytest.mark.ui
def test_user_places_single_bet_and_receives_correct_receipt(api_client, betting_page, upcoming_match, soft):
    """Why this test: placing a bet is the product's core revenue flow and the point where
    money moves. One journey checks that what the user is quoted (slip), what they are given
    (receipt) and what the system stores (backend balance) all agree, which is where most
    high-impact defects live. The backend balance is the source of truth, not the UI.
    """
    stake = Decimal("10.00")
    odds = to_decimal(upcoming_match["odds"]["home"])
    expected_payout = potential_payout(stake, odds)
    balance_before = api_client.get_balance()

    betting_page.open()
    betting_page.match_list.select_outcome(upcoming_match["id"], "home")
    assert betting_page.bet_slip.selection_count() == 1

    betting_page.bet_slip.enter_stake(stake)
    assert betting_page.bet_slip.potential_payout() == expected_payout
    betting_page.bet_slip.place_bet()

    receipt = betting_page.receipt
    receipt.wait_until_displayed()
    assert receipt.bet_id, "Receipt must show a Bet ID"
    assert receipt.stake == stake
    assert receipt.odds == odds
    assert api_client.get_balance() == balance_before - stake, "Backend must deduct exactly the stake"

    # Remaining receipt and display checks are soft so one run reports every discrepancy.
    expected_match = f"{upcoming_match['homeTeam']} vs {upcoming_match['awayTeam']}"
    soft.check_equal(receipt.payout, expected_payout, "Receipt potential payout (stake x odds) [BUG-03]")
    soft.check_equal(receipt.match, expected_match, "Receipt match details [BUG-07]")
    soft.check(bool(receipt.placed_at), "Receipt must show a placement timestamp")
    soft.check(
        betting_page.wait_for_balance(balance_before - stake),
        f"Displayed balance did not update to {balance_before - stake} after the bet [BUG-05]",
    )

    receipt.close()
    assert betting_page.bet_slip.wait_until_empty(), "Closing the receipt must clear the selection"
    soft.assert_all()
