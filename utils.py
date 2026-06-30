"""
utils.py
--------
Shared helper utilities used across the SkyLink Airlines GUI: themed
message dialogs, window centering, color/theme constants, and small
reusable widget helpers.

This is a presentation-layer module only. It does not contain any
business logic — all business logic lives in database.py and is
called as-is by the GUI pages.
"""

import os
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


# ----------------------------------------------------------------------
# THEME / COLOR PALETTE
# ----------------------------------------------------------------------
# A single professional dark palette shared by every page so the whole
# application looks consistent. Centralizing it here means a future
# re-theme only requires editing this dictionary.
COLORS = {
    "bg_root": "#0d0f17",
    "bg_panel": "#11141c",
    "bg_card": "#161b26",
    "bg_card_alt": "#1b2130",
    "bg_input": "#1b2130",
    "border": "#232938",
    "accent": "#3d8bfd",
    "accent_hover": "#2f78e0",
    "accent_soft": "#1d3a63",
    "success": "#2fb872",
    "success_hover": "#23985d",
    "danger": "#e5484d",
    "danger_hover": "#c93f44",
    "warning": "#f5a623",
    "text_primary": "#f0f1f5",
    "text_secondary": "#b7bcc9",
    "text_muted": "#8d93a3",
    "white": "#ffffff",
}

FONT_FAMILY = "Segoe UI"


def font(size=13, weight="normal"):
    """Returns a CTkFont-compatible tuple/font object for consistent typography."""
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def init_appearance():
    """Sets the global CustomTkinter appearance mode and color theme.
    Call this once, before any CTk windows are created."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


def style_treeview(style: ttk.Style):
    """Applies a dark, professional theme to ttk.Treeview widgets so the
    tables match the CustomTkinter dark theme (CTk has no native table
    widget, so ttk.Treeview is used for all tabular data)."""
    style.theme_use("default")

    style.configure(
        "Sky.Treeview",
        background=COLORS["bg_card"],
        foreground=COLORS["text_primary"],
        fieldbackground=COLORS["bg_card"],
        bordercolor=COLORS["border"],
        borderwidth=0,
        rowheight=32,
        font=(FONT_FAMILY, 11),
    )
    style.map(
        "Sky.Treeview",
        background=[("selected", COLORS["accent_soft"])],
        foreground=[("selected", COLORS["white"])],
    )
    style.configure(
        "Sky.Treeview.Heading",
        background=COLORS["bg_card_alt"],
        foreground=COLORS["text_secondary"],
        relief="flat",
        font=(FONT_FAMILY, 11, "bold"),
    )
    style.map(
        "Sky.Treeview.Heading",
        background=[("active", COLORS["bg_card_alt"])],
    )


# ----------------------------------------------------------------------
# WINDOW HELPERS
# ----------------------------------------------------------------------
def center_window(window, width=None, height=None):
    """Centers a Tk/CTk Toplevel or root window on the primary screen."""
    window.update_idletasks()
    width = width or window.winfo_width()
    height = height or window.winfo_height()
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


# ----------------------------------------------------------------------
# MESSAGE DIALOGS
# ----------------------------------------------------------------------
class _MessageDialog(ctk.CTkToplevel):
    """A small, professional modal dialog used for success / error /
    warning notifications and yes-no confirmations. Replaces PySide6's
    QMessageBox with a themed CustomTkinter equivalent."""

    ICONS = {
        "success": ("\u2713", COLORS["success"]),
        "error": ("\u2715", COLORS["danger"]),
        "warning": ("\u26A0", COLORS["warning"]),
        "question": ("?", COLORS["accent"]),
    }

    def __init__(self, parent, title, message, kind="success", confirm_mode=False):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_panel"])
        self.result = False
        self.transient(parent)
        self.grab_set()

        icon_char, icon_color = self.ICONS.get(kind, self.ICONS["success"])

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(padx=28, pady=24, fill="both", expand=True)

        icon_circle = ctk.CTkLabel(
            container, text=icon_char, width=48, height=48,
            corner_radius=24, fg_color=icon_color, text_color=COLORS["white"],
            font=font(20, "bold"),
        )
        icon_circle.pack(pady=(0, 14))

        title_label = ctk.CTkLabel(container, text=title, font=font(16, "bold"),
                                    text_color=COLORS["text_primary"])
        title_label.pack()

        message_label = ctk.CTkLabel(
            container, text=message, font=font(12), text_color=COLORS["text_secondary"],
            wraplength=320, justify="center",
        )
        message_label.pack(pady=(8, 20))

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack()

        if confirm_mode:
            no_btn = ctk.CTkButton(
                btn_row, text="No", width=110, height=36, fg_color=COLORS["bg_card_alt"],
                hover_color=COLORS["border"], text_color=COLORS["text_primary"],
                font=font(12, "bold"), command=self._on_no,
            )
            no_btn.pack(side="left", padx=6)
            yes_btn = ctk.CTkButton(
                btn_row, text="Yes", width=110, height=36, fg_color=COLORS["danger"],
                hover_color=COLORS["danger_hover"], font=font(12, "bold"),
                command=self._on_yes,
            )
            yes_btn.pack(side="left", padx=6)
        else:
            ok_btn = ctk.CTkButton(
                btn_row, text="OK", width=140, height=36, fg_color=icon_color,
                hover_color=icon_color, font=font(12, "bold"), command=self._on_yes,
            )
            ok_btn.pack()

        self.protocol("WM_DELETE_WINDOW", self._on_no)
        self.after(10, lambda: center_window(self, 400, self.winfo_reqheight()))
        self.wait_window(self)

    def _on_yes(self):
        self.result = True
        self.destroy()

    def _on_no(self):
        self.result = False
        self.destroy()


def show_success(parent, title: str, message: str):
    _MessageDialog(parent, title, message, kind="success")


def show_error(parent, title: str, message: str):
    _MessageDialog(parent, title, message, kind="error")


def show_warning(parent, title: str, message: str):
    _MessageDialog(parent, title, message, kind="warning")


def confirm(parent, title: str, message: str) -> bool:
    dialog = _MessageDialog(parent, title, message, kind="question", confirm_mode=True)
    return dialog.result


# ----------------------------------------------------------------------
# SMALL REUSABLE WIDGETS
# ----------------------------------------------------------------------
def make_card(parent, **kwargs):
    """Creates a CTkFrame styled as a 'card' with rounded corners and a
    subtle border, used throughout the app for panels and stat tiles."""
    defaults = dict(
        fg_color=COLORS["bg_card"],
        corner_radius=14,
        border_width=1,
        border_color=COLORS["border"],
    )
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def primary_button(parent, text, command, width=160, height=40):
    return ctk.CTkButton(
        parent, text=text, command=command, width=width, height=height,
        fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
        font=font(13, "bold"), corner_radius=10,
    )


def secondary_button(parent, text, command, width=160, height=40):
    return ctk.CTkButton(
        parent, text=text, command=command, width=width, height=height,
        fg_color=COLORS["bg_card_alt"], hover_color=COLORS["border"],
        text_color=COLORS["text_primary"], font=font(13, "bold"), corner_radius=10,
        border_width=1, border_color=COLORS["border"],
    )


def success_button(parent, text, command, width=160, height=40):
    return ctk.CTkButton(
        parent, text=text, command=command, width=width, height=height,
        fg_color=COLORS["success"], hover_color=COLORS["success_hover"],
        font=font(13, "bold"), corner_radius=10,
    )


def danger_button(parent, text, command, width=160, height=40):
    return ctk.CTkButton(
        parent, text=text, command=command, width=width, height=height,
        fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
        font=font(13, "bold"), corner_radius=10,
    )


def page_header(parent, title_text, subtitle_text):
    """Builds the consistent large-header + subtitle block used at the
    top of every feature page."""
    box = ctk.CTkFrame(parent, fg_color="transparent")
    title = ctk.CTkLabel(box, text=title_text, font=font(26, "bold"),
                          text_color=COLORS["text_primary"], anchor="w")
    title.pack(anchor="w")
    subtitle = ctk.CTkLabel(box, text=subtitle_text, font=font(13),
                             text_color=COLORS["text_muted"], anchor="w")
    subtitle.pack(anchor="w", pady=(4, 0))
    return box


def stat_card(parent, label_text, value_text="0"):
    """Creates a stat tile (used on Admin Dashboard and Statistics page)
    and returns (card_widget, value_label) so callers can update the
    displayed value later."""
    card = make_card(parent, width=200, height=110)
    card.grid_propagate(False)
    card.pack_propagate(False)

    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(expand=True, fill="both", padx=18, pady=16)

    value_label = ctk.CTkLabel(inner, text=str(value_text), font=font(26, "bold"),
                                text_color=COLORS["accent"], anchor="w")
    value_label.pack(anchor="w")

    label = ctk.CTkLabel(inner, text=label_text, font=font(12),
                          text_color=COLORS["text_muted"], anchor="w")
    label.pack(anchor="w", pady=(4, 0))

    return card, value_label
