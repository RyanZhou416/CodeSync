import platform
import ctypes


def apply_windows_dark_mode(root, is_dark):
    """
    仅在 Windows 下尝试修改标题栏颜色为深色/浅色。
    Mac/Linux 会自动忽略。
    """
    if platform.system() != "Windows":
        return

    try:
        # 强制刷新窗口以获取句柄
        root.update()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())

        # Windows API 常量
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Win11 / Win10 20H1+
        DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19  # Win10 旧版本

        # 2 = 强制深色, 0 = 强制浅色 (根据之前的经验值)
        value = ctypes.c_int(2 if is_dark else 0)

        # 优先尝试新 API
        if ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), 4) != 0:
            # 失败则尝试旧 API
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_OLD, ctypes.byref(value), 4)
    except Exception:
        pass