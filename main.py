"""
main.py
-------
SkyLink Airlines Reservation System -- GUI Entry Point (CustomTkinter).

Run with:  python main.py
"""

import sys

import customtkinter as ctk
from tkinter import ttk

from database import SkyLinkSystem
from utils import COLORS, font, init_appearance, center_window, style_treeview
from login import LoginWindow
from dashboard import AdminDashboard, CustomerDashboard


class SplashScreen(ctk.CTkToplevel):
    """Branded splash screen with a progress bar, shown briefly before
    the login window appears."""

    def __init__(self, master, on_finished):
        super().__init__(master)
        self.on_finished = on_finished
        self.overrideredirect(True)
        self.configure(fg_color=COLORS["bg_panel"])
        self.geometry("520x320")
        center_window(self, 520, 320)

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=30, pady=30)

        spacer = ctk.CTkFrame(wrap, fg_color="transparent")
        spacer.pack(expand=True)

        ctk.CTkLabel(spacer, text="\u2708 SkyLink Airlines", font=font(28, "bold"),
                     text_color=COLORS["accent"]).pack()
        ctk.CTkLabel(spacer, text="Reservation System v1.0", font=font(11),
                     text_color=COLORS["text_muted"]).pack(pady=(8, 0))

        self.progress = ctk.CTkProgressBar(wrap, width=440, height=10,
                                            progress_color=COLORS["accent"])
        self.progress.set(0)
        self.progress.pack(side="bottom", pady=(0, 6))

        self._value = 0.0
        self._tick()

    def _tick(self):
        self._value += 0.05
        self.progress.set(min(self._value, 1.0))
        if self._value >= 1.0:
            self.destroy()
            self.on_finished()
        else:
            self.after(35, self._tick)


class Application:
    """Orchestrates window transitions: splash -> login -> dashboards."""

    def __init__(self):
        init_appearance()

        # A hidden root window is required because every CTkToplevel
        # needs a master; the actual UI lives entirely in Toplevels so
        # windows can be freely shown/destroyed/recreated.
        self.root = ctk.CTk()
        self.root.withdraw()
        self.root.title("SkyLink Airlines")

        style = ttk.Style(self.root)
        style_treeview(style)

        self.system = SkyLinkSystem()

        self.login_window = None
        self.admin_dashboard = None
        self.customer_dashboard = None

    # ------------------------------------------------------------------
    def show_splash_then_login(self):
        SplashScreen(self.root, self.show_login)

    def show_login(self):
        self.login_window = LoginWindow(
            self.root, self.system,
            on_admin_authenticated=self.show_admin_dashboard,
            on_customer_authenticated=self.show_customer_dashboard,
        )
        center_window(self.login_window, 960, 600)
        self.login_window.lift()
        self.login_window.focus_force()

    def show_admin_dashboard(self):
        if self.login_window:
            self.login_window.destroy()
            self.login_window = None
        self.admin_dashboard = AdminDashboard(self.root, self.system, on_logout=self.show_login)
        center_window(self.admin_dashboard, 1280, 800)

    def show_customer_dashboard(self):
        if self.login_window:
            self.login_window.destroy()
            self.login_window = None
        self.customer_dashboard = CustomerDashboard(
            self.root, self.system, on_logout=self._handle_customer_logout
        )
        center_window(self.customer_dashboard, 1280, 800)

    def _handle_customer_logout(self):
        self.system.logout_passenger()
        self.show_login()

    # ------------------------------------------------------------------
    def run(self):
        self.show_splash_then_login()
        self.root.mainloop()


def main():
    application = Application()
    application.run()


if __name__ == "__main__":
    main()
