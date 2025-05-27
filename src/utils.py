import json
import platform
import shutil
import subprocess
import zipfile
from pathlib import Path
import requests
from tqdm import tqdm
import project

CHROME_SYMLINK = project.BIN_DIR / ("chrome.exe" if platform.system() == "Windows" else "chrome")
CHROMEDRIVER_SYMLINK = project.BIN_DIR / ("chromedriver.exe" if platform.system() == "Windows" else "chromedriver")

PLATFORM_MAP = {
    "Windows": "win64",
    "Linux": "linux64",
    "Darwin": "mac-arm64" if platform.machine() == "arm64" else "mac-x64"
}
CHANNEL = "Stable"


def install_or_update_chromedriver_and_cft():
    print("Checking current Chrome for Testing and ChromeDriver versions...")
    local_chrome_ver = get_local_version(CHROME_SYMLINK, kind="chrome")
    local_driver_ver = get_local_version(CHROMEDRIVER_SYMLINK, kind="chromedriver")
    latest_ver, downloads = get_latest_cft_version()

    print(f"Local Chrome version: {local_chrome_ver or 'not installed'}")
    print(f"Local ChromeDriver version: {local_driver_ver or 'not installed'}")
    print(f"Latest version: {latest_ver}")

    chrome_needs_update = local_chrome_ver != latest_ver
    driver_needs_update = local_driver_ver != latest_ver

    if chrome_needs_update:
        print("Updating Chrome for Testing...")
        install_chrome(latest_ver, downloads["chrome"])
    else:
        print("Chrome for Testing is up to date.")

    if driver_needs_update:
        print("Updating ChromeDriver...")
        install_chromedriver(latest_ver, downloads["chromedriver"])
    else:
        print("ChromeDriver is up to date.")


def get_local_version(binary_path, kind="chrome"):
    import platform
    import re

    if not binary_path.exists():
        return None

    if platform.system() == "Darwin" and kind == "chrome":
        manifest_path = binary_path.parent / "manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r") as f:
                    data = json.load(f)
                    version = data.get("version")
                    if version:
                        return version
            except Exception as e:
                print(f"Warning: failed to read manifest.json: {e}")
        app_path = CHROME_SYMLINK.resolve().parents[2]
        version = get_mac_app_version(app_path)
        if version:
            return version

    try:
        result = subprocess.run([str(binary_path), "--version"], capture_output=True, text=True)
        output = result.stdout.strip()
        if kind == "chromedriver":
            parts = output.split()
            if len(parts) > 1:
                return parts[1]
        else:
            match = re.search(r"\b\d+\.\d+\.\d+\.\d+\b", output)
            if match:
                return match.group(0)
    except Exception:
        pass

    return None


def get_mac_app_version(app_path):
    try:
        result = subprocess.run(
            ["defaults", "read", str(app_path) + "/Contents/Info", "CFBundleShortVersionString"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"Error reading app version: {e}")
    return None


def get_latest_cft_version(channel=CHANNEL):
    url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    ch_info = data["channels"][channel]
    version = ch_info["version"]
    downloads = ch_info["downloads"]
    return version, downloads


def find_download_url(download_list, platform_key):
    for item in download_list:
        if item["platform"] == platform_key:
            return item["url"]
    raise ValueError(f"No download URL found for platform: {platform_key}")


def download_and_extract(url: str, extract_to: Path, desc: str):
    extract_to.mkdir(parents=True, exist_ok=True)
    zip_path = extract_to / "temp.zip"

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(zip_path, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=desc) as bar:
            for chunk in r.iter_content(1024):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    zip_path.unlink()


def ensure_executable(path: Path):
    if platform.system() != "Windows":
        path.chmod(path.stat().st_mode | 0o111)


def install_chrome(version: str, chrome_downloads: list):
    plat = PLATFORM_MAP[platform.system()]
    url = find_download_url(chrome_downloads, plat)
    print(f"Installing Chrome for Testing {version} ({plat})...")
    download_and_extract(url, project.BIN_DIR, "Downloading Chrome")

    dest = next(project.BIN_DIR.glob("chrome-*"))

    if plat == "mac-arm64":
        real_bin = dest / "Google Chrome for Testing.app" / "Contents" / "MacOS" / "Google Chrome for Testing"
    else:
        bin_name = "chrome.exe" if platform.system() == "Windows" else "chrome"
        real_bin = dest / bin_name

    if CHROME_SYMLINK.exists() or CHROME_SYMLINK.is_symlink():
        CHROME_SYMLINK.unlink()

    try:
        CHROME_SYMLINK.symlink_to(real_bin.resolve())
    except OSError:
        shutil.copy(real_bin, CHROME_SYMLINK)

    ensure_executable(real_bin)
    ensure_executable(CHROME_SYMLINK)

    print(f"Chrome for Testing installed at: {CHROME_SYMLINK}")


def install_chromedriver(version: str, driver_downloads: list):
    plat = PLATFORM_MAP[platform.system()]
    url = find_download_url(driver_downloads, plat)
    print(f"Installing ChromeDriver {version} ({plat})...")
    download_and_extract(url, project.BIN_DIR, "Downloading ChromeDriver")

    dest = next(project.BIN_DIR.glob("chromedriver-*"))

    if plat == "mac-arm64":
        real_bin = dest / "chromedriver"
    else:
        bin_name = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
        real_bin = dest / bin_name

    if CHROMEDRIVER_SYMLINK.exists() or CHROMEDRIVER_SYMLINK.is_symlink():
        CHROMEDRIVER_SYMLINK.unlink()

    try:
        CHROMEDRIVER_SYMLINK.symlink_to(real_bin.resolve())
    except OSError:
        shutil.copy(real_bin, CHROMEDRIVER_SYMLINK)

    ensure_executable(real_bin)
    ensure_executable(CHROMEDRIVER_SYMLINK)

    print(f"ChromeDriver installed at: {CHROMEDRIVER_SYMLINK}")
