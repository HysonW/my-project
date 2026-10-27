# -*- coding: utf-8 -*-
"""检查当前环境是否具备运行 Orange3 / 截图的条件。

Orange 经常装在独立的 conda 环境里（例如 D:\\orange），
所以除了当前解释器，还会探测 ORANGE_PYTHON 和常见安装路径。
"""
import importlib.util
import os
import platform
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def spec(name):
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


def orange_version():
    if not spec("Orange"):
        return None
    try:
        import Orange
        for attr in ("__version__", "version"):
            obj = getattr(Orange, attr, None)
            if obj is None:
                continue
            if isinstance(obj, str):
                return obj
            ver = getattr(obj, "version", None)
            if ver:
                return str(ver)
        return "unknown"
    except Exception as exc:  # pragma: no cover
        return f"import-error: {exc}"


def probe_external(python):
    if not python or not os.path.isfile(python):
        return None
    try:
        result = subprocess.run(
            [python, "-c", "import Orange; print(Orange.version.version)"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=40,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
    return lines[-1] if lines else "unknown"


def external_candidates():
    seen = set()
    env_python = os.environ.get("ORANGE_PYTHON")
    home = os.path.expanduser("~")
    local = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        env_python,
        r"D:\orange\python.exe",
        r"C:\Program Files\Orange\python.exe",
        os.path.join(local, "Programs", "Orange", "python.exe") if local else "",
        os.path.join(home, "miniconda3", "envs", "orange", "python.exe"),
        os.path.join(home, "anaconda3", "envs", "orange", "python.exe"),
        r"C:\ProgramData\Miniconda3\envs\orange\python.exe",
    ]
    for path in candidates:
        if path and path not in seen:
            seen.add(path)
            yield path


def main():
    py = sys.executable
    print(f"python: {py}")
    print(f"python-version: {platform.python_version()}")
    print(f"platform: {platform.platform()}")
    print(f"orange-installed: {spec('Orange')}")
    print(f"orange-version: {orange_version()}")
    print(f"orange-canvas-module: {spec('Orange.canvas')}")
    print(f"pyqt5: {spec('PyQt5')}")
    print(f"pyside6: {spec('PySide6')}")
    print(f"pyautogui: {spec('pyautogui')}")
    print(f"pywinauto: {spec('pywinauto')}")

    gui = True
    if platform.system() == "Linux":
        gui = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    print(f"graphical-session-likely: {gui}")

    found = []
    for path in external_candidates():
        version = probe_external(path)
        if version:
            found.append((path, version))
            print(f"external-orange: {path} ({version})")

    print()
    if spec("Orange") and gui:
        print("结论：当前解释器可以运行 Orange 画布并截图。")
        print("启动：python -m Orange.canvas")
        print("截图：用系统截图工具截取画布，或用 pyautogui/pywinauto 自动化。")
    elif found:
        print("结论：当前解释器没有 Orange，但发现了独立的 Orange 环境：")
        for path, version in found:
            print(f"  - {path}  (Orange {version})")
        print("用该环境的 python 运行 Orange 代码，例如：")
        print(f'  "{found[0][0]}" -m Orange.canvas')
        print("也可以设置环境变量 ORANGE_PYTHON 指向它。")
    elif spec("Orange") and not gui:
        print("结论：Orange 已安装，但当前没有图形会话，无法显示/截图。")
        print("可在带桌面的机器上运行，或使用工作流示意图。")
    else:
        print("结论：未安装 Orange。")
        print("安装：python -m pip install orange3")
        print("启动：python -m Orange.canvas")
        print("没有 GUI 时：用 scripts/orange_style_diagram.py 生成示意图，并标注“示意图”。")

    if shutil.which("orange-canvas"):
        print(f"orange-canvas-cli: {shutil.which('orange-canvas')}")


if __name__ == "__main__":
    main()
