"""API test for stake validation rules (spec section 4.1)."""
import pytest

INVALID_STAKES = [
    pytest.param(0, "invalid_stake_min", id="zero"),
    pytest.param(0.99, "invalid_stake_min", id="just-below-minimum"),
    pytest.param(-5, "invalid_stake_min", id="negative"),
    pytest.param(100.01, "invalid_stake_max", id="just-above-maximum"),
    pytest.param(10.123, "invalid_stake_precision", id="three-decimals"),
    pytest.param("abc", "invalid_stake_type", id="non-numeric"),
]


@pytest.mark.api
@pytest.mark.parametrize("stake, expected_error", INVALID_STAKES)
def test_invalid_stake_is_rejected_and_balance_is_untouched(api_client, upcoming_match, stake, expected_error):
    """Why this test: stake limits are the operator's main financial control and the spec
    requires them in the API, not just the UI. A UI-only check can be bypassed, so each boundary
    and malformed value is sent directly. Asserting the balance is unchanged proves a rejected
    bet has no side effects, which matters most for the negative-stake case (it must not credit money).
    """
    balance_before = api_client.get_balance()

    response = api_client.place_bet(upcoming_match["id"], "HOME", stake)

    assert response.status_code == 422, f"Expected 422 for stake {stake!r}, got {response.status_code}: {response.text}"
    assert response.json()["error"] == expected_error
    assert api_client.get_balance() == balance_before, "A rejected bet must not change the balance"
