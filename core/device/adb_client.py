from __future__ import annotations

import subprocess
from pathlib import Path

from core.device.device_manager import DeviceManager


class ADBClient:
    def __init__(self, manager: DeviceManager) -> None:
        self.manager = manager

    def shell(self, command: str) -> str:
        if self.manager.is_simulation_backend():
            return self.manager.shell(command)
        result = subprocess.run(["adb", "-s", self.manager.serial, "shell", command], capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def install(self, apk_path: str) -> dict[str, str]:
        if self.manager.is_simulation_backend():
            return self.manager.install(apk_path)
        subprocess.run(["adb", "-s", self.manager.serial, "install", apk_path], check=True)
        return {"status": "passed", "apk": apk_path}

    def uninstall(self, package: str) -> dict[str, str]:
        if self.manager.is_simulation_backend():
            return self.manager.uninstall(package)
        subprocess.run(["adb", "-s", self.manager.serial, "uninstall", package], check=True)
        return {"status": "passed", "package": package}

    def start_app(self, package: str, activity: str | None = None) -> dict[str, str]:
        if self.manager.is_simulation_backend():
            return self.manager.launch_app()
        component = f"{package}/{activity}" if activity else package
        result = subprocess.run(
            ["adb", "-s", self.manager.serial, "shell", "am", "start", "-n", component],
            capture_output=True,
            text=True,
            check=False,
        )
        output = "\n".join(part.strip() for part in [result.stdout, result.stderr] if part and part.strip())
        if result.returncode != 0 or "Error type" in output or "Error:" in output:
            raise RuntimeError(output or f"adb am start failed: {component}")
        return {"status": "passed", "package": package}

    def stop_app(self, package: str) -> dict[str, str]:
        if self.manager.is_simulation_backend():
            return self.manager.stop_app()
        self.shell(f"am force-stop {package}")
        return {"status": "passed", "package": package}

    def pull(self, remote: str, local: str) -> dict[str, str]:
        if self.manager.is_simulation_backend():
            return self.manager.pull(remote, local)
        subprocess.run(["adb", "-s", self.manager.serial, "pull", remote, local], check=True)
        return {"status": "passed", "remote": remote, "local": local}

    def push(self, local: str, remote: str) -> dict[str, str]:
        if self.manager.is_simulation_backend():
            return self.manager.push(local, remote)
        subprocess.run(["adb", "-s", self.manager.serial, "push", local, remote], check=True)
        return {"status": "passed", "local": local, "remote": remote}

    def dumpsys(self, service: str) -> str:
        return self.shell(f"dumpsys {service}")

    def logcat(self, lines: int = 200) -> str:
        if self.manager.is_simulation_backend():
            return self.manager.get_logcat()
        result = subprocess.run(["adb", "-s", self.manager.serial, "logcat", "-d", "-t", str(lines)], capture_output=True, text=True, check=True)
        return result.stdout

    def screencap(self, output_path: str | Path) -> str:
        if self.manager.is_simulation_backend():
            return self.manager.screencap(output_path)
        temp_remote = "/sdcard/__codex_tmp_screen.png"
        self.shell(f"screencap -p {temp_remote}")
        self.pull(temp_remote, str(output_path))
        return str(output_path)

    def start_intent(self, action: str, data: str | None = None) -> dict[str, str]:
        if self.manager.is_simulation_backend():
            return {"status": "passed", "action": action, "data": data}
        command = ["adb", "-s", self.manager.serial, "shell", "am", "start", "-a", action]
        if data:
            command.extend(["-d", data])
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        output = "\n".join(part.strip() for part in [result.stdout, result.stderr] if part and part.strip())
        if result.returncode != 0 or "Error" in output:
            raise RuntimeError(output or f"adb am start failed: {action}")
        return {"status": "passed", "action": action, "data": data}

    def list_packages(self) -> list[str]:
        if self.manager.is_simulation_backend():
            base = [value for value in [self.manager.package, "com.android.settings", "com.android.systemui"] if value]
            return base
        output = self.shell("pm list packages")
        return [line.replace("package:", "").strip() for line in output.splitlines() if line.strip()]

    def setting_get(self, namespace: str, name: str) -> str:
        return self.shell(f"settings get {namespace} {name}")
