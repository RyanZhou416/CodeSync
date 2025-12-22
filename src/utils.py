import platform
import subprocess
import os
import sys


def is_system_dark_mode():
    """
    跨平台检测系统是否处于深色模式
    返回: True (深色), False (浅色/未知)
    """
    sys_name = platform.system()

    if sys_name == "Windows":
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize')
            val, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            return val == 0
        except:
            return False

    elif sys_name == "Darwin":  # macOS
        try:
            # 检查 AppleInterfaceStyle，如果存在且为 Dark 则返回 True
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True
            )
            return "Dark" in result.stdout
        except:
            return False

    elif sys_name == "Linux":
        try:
            # 优先尝试 GNOME/GTK 设置
            # 检查 color-scheme (prefer-dark)
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True, text=True
            )
            if "prefer-dark" in result.stdout:
                return True

            # 某些旧版 GTK 可能使用 gtk-theme，如果包含 'dark' 字样
            result2 = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                capture_output=True, text=True
            )
            if "dark" in result2.stdout.lower() or "black" in result2.stdout.lower():
                return True
        except:
            pass

    return False


def apply_windows_dark_mode(root, is_dark):
    """
    仅在 Windows 下尝试修改标题栏颜色。
    """
    if platform.system() != "Windows":
        return

    try:
        import ctypes
        from ctypes import windll, c_int, byref

        root.update()
        hwnd = windll.user32.GetParent(root.winfo_id())

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19

        value = c_int(2 if is_dark else 0)

        if windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(value), 4) != 0:
            windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_OLD, byref(value), 4)
    except Exception:
        pass