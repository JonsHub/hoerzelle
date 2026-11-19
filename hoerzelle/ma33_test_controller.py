"""Safe, manually-confirmed visual controls for the MA33 test window.

This module is intentionally not wired into the production test flow yet. It is a
test tool for validating template matching before any automatic click is enabled.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import pyautogui
import win32gui
import win32process
import psutil

import paths_dir


BUTTON_TEMPLATES = {
    "autotest": "1_autotest_button.png",
    #"autotest_pushed": "2_autotest_pushed.png",
    "play": "3_playbutton.png",
    "save_and_close": "4_speichern_button.png",
    "confirm_yes": "5_save_and_close_ask.png",
}

CLICK_POSITIONS = {
    "autotest": (0.50, 0.25),
    #"autotest_pushed": (0.54, 0.25),
    "play": (0.36, 0.36),
    "save_and_close": (0.50, 0.52),
    "confirm_yes": (0.20, 0.68),
}

# Match against the actual control region rather than all unused background.
# The values are (left, top, right, bottom) fractions of the reference image.
MATCH_CROPS = {
    "autotest": (0.25, 0.05, 0.76, 0.52),
    #"autotest_pushed": (0.08, 0.02, 0.96, 0.55),
    "play": (0.08, 0.45, 0.58, 0.72),
    "save_and_close": (0.02, 0.02, 0.98, 0.70),
    "confirm_yes": (0.02, 0.02, 0.98, 0.98),
}

TEMPLATE_THRESHOLDS = {
    "autotest": 0.80,
    #"autotest_pushed": 0.80,
    "play": 0.70,
    "save_and_close": 0.75,
    "confirm_yes": 0.70,
}

# Small measured corrections from live testing. Positive values move the click
# further down, negative values further up.
CLICK_OFFSET_PX = {
    "autotest": (0, -5),
    #"autotest_pushed": (0, 0),
    "play": (0, -25),
    "save_and_close": (0, 20),
    "confirm_yes": (0, 0),
}


@dataclass(frozen=True)
class TemplateMatch:
    """A template match in screen coordinates."""

    template_name: str
    confidence: float
    center_x: int
    center_y: int
    width: int
    height: int
    click_x: int
    click_y: int


class MA33TestController:
    """Find and operate MA33 controls with visual confirmation."""

    def __init__(
        self,
        template_directory: Optional[Path] = None,
        confidence_threshold: Optional[float] = None,
        poll_interval: float = 0.5,
    ) -> None:
        self.template_directory = template_directory or (
            paths_dir.IMAGES_DIR / "buttons"
        )
        self.confidence_threshold = confidence_threshold
        self.poll_interval = poll_interval

    def wait_for_ma33_window(self) -> int:
        """Wait until a visible MA33 window exists and return its handle."""

        print("Warte auf das MA33-Fenster ...")
        while True:
            for window_handle in self._find_visible_ma33_windows():
                print(
                    "MA33-Fenster gefunden: "
                    f"{win32gui.GetWindowText(window_handle) or window_handle}"
                )
                return window_handle
            time.sleep(self.poll_interval)

    @staticmethod
    def _find_visible_ma33_windows() -> list[int]:
        """Find visible windows owned by ma33.exe, not by title matching."""

        handles: list[int] = []

        def enum_callback(handle: int, _unused: object) -> bool:
            if not win32gui.IsWindowVisible(handle):
                return True
            try:
                _thread_id, process_id = win32process.GetWindowThreadProcessId(handle)
                process_name = psutil.Process(process_id).name().lower()
                if process_name == "ma33.exe":
                    handles.append(handle)
            except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                pass
            return True

        win32gui.EnumWindows(enum_callback, None)
        return handles

    def wait_for_template(
        self,
        template_name: str,
        timeout: Optional[float] = None,
    ) -> Optional[TemplateMatch]:
        """Wait for a template in the MA33 window, or return None on timeout."""

        template_path = self.template_directory / BUTTON_TEMPLATES[template_name]
        template = self._load_template(template_path)
        started_at = time.monotonic()

        print(f"Suche '{template_name}' ({template_path.name}) ...")
        window_handle = self.wait_for_ma33_window()
        while timeout is None or time.monotonic() - started_at < timeout:
            if not win32gui.IsWindowVisible(window_handle):
                window_handle = self.wait_for_ma33_window()
            screenshot, window_left, window_top = self._capture_window(window_handle)
            match = self._find_template(
                screenshot,
                template,
                template_name,
                window_left,
                window_top,
            )
            if match is not None:
                print(
                    f"Gefunden: '{template_name}' mit "
                    f"{match.confidence:.1%} bei "
                    f"Match-Bereich ({match.center_x}, {match.center_y}), "
                    f"Klick-Ziel ({match.click_x}, {match.click_y})"
                )
                return match
            time.sleep(self.poll_interval)

        print(f"Timeout: '{template_name}' wurde nicht gefunden.")
        return None

    def confirm_and_click(self, match: TemplateMatch) -> bool:
        """Move to a match and click only after explicit console confirmation."""

        if not self._move_to_match(match):
            return False
        confirmation = input(
            "Mit 'j' bestätigen, jede andere Eingabe bricht ab: "
        ).strip().lower()
        if confirmation != "j":
            print("Klick abgebrochen.")
            return False

        if not self._ma33_is_foreground():
            print("Klick abgebrochen: MA33 ist nicht im Vordergrund.")
            return False

        pyautogui.click(match.click_x, match.click_y)
        print("Klick ausgeführt.")
        return True

    def click_template(
        self,
        template_name: str,
        timeout: Optional[float] = None,
    ) -> bool:
        """Find a control and click it automatically after a safe foreground check."""

        if template_name not in BUTTON_TEMPLATES:
            valid_names = ", ".join(BUTTON_TEMPLATES)
            raise ValueError(f"Unbekannter Button '{template_name}'. Erlaubt: {valid_names}")

        match = self.wait_for_template(template_name, timeout)
        return match is not None and self._click_match(match)

    def confirm_save_and_close(
        self,
        timeout: Optional[float] = None,
        confirmation_delay: float = 1.5,
    ) -> bool:
        """Click save, then confirm the preselected Ja action with Space."""

        if not self.click_template("save_and_close", timeout):
            return False

        print(
            f"Warte {confirmation_delay:.1f} Sekunden auf den "
            "Bestätigungsdialog ..."
        )
        time.sleep(confirmation_delay)
        if not self._ma33_is_foreground():
            print("Bestätigung abgebrochen: MA33 ist nicht im Vordergrund.")
            return False

        print("Bestätige die vorausgewählte Ja-Aktion mit Leertaste.")
        pyautogui.press("space")
        return True

    def _move_to_match(self, match: TemplateMatch) -> bool:
        pyautogui.moveTo(match.click_x, match.click_y, duration=0.2)
        print(
            f"Maus steht auf ({match.click_x}, {match.click_y}). "
        )
        return True

    def _click_match(self, match: TemplateMatch) -> bool:
        if not self._move_to_match(match):
            return False

        if not self._ma33_is_foreground():
            print("Klick abgebrochen: MA33 ist nicht im Vordergrund.")
            return False

        pyautogui.click(match.click_x, match.click_y)
        print("Klick ausgeführt.")
        return True

    def run_single_step(
        self,
        template_name: str,
        timeout: Optional[float] = None,
    ) -> bool:
        """Find one control, ask for confirmation, and optionally click it."""

        if template_name not in BUTTON_TEMPLATES:
            valid_names = ", ".join(BUTTON_TEMPLATES)
            raise ValueError(f"Unbekannter Button '{template_name}'. Erlaubt: {valid_names}")

        match = self.wait_for_template(template_name, timeout)
        return match is not None and self.confirm_and_click(match)

    @staticmethod
    def _load_template(template_path: Path) -> np.ndarray:
        if not template_path.exists():
            raise FileNotFoundError(f"Template nicht gefunden: {template_path}")

        template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
        if template is None:
            raise ValueError(f"Template konnte nicht gelesen werden: {template_path}")
        return template

    @staticmethod
    def _capture_window(window_handle: int) -> tuple[np.ndarray, int, int]:
        left, top, right, bottom = win32gui.GetWindowRect(window_handle)
        width = right - left
        height = bottom - top
        if width <= 0 or height <= 0:
            raise RuntimeError("Ungültige Größe des MA33-Fensters")

        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        return frame, left, top

    def _find_template(
        self,
        frame: np.ndarray,
        template: np.ndarray,
        template_name: str,
        window_left: int,
        window_top: int,
    ) -> Optional[TemplateMatch]:
        best_match: Optional[TemplateMatch] = None
        confidence_threshold = (
            self.confidence_threshold
            if self.confidence_threshold is not None
            else TEMPLATE_THRESHOLDS[template_name]
        )
        left, top, right, bottom = MATCH_CROPS[template_name]
        crop_left = round(template.shape[1] * left)
        crop_top = round(template.shape[0] * top)
        crop_right = round(template.shape[1] * right)
        crop_bottom = round(template.shape[0] * bottom)
        template = template[crop_top:crop_bottom, crop_left:crop_right]

        for scale in np.linspace(0.75, 1.35, 13):
            scaled_width = max(1, round(template.shape[1] * scale))
            scaled_height = max(1, round(template.shape[0] * scale))
            if scaled_width > frame.shape[1] or scaled_height > frame.shape[0]:
                continue

            scaled_template = cv2.resize(
                template,
                (scaled_width, scaled_height),
                interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC,
            )
            result = cv2.matchTemplate(
                frame,
                scaled_template,
                cv2.TM_CCOEFF_NORMED,
            )
            _, confidence, _, location = cv2.minMaxLoc(result)
            if confidence < confidence_threshold:
                continue

            candidate = TemplateMatch(
                template_name=template_name,
                confidence=float(confidence),
                center_x=window_left + location[0] + scaled_width // 2,
                center_y=window_top + location[1] + scaled_height // 2,
                width=scaled_width,
                height=scaled_height,
                click_x=(
                    window_left + location[0] + scaled_width // 2
                    if template_name in {"save_and_close", "confirm_yes"}
                    else window_left + location[0] + round(
                        scaled_width
                        * CLICK_POSITIONS.get(template_name, (0.5, 0.5))[0]
                    )
                ) + (
                    -98
                    if template_name == "confirm_yes"
                    else 0
                ) + CLICK_OFFSET_PX[template_name][0],
                click_y=(
                    window_top + location[1] + scaled_height // 2
                    if template_name in {"save_and_close", "confirm_yes"}
                    else window_top + location[1] + round(
                        scaled_height
                        * CLICK_POSITIONS.get(template_name, (0.5, 0.5))[1]
                    )
                ) + (
                    21
                    if template_name == "confirm_yes"
                    else 0
                ) + CLICK_OFFSET_PX[template_name][1],
            )
            if best_match is None or candidate.confidence > best_match.confidence:
                best_match = candidate

        return best_match

    @staticmethod
    def _ma33_is_foreground() -> bool:
        foreground_handle = win32gui.GetForegroundWindow()
        try:
            _thread_id, process_id = win32process.GetWindowThreadProcessId(
                foreground_handle
            )
            process_name = psutil.Process(process_id).name().lower()
            return process_name == "ma33.exe"
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manuell bestätigter MA33-Template-Matching-Test"
    )
    parser.add_argument(
        "--target",
        choices=tuple(BUTTON_TEMPLATES),
        default="autotest",
        help="Zu suchendes Button-Template",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Maximale Suchzeit in Sekunden; ohne Angabe unbegrenzt",
    )
    args = parser.parse_args()

    controller = MA33TestController()
    try:
        return 0 if controller.run_single_step(args.target, args.timeout) else 1
    except KeyboardInterrupt:
        print("\nDurch Benutzer abgebrochen.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())