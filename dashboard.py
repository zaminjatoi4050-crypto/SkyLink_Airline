"""
dashboard.py
------------
Main application shells for Admin and Customer roles: large top header,
modern sidebar navigation, and a content area that swaps between
feature pages. This is a CustomTkinter rewrite of the original
PySide6 QMainWindow-based shell.
"""

import customtkinter as ctk

from utils import COLORS, font, confirm, make_card, stat_card
from flight import FlightManagementPage
from booking import BookingPage
from reports import PassengersPage, AllBookingsPage, RevenueReportPage, StatisticsPage


class NavButton(ctk.CTkButton):
    """A sidebar navigation button that visually toggles between an
    'active' and 'inactive' state."""

    def __init__(self, parent, text, command):
        super().__init__(
            parent, text=text, command=command, anchor="w", height=42,
            corner_radius=10, font=font(13, "bold"),
            fg_color="transparent", hover_color=COLORS["bg_card_alt"],
            text_color=COLORS["text_secondary"],
        )

    def set_active(self, active: bool):
        if active:
            self.configure(fg_color=COLORS["accent_soft"], text_color=COLORS["white"])
        else:
            self.configure(fg_color="transparent", text_color=COLORS["text_secondary"])


class BaseDashboard(ctk.CTkToplevel):
    """Shared shell: large header + sidebar + swappable content area."""

    def __init__(self, master, app_title: str, user_label: str, on_logout):
        super().__init__(master)
        self.on_logout = on_logout
        self.title(app_title)
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["bg_root"])
        self.protocol("WM_DELETE_WINDOW", self._handle_exit)

        self._nav_buttons = {}
        self._pages = {}
        self._current_page_key = None

        self._build_shell(app_title, user_label)

    # ------------------------------------------------------------------
    def _build_shell(self, app_title, user_label):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ---- Large header / top bar ----
        topbar = ctk.CTkFrame(self, height=64, fg_color=COLORS["bg_panel"], corner_radius=0)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(topbar, text=app_title, font=font(18, "bold"),
                                    text_color=COLORS["text_primary"], anchor="w")
        title_label.grid(row=0, column=0, sticky="w", padx=24)

        user_widget = ctk.CTkLabel(topbar, text=f"\U0001F464  {user_label}", font=font(13),
                                    text_color=COLORS["text_secondary"], anchor="e")
        user_widget.grid(row=0, column=1, sticky="e", padx=24)

        # ---- Body: sidebar + content ----
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        sidebar = ctk.CTkFrame(body, width=230, fg_color=COLORS["bg_panel"], corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        self.sidebar_nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        self.sidebar_nav.pack(fill="x", padx=12, pady=(18, 0))

        self.sidebar_footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        self.sidebar_footer.pack(side="bottom", fill="x", padx=12, pady=18)

        self.content_area = ctk.CTkFrame(body, fg_color=COLORS["bg_root"], corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    def add_nav_page(self, key: str, label: str, page_widget):
        """Registers a page widget under `key`, creates its sidebar nav
        button, and places (but hides) the page in the content area."""
        page_widget.grid(row=0, column=0, sticky="nsew")
        page_widget.grid_remove()
        self._pages[key] = page_widget

        btn = NavButton(self.sidebar_nav, label, command=lambda: self.show_page(key))
        btn.pack(fill="x", pady=3)
        self._nav_buttons[key] = btn

        if self._current_page_key is None:
            self.show_page(key)

    def show_page(self, key: str):
        if self._current_page_key is not None:
            self._pages[self._current_page_key].grid_remove()
            self._nav_buttons[self._current_page_key].set_active(False)

        page = self._pages[key]
        page.grid()
        if hasattr(page, "refresh"):
            page.refresh()
        self._nav_buttons[key].set_active(True)
        self._current_page_key = key

    def add_logout_button(self):
        logout_btn = ctk.CTkButton(
            self.sidebar_footer, text="\u23FB  Logout", command=self._handle_logout,
            height=42, corner_radius=10, font=font(13, "bold"),
            fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
        )
        logout_btn.pack(fill="x")

    # ------------------------------------------------------------------
    def _handle_logout(self):
        if confirm(self, "Confirm Logout", "Are you sure you want to logout?"):
            self.on_logout()
            self.destroy()

    def _handle_exit(self):
        if confirm(self, "Exit", "Are you sure you want to exit?"):
            self.master.destroy()


# ===========================================================================
# ADMIN DASHBOARD
# ===========================================================================
class AdminOverviewPage(ctk.CTkFrame):
    """Premium admin landing dashboard with key stat cards."""

    def __init__(self, parent, system):
        super().__init__(parent, fg_color="transparent")
        self.system = system

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(24, 16))
        ctk.CTkLabel(header, text="Admin Dashboard", font=font(26, "bold"),
                     text_color=COLORS["text_primary"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(header, text="Welcome back. Here's what's happening with SkyLink Airlines.",
                     font=font(13), text_color=COLORS["text_muted"], anchor="w").pack(anchor="w", pady=(4, 0))

        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="x", padx=28, pady=10)

        labels = ["Total Flights", "Total Passengers", "Total Bookings",
                  "Available Seats", "Booked Seats"]
        self.value_labels = {}
        for i, label in enumerate(labels):
            card, value_label = stat_card(self.grid_frame, label, "0")
            self.value_labels[label] = value_label
            card.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="w")

        self.refresh()

    def refresh(self):
        result = self.system.flight_statics()
        stats = result.get("data", {}) or {}
        for label, value_label in self.value_labels.items():
            value_label.configure(text=str(stats.get(label, 0)))


class AdminDashboard(BaseDashboard):
    def __init__(self, master, system, on_logout):
        super().__init__(master, "SkyLink Airlines \u2014 Admin Dashboard", "Administrator", on_logout)

        self.overview_page = AdminOverviewPage(self.content_area, system)
        self.flight_page = FlightManagementPage(self.content_area, system)
        self.passengers_page = PassengersPage(self.content_area, system)
        self.bookings_page = AllBookingsPage(self.content_area, system)
        self.revenue_page = RevenueReportPage(self.content_area, system)
        self.stats_page = StatisticsPage(self.content_area, system)

        self.add_nav_page("overview", "\U0001F3E0  Dashboard", self.overview_page)
        self.add_nav_page("flights", "\u2708  Flight Management", self.flight_page)
        self.add_nav_page("passengers", "\U0001F465  Passengers", self.passengers_page)
        self.add_nav_page("bookings", "\U0001F4CB  Bookings", self.bookings_page)
        self.add_nav_page("revenue", "\U0001F4B0  Revenue Report", self.revenue_page)
        self.add_nav_page("stats", "\U0001F4CA  Statistics", self.stats_page)
        self.add_logout_button()


# ===========================================================================
# CUSTOMER DASHBOARD
# ===========================================================================
class CustomerOverviewPage(ctk.CTkFrame):
    def __init__(self, parent, system):
        super().__init__(parent, fg_color="transparent")
        self.system = system

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(24, 16))
        ctk.CTkLabel(header, text="Welcome to SkyLink Airlines", font=font(26, "bold"),
                     text_color=COLORS["text_primary"], anchor="w").pack(anchor="w")

        self.subtitle = ctk.CTkLabel(header, text="", font=font(13),
                                      text_color=COLORS["text_muted"], anchor="w",
                                      wraplength=600, justify="left")
        self.subtitle.pack(anchor="w", pady=(8, 0))

        self.refresh()

    def refresh(self):
        passenger = self.system.Current_Passenger
        name = passenger["passenger_name"] if passenger else "Guest"
        self.subtitle.configure(
            text=f"Hello, {name}! Use the menu on the left to browse flights, "
                 "book tickets, and manage your bookings."
        )


class CustomerDashboard(BaseDashboard):
    def __init__(self, master, system, on_logout):
        passenger_name = system.Current_Passenger["passenger_name"] if system.Current_Passenger else "Guest"
        super().__init__(master, "SkyLink Airlines \u2014 Customer Dashboard", passenger_name, on_logout)

        self.overview_page = CustomerOverviewPage(self.content_area, system)
        self.booking_page = BookingPage(self.content_area, system)

        self.add_nav_page("home", "\U0001F3E0  Home", self.overview_page)
        self.add_nav_page("booking", "\u2708  Flights & Bookings", self.booking_page)
        self.add_logout_button()
