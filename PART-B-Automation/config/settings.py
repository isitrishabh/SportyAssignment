"""Central test configuration. Every value can be overridden with an environment variable."""
import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _env_flag(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("BASE_URL", "https://qae-assignment-tau.vercel.app").rstrip("/")
    user_id: str = os.getenv("USER_ID", "candidate-tynWiuDmY7AR")
    headless: bool = _env_flag("HEADLESS", False)
    ui_timeout: int = int(os.getenv("UI_TIMEOUT", "10"))
    api_timeout: int = int(os.getenv("API_TIMEOUT", "10"))
    screenshot_dir: Path = PROJECT_ROOT / "reports" / "screenshots"

    @property
    def app_url(self) -> str:
        return f"{self.base_url}/?user-id={self.user_id}"


settings = Settings()
