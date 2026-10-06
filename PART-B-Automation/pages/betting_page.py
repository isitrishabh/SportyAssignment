from decimal import Decimal

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage
from pages.components.bet_slip import BetSlip
from pages.components.match_list import MatchList
from pages.components.receipt_modal import ReceiptModal
from utils.money import parse_amount


class BettingPage(BasePage):
    """Single page of the app. Owns navigation and the header; delegates the rest to components."""

    HEADER_BALANCE = (By.ID, "header-balance")

    def __init__(self, driver: WebDriver, app_url: str, timeout: int) -> None:
        super().__init__(driver, timeout)
        self._app_url = app_url
        self.match_list = MatchList(driver, timeout)
        self.bet_slip = BetSlip(driver, timeout)
        self.receipt = ReceiptModal(driver, timeout)

    def open(self) -> "BettingPage":
        self._driver.get(self._app_url)
        self.match_list.wait_until_loaded()
        return self

    def balance(self) -> Decimal:
        return parse_amount(self._text(self.HEADER_BALANCE))

    def wait_for_balance(self, expected: Decimal) -> bool:
        """Poll the header until it shows the expected balance; False if it never does."""
        try:
            return bool(self._wait.until(lambda _: self.balance() == expected))
        except TimeoutException:
            return False
