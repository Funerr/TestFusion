from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class UIElement(BaseModel):
    resource_id: str
    text: str = ""
    attrs: dict[str, Any] = Field(default_factory=dict)


class DeviceState(BaseModel):
    serial: str = "auto"
    backend: str = "simulation"
    platform: str = "android"
    package: str | None = None
    current_activity: str | None = None
    current_screen: str = "stopped"
    elements: dict[str, UIElement] = Field(default_factory=dict)
    logs: list[str] = Field(default_factory=list)
    occupied: bool = False
    crashed: bool = False
    backgrounded: bool = False
    inputs: dict[str, str] = Field(default_factory=dict)
    wlan_enabled: bool = False
    bluetooth_enabled: bool = False
    location_enabled: bool = False
    mobile_data_enabled: bool = True
    airplane_mode_enabled: bool = False
    nfc_enabled: bool = False
    hotspot_enabled: bool = False
    dark_mode_enabled: bool = False
    auto_rotate_enabled: bool = True
    brightness_percent: int = 50
    media_volume_percent: int = 50
    ring_volume_percent: int = 60
    permission_dialog_visible: bool = False
    permission_dialog_name: str = ""
    permission_grants: dict[str, str] = Field(default_factory=dict)
    screen_locked: bool = False
    screen_on: bool = True
