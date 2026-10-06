"""Shared Selenium helpers: explicit waits only, no sleeps."""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

Locator = tuple[str, str]


class BasePage:
    def __init__(self, driver: WebDriver, timeout: int) -> None:
        self._driver = driver
        self._wait = WebDriverWait(driver, timeout)

    def _visible(self, locator: Locator) -> WebElement:
        return self._wait.until(EC.visibility_of_element_located(locator))

    def _text(self, locator: Locator) -> str:
        return self._visible(locator).text

    def _click(self, locator: Locator) -> None:
        element = self._wait.until(EC.presence_of_element_located(locator))
        # Centre the element so the sticky header cannot intercept the click.
        self._driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        self._wait.until(EC.element_to_be_clickable(locator)).click()

    def _type(self, locator: Locator, text: str) -> None:
        self._visible(locator).send_keys(text)
