"""Thin client for the betting backend. Returns raw responses where tests need to inspect errors."""
import json
from decimal import Decimal

import allure
import requests

from utils.money import to_decimal


class BettingApiClient:
    def __init__(self, base_url: str, user_id: str, timeout: int = 10) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"x-user-id": user_id})

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self._base_url}{path}"
        with allure.step(f"{method} {path}"):
            if "json" in kwargs:
                allure.attach(json.dumps(kwargs["json"], indent=2), "request body", allure.attachment_type.JSON)
            response = self._session.request(method, url, timeout=self._timeout, **kwargs)
            allure.attach(
                f"{response.status_code} {response.reason}\n\n{response.text}",
                "response",
                allure.attachment_type.TEXT,
            )
            return response

    def get_matches(self) -> list[dict]:
        response = self._request("GET", "/api/matches")
        response.raise_for_status()
        return response.json()

    def get_balance(self) -> Decimal:
        response = self._request("GET", "/api/balance")
        response.raise_for_status()
        return to_decimal(response.json()["balance"])

    def reset_balance(self) -> None:
        self._request("POST", "/api/reset-balance").raise_for_status()

    def place_bet(self, match_id: str, selection: str, stake) -> requests.Response:
        """Return the raw response so negative tests can assert on status and error code."""
        payload = {"matchId": match_id, "selection": selection, "stake": stake}
        return self._request("POST", "/api/place-bet", json=payload)
