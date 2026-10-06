"""Fixtures shared by UI and API tests."""
from datetime import date

import allure
import pytest

from api.betting_client import BettingApiClient
from config.settings import settings
from utils.soft_assert import SoftAssertions


@pytest.fixture(scope="session")
def api_client() -> BettingApiClient:
    return BettingApiClient(settings.base_url, settings.user_id, settings.api_timeout)


@pytest.fixture(autouse=True)
def allure_labels(request) -> None:
    """Group results in the Allure report by test layer (ui / api)."""
    for layer in ("ui", "api"):
        if request.node.get_closest_marker(layer):
            allure.dynamic.epic(layer.upper())
            allure.dynamic.feature("Single Bet Placement")


@pytest.fixture(autouse=True)
def fresh_balance(api_client: BettingApiClient) -> None:
    """Start every test from the backend's initial balance so tests stay independent."""
    api_client.reset_balance()


@pytest.fixture(scope="session")
def upcoming_match(api_client: BettingApiClient) -> dict:
    """First match kicking off after today; avoids the stale 'PAST' fixtures in the catalogue."""
    today = date.today().isoformat()
    for match in api_client.get_matches():
        if match["kickoffDate"] > today:
            return match
    pytest.skip("No upcoming match available in the catalogue")


@pytest.fixture
def soft() -> SoftAssertions:
    return SoftAssertions()
