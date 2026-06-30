"""
reports.py
----------
Admin reporting pages: Passenger directory, all-bookings view, revenue
report, and flight statistics dashboard. Wraps database.SkyLinkSystem
reporting methods without altering their logic.
"""

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from utils import COLORS, font, secondary_button, stat_card

PASSENGER_COLUMNS = ["Name", "Email", "CNIC", "Phone", "Age", "Gender"]
BOOKING_COLUMNS = ["Booking ID", "Passenger Name", "Passenger Email",
                    "Flight No.", "Booking Date", "Status", "Price"]


def _build_table(parent, columns):
    """Helper that builds a themed, scrollable ttk.Treeview and returns it."""
    table_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=14,
                                border_width=1, border_color=COLORS["border"])
    table_frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                         style="Sky.Treeview", selectmode="browse")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=110, stretch=True)
    tree.pack(fill="both", expand=True, padx=10, pady=10, side="left")

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y", pady=10)
    return tree


class PassengersPage(ctk.CTkFrame):
    """Admin page: read-only directory of all registered passengers."""

    def __init__(self, parent, system):
        super().__init__(parent, fg_color="transparent")
        self.system = system

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=28, pady=24)

        ctk.CTkLabel(wrap, text="Passenger Directory", font=font(24, "bold"),
                     text_color=COLORS["text_primary"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(wrap, text="All registered passengers", font=font(13),
                     text_color=COLORS["text_muted"], anchor="w").pack(anchor="w", pady=(4, 12))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh())
        search_entry = ctk.CTkEntry(
            wrap, textvariable=self.search_var, placeholder_text="Search by email...",
            height=38, fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], corner_radius=8,
        )
        search_entry.pack(fill="x", pady=(0, 12))

        self.tree = _build_table(wrap, PASSENGER_COLUMNS)
        self.refresh()

    def refresh(self):
        query = self.search_var.get().strip().lower()
        result = self.system.view_passengers()
        passengers = result.get("data", []) or []
        if query:
            passengers = [p for p in passengers if query in p["passenger_email"].lower()]

        self.tree.delete(*self.tree.get_children())
        for i, p in enumerate(passengers):
            values = (p["passenger_name"], p["passenger_email"], p["passenger_CNIC"],
                      p["passenger_phone"], str(p["passenger_age"]), p["passenger_gender"])
            self.tree.insert("", "end", iid=f"p{i}", values=values)


class AllBookingsPage(ctk.CTkFrame):
    """Admin page: read-only view of every booking made across the system."""

    def __init__(self, parent, system):
        super().__init__(parent, fg_color="transparent")
        self.system = system

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=28, pady=24)

        ctk.CTkLabel(wrap, text="All Bookings", font=font(24, "bold"),
                     text_color=COLORS["text_primary"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(wrap, text="Every booking made across the system", font=font(13),
                     text_color=COLORS["text_muted"], anchor="w").pack(anchor="w", pady=(4, 12))

        self.tree = _build_table(wrap, BOOKING_COLUMNS)
        self.refresh()

    def refresh(self):
        result = self.system.view_all_bookings()
        bookings = result.get("data", []) or []
        self.tree.delete(*self.tree.get_children())
        for b in bookings:
            values = (str(b["booking_id"]), b["passenger_name"], b["passenger_email"],
                      b["flight_number"], b["booking_date"], b["booking_status"],
                      f"${b['price']:.2f}")
            self.tree.insert("", "end", iid=str(b["booking_id"]), values=values)


class RevenueReportPage(ctk.CTkFrame):
    """Admin page: total revenue generated from confirmed bookings."""

    def __init__(self, parent, system):
        super().__init__(parent, fg_color="transparent")
        self.system = system

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=28, pady=24)

        ctk.CTkLabel(wrap, text="Revenue Report", font=font(24, "bold"),
                     text_color=COLORS["text_primary"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(wrap, text="Total revenue generated from confirmed bookings", font=font(13),
                     text_color=COLORS["text_muted"], anchor="w").pack(anchor="w", pady=(4, 16))

        self.card, self.value_label = stat_card(wrap, "Total Revenue", "$0.00")
        self.card.pack(anchor="w")

        refresh_btn = secondary_button(wrap, "Refresh", self.refresh, width=140)
        refresh_btn.pack(anchor="w", pady=(16, 0))

        self.refresh()

    def refresh(self):
        result = self.system.revenu_report()
        total = result.get("data", 0) or 0
        self.value_label.configure(text=f"${total:.2f}")


class StatisticsPage(ctk.CTkFrame):
    """Admin page: system-wide flight and booking statistics."""

    def __init__(self, parent, system):
        super().__init__(parent, fg_color="transparent")
        self.system = system

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=28, pady=24)

        ctk.CTkLabel(wrap, text="Flight Statistics", font=font(24, "bold"),
                     text_color=COLORS["text_primary"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(wrap, text="System-wide flight and booking statistics", font=font(13),
                     text_color=COLORS["text_muted"], anchor="w").pack(anchor="w", pady=(4, 16))

        self.grid_frame = ctk.CTkFrame(wrap, fg_color="transparent")
        self.grid_frame.pack(fill="x")

        labels = ["Total Flights", "Total Passengers", "Total Bookings",
                  "Available Seats", "Booked Seats"]
        self.value_labels = {}
        for i, label in enumerate(labels):
            card, value_label = stat_card(self.grid_frame, label, "0")
            self.value_labels[label] = value_label
            card.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="w")

        refresh_btn = secondary_button(wrap, "Refresh", self.refresh, width=140)
        refresh_btn.pack(anchor="w", pady=(16, 0))

        self.refresh()

    def refresh(self):
        result = self.system.flight_statics()
        stats = result.get("data", {}) or {}
        for label, value_label in self.value_labels.items():
            value_label.configure(text=str(stats.get(label, 0)))
