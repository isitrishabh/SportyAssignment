from decimal import Decimal

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.money import parse_amount


class BetSlip(BasePage):
    COUNT = (By.ID, "bet-slip-count")
    STAKE_INPUT = (By.ID, "bet-slip-stake-input")
    POTENTIAL_PAYOUT = (By.ID, "bet-slip-potential-payout")
    PLACE_BET_BUTTON = (By.ID, "bet-slip-place-bet")

    def selection_count(self) -> int:
        return int(self._text(self.COUNT))

    def enter_stake(self, stake: Decimal) -> None:
        self._type(self.STAKE_INPUT, str(stake))

    def potential_payout(self) -> Decimal:
        """Wait for the payout to be computed from the entered stake, then return it."""
        self._wait.until(lambda _: parse_amount(self._text(self.POTENTIAL_PAYOUT)) > 0)
        return parse_amount(self._text(self.POTENTIAL_PAYOUT))

    def place_bet(self) -> None:
        self._click(self.PLACE_BET_BUTTON)

    def wait_until_empty(self) -> bool:
        """True once the slip holds no selection (spec 2.4: closing the receipt clears it)."""
        return bool(self._wait.until(lambda _: self.selection_count() == 0))
