from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToggleSpec:
    key: str
    field: str
    label: str
    aliases: tuple[str, ...]
    namespace: str
    settings_key: str
    page: str
    intent_action: str


@dataclass(frozen=True)
class ValueSpec:
    key: str
    field: str
    label: str
    aliases: tuple[str, ...]
    namespace: str
    settings_key: str
    page: str
    min_value: int = 0
    max_value: int = 100


SYSTEM_TOGGLE_SPECS: dict[str, ToggleSpec] = {
    "wlan": ToggleSpec(
        key="wlan",
        field="wlan_enabled",
        label="WLAN",
        aliases=("wlan", "wifi", "wi-fi", "无线网络", "无线网"),
        namespace="global",
        settings_key="wifi_on",
        page="wlan",
        intent_action="android.settings.WIFI_SETTINGS",
    ),
    "bluetooth": ToggleSpec(
        key="bluetooth",
        field="bluetooth_enabled",
        label="蓝牙",
        aliases=("蓝牙", "bluetooth"),
        namespace="global",
        settings_key="bluetooth_on",
        page="bluetooth",
        intent_action="android.settings.BLUETOOTH_SETTINGS",
    ),
    "location": ToggleSpec(
        key="location",
        field="location_enabled",
        label="定位",
        aliases=("定位", "位置", "location", "位置信息"),
        namespace="secure",
        settings_key="location_mode",
        page="location",
        intent_action="android.settings.LOCATION_SOURCE_SETTINGS",
    ),
    "mobile_data": ToggleSpec(
        key="mobile_data",
        field="mobile_data_enabled",
        label="移动数据",
        aliases=("移动数据", "流量", "蜂窝数据", "mobile data"),
        namespace="global",
        settings_key="mobile_data",
        page="mobile_network",
        intent_action="android.settings.DATA_ROAMING_SETTINGS",
    ),
    "airplane_mode": ToggleSpec(
        key="airplane_mode",
        field="airplane_mode_enabled",
        label="飞行模式",
        aliases=("飞行模式", "airplane", "airplane mode"),
        namespace="global",
        settings_key="airplane_mode_on",
        page="network",
        intent_action="android.settings.AIRPLANE_MODE_SETTINGS",
    ),
    "nfc": ToggleSpec(
        key="nfc",
        field="nfc_enabled",
        label="NFC",
        aliases=("nfc", "NFC"),
        namespace="global",
        settings_key="nfc_on",
        page="nfc",
        intent_action="android.settings.NFC_SETTINGS",
    ),
    "hotspot": ToggleSpec(
        key="hotspot",
        field="hotspot_enabled",
        label="个人热点",
        aliases=("热点", "个人热点", "hotspot", "wifi热点"),
        namespace="global",
        settings_key="wifi_ap_state",
        page="hotspot",
        intent_action="android.settings.TETHER_SETTINGS",
    ),
    "dark_mode": ToggleSpec(
        key="dark_mode",
        field="dark_mode_enabled",
        label="深色模式",
        aliases=("深色模式", "暗色模式", "dark mode"),
        namespace="secure",
        settings_key="ui_night_mode",
        page="display",
        intent_action="android.settings.DISPLAY_SETTINGS",
    ),
    "auto_rotate": ToggleSpec(
        key="auto_rotate",
        field="auto_rotate_enabled",
        label="自动旋转",
        aliases=("自动旋转", "旋转", "auto rotate"),
        namespace="system",
        settings_key="accelerometer_rotation",
        page="display",
        intent_action="android.settings.DISPLAY_SETTINGS",
    ),
}


SYSTEM_VALUE_SPECS: dict[str, ValueSpec] = {
    "brightness": ValueSpec(
        key="brightness",
        field="brightness_percent",
        label="亮度",
        aliases=("亮度", "屏幕亮度", "brightness"),
        namespace="system",
        settings_key="screen_brightness",
        page="display",
    ),
    "media_volume": ValueSpec(
        key="media_volume",
        field="media_volume_percent",
        label="媒体音量",
        aliases=("媒体音量", "音量", "media volume"),
        namespace="system",
        settings_key="volume_music_speaker",
        page="sound",
    ),
    "ring_volume": ValueSpec(
        key="ring_volume",
        field="ring_volume_percent",
        label="铃声音量",
        aliases=("铃声音量", "来电音量", "ring volume"),
        namespace="system",
        settings_key="volume_ring_speaker",
        page="sound",
    ),
}


SYSTEM_PAGE_ALIASES: dict[str, tuple[str, ...]] = {
    "settings": ("设置", "系统设置", "settings"),
    "wlan": ("wlan", "wifi", "无线网络", "WLAN"),
    "bluetooth": ("蓝牙", "bluetooth"),
    "location": ("定位", "位置", "location"),
    "mobile_network": ("移动网络", "移动数据", "蜂窝网络"),
    "network": ("网络", "网络和互联网"),
    "nfc": ("nfc", "NFC"),
    "hotspot": ("热点", "个人热点", "hotspot"),
    "display": ("显示", "显示和亮度", "亮度", "display"),
    "sound": ("声音", "声音和振动", "sound"),
    "notifications": ("通知", "通知中心", "notifications"),
    "permissions": ("权限", "应用权限", "permissions"),
}


SYSTEM_PAGE_INTENTS: dict[str, str] = {
    "settings": "android.settings.SETTINGS",
    "wlan": "android.settings.WIFI_SETTINGS",
    "bluetooth": "android.settings.BLUETOOTH_SETTINGS",
    "location": "android.settings.LOCATION_SOURCE_SETTINGS",
    "mobile_network": "android.settings.DATA_ROAMING_SETTINGS",
    "network": "android.settings.WIRELESS_SETTINGS",
    "nfc": "android.settings.NFC_SETTINGS",
    "hotspot": "android.settings.TETHER_SETTINGS",
    "display": "android.settings.DISPLAY_SETTINGS",
    "sound": "android.settings.SOUND_SETTINGS",
    "notifications": "android.settings.NOTIFICATION_SETTINGS",
    "permissions": "android.settings.APPLICATION_DETAILS_SETTINGS",
}


def resolve_toggle_key(raw: str) -> str | None:
    lowered = raw.strip().lower()
    for key, spec in SYSTEM_TOGGLE_SPECS.items():
        if lowered == key or lowered in {item.lower() for item in spec.aliases}:
            return key
    return None


def resolve_value_key(raw: str) -> str | None:
    lowered = raw.strip().lower()
    for key, spec in SYSTEM_VALUE_SPECS.items():
        if lowered == key or lowered in {item.lower() for item in spec.aliases}:
            return key
    return None


def resolve_page_key(raw: str) -> str | None:
    lowered = raw.strip().lower()
    for key, aliases in SYSTEM_PAGE_ALIASES.items():
        if lowered == key or lowered in {item.lower() for item in aliases}:
            return key
    return None
