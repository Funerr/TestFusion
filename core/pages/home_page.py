from __future__ import annotations

from agent.schemas.assertion_spec_schema import LocatorSpec
from core.pages.base_page import BasePage


class HomePage(BasePage):
    name = "home"
    activity = "com.example.cursor.MainActivity"
    must_have = [
        LocatorSpec(by="id", value="home_tab"),
        LocatorSpec(by="id", value="search_box"),
        LocatorSpec(by="id", value="welcome_banner"),
    ]
    must_not_have = [LocatorSpec(by="id", value="error_dialog")]
