from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class MatchList(BasePage):
    MATCH_LIST = (By.ID, "match-list")
    FIRST_ODDS_BUTTON = (By.CSS_SELECTOR, "#match-list .oddsButton")

    def wait_until_loaded(self) -> None:
        self._visible(self.MATCH_LIST)
        self._visible(self.FIRST_ODDS_BUTTON)

    def select_outcome(self, match_id: str, outcome: str) -> None:
        """outcome is 'home', 'draw' or 'away' (buttons 1, X, 2)."""
        self._click((By.ID, f"odds-{match_id}-{outcome}"))
