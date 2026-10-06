from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.money import parse_amount


class ReceiptModal(BasePage):
    ROOT = (By.ID, "modal-success")
    BET_ID = (By.ID, "modal-success-bet-id")
    MATCH = (By.ID, "modal-success-match")
    STAKE = (By.ID, "modal-success-stake")
    ODDS = (By.ID, "modal-success-odds")
    PAYOUT = (By.ID, "modal-success-payout")
    PLACED_AT = (By.ID, "modal-success-placed-at")
    CLOSE_BUTTON = (By.ID, "modal-success-close")

    def wait_until_displayed(self) -> None:
        self._visible(self.ROOT)

    @property
    def bet_id(self) -> str:
        return self._text(self.BET_ID)

    @property
    def match(self) -> str:
        return self._text(self.MATCH)

    @property
    def stake(self) -> Decimal:
        return parse_amount(self._text(self.STAKE))

    @property
    def odds(self) -> Decimal:
        return parse_amount(self._text(self.ODDS))

    @property
    def payout(self) -> Decimal:
        return parse_amount(self._text(self.PAYOUT))

    @property
    def placed_at(self) -> str:
        return self._text(self.PLACED_AT)

    def close(self) -> None:
        self._click(self.CLOSE_BUTTON)
        self._wait.until(EC.invisibility_of_element_located(self.ROOT))
