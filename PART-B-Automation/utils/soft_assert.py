"""Collect several independent failures in one test run instead of stopping at the first."""


class SoftAssertions:
    def __init__(self) -> None:
        self._failures: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self._failures.append(message)

    def check_equal(self, actual, expected, description: str) -> None:
        self.check(actual == expected, f"{description}: expected {expected!r}, got {actual!r}")

    def assert_all(self) -> None:
        if self._failures:
            report = "\n".join(f"  - {failure}" for failure in self._failures)
            raise AssertionError(f"{len(self._failures)} soft assertion(s) failed:\n{report}")
