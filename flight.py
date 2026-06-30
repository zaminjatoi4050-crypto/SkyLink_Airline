"""
flight.py
---------
Admin-facing flight management page: add, view, search, update, and
delete flights using a themed ttk.Treeview table. Wraps
database.SkyLinkSystem flight methods without altering their logic.
"""

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from utils import (
    COLORS, font, show_error, show_success, confirm,
    primary_button, secondary_button, success_button, danger_button,
)

FLIGHT_COLUMNS = [
    "Flight No.", "Origin", "Destination", "Departure", "Arrival",
    "Price", "Total Seats", "Available", "Status", "Gate", "Terminal"
]


class FlightFormDialog(ctk.CTkToplevel):
    """Add / Update flight dialog. Calling .show() blocks until the
    dialog is closed and returns the entered values dict, or None if
    the user cancelled."""

    def __init__(self, parent, flight=None):
        super().__init__(parent)
        self.flight = flight
        self.result = None
        self.title("Update Flight" if flight else "Add New Flight")
        self.geometry("460x680")
        self.configure(fg_color=COLORS["bg_panel"])
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        if flight:
            self._populate(flight)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    # ------------------------------------------------------------------
    def _field(self, parent, label_text):
        ctk.CTkLabel(parent, text=label_text, font=font(12, "bold"),
                     text_color=COLORS["text_secondary"], anchor="w").pack(anchor="w", pady=(10, 4))
        entry = ctk.CTkEntry(
            parent, height=36, fg_color=COLORS["bg_input"],
            border_color=COLORS["border"], text_color=COLORS["text_primary"], corner_radius=8,
        )
        entry.pack(fill="x")
        return entry

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        self.flight_number = self._field(scroll, "Flight Number")
        self.origin = self._field(scroll, "Origin")
        self.destination = self._field(scroll, "Destination")
        self.departure_time = self._field(scroll, "Departure Time (e.g. 14:30)")
        self.arrival_time = self._field(scroll, "Arrival Time (e.g. 17:45)")
        self.price = self._field(scroll, "Price")
        self.total_seats = self._field(scroll, "Total Seats")

        ctk.CTkLabel(scroll, text="Status", font=font(12, "bold"),
                     text_color=COLORS["text_secondary"], anchor="w").pack(anchor="w", pady=(10, 4))
        self.status = ctk.CTkOptionMenu(
            scroll, values=["On Time", "Delayed", "Cancelled"], height=36,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"], text_color=COLORS["text_primary"],
            dropdown_fg_color=COLORS["bg_card_alt"], corner_radius=8,
        )
        self.status.set("On Time")
        self.status.pack(fill="x")

        self.gate_number = self._field(scroll, "Gate Number")
        self.terminal = self._field(scroll, "Terminal")

        # If updating, lock fields whose values are not safe to change
        # (mirrors original PySide6 behavior exactly).
        if self.flight:
            self.flight_number.configure(state="disabled")
            self.total_seats.configure(state="disabled")
            self.status.configure(state="disabled")
            self.gate_number.configure(state="disabled")
            self.terminal.configure(state="disabled")

        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", pady=(20, 0))
        cancel_btn = secondary_button(btn_row, "Cancel", self._on_cancel, width=120)
        cancel_btn.pack(side="left")
        save_btn = success_button(btn_row, "Save", self._on_save, width=120)
        save_btn.pack(side="right")

    def _populate(self, flight):
        self.flight_number.insert(0, flight["flight_number"])
        self.origin.insert(0, flight["origin"])
        self.destination.insert(0, flight["destination"])
        self.departure_time.insert(0, flight["departure_time"])
        self.arrival_time.insert(0, flight["arrival_time"])
        self.price.insert(0, str(flight["price"]))
        self.total_seats.insert(0, str(flight["total_seats"]))
        self.status.set(flight["status"])
        self.gate_number.insert(0, flight["gate_number"])
        self.terminal.insert(0, flight["terminal"])

    def _on_save(self):
        self.result = {
            "flight_number": self.flight_number.get().strip(),
            "origin": self.origin.get().strip(),
            "destination": self.destination.get().strip(),
            "departure_time": self.departure_time.get().strip(),
            "arrival_time": self.arrival_time.get().strip(),
            "price": self.price.get().strip(),
            "total_seats": self.total_seats.get().strip(),
            "status": self.status.get(),
            "gate_number": self.gate_number.get().strip(),
            "terminal": self.terminal.get().strip(),
        }
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def show(self):
        self.wait_window(self)
        return self.result


class FlightManagementPage(ctk.CTkFrame):
    """Admin page: Add / View / Search / Update / Delete flights."""

    def __init__(self, parent, system):
        super().__init__(parent, fg_color="transparent")
        self.system = system
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=28, pady=24)

        # Header row with title + Add Flight button
        header = ctk.CTkFrame(wrap, fg_color="transparent")
        header.pack(fill="x")

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", anchor="w")
        ctk.CTkLabel(title_box, text="Flight Management", font=font(24, "bold"),
                     text_color=COLORS["text_primary"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(title_box, text="Add, search, update and remove flights",
                     font=font(13), text_color=COLORS["text_muted"], anchor="w").pack(anchor="w", pady=(4, 0))

        add_btn = primary_button(header, "+ Add Flight", self._add_flight, width=150)
        add_btn.pack(side="right")

        # Search box
        search_row = ctk.CTkFrame(wrap, fg_color="transparent")
        search_row.pack(fill="x", pady=(16, 12))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh())
        search_entry = ctk.CTkEntry(
            search_row, textvariable=self.search_var, placeholder_text="Search by flight number...",
            height=38, fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], corner_radius=8,
        )
        search_entry.pack(fill="x")

        # Table
        table_frame = ctk.CTkFrame(wrap, fg_color=COLORS["bg_card"], corner_radius=14,
                                    border_width=1, border_color=COLORS["border"])
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            table_frame, columns=FLIGHT_COLUMNS, show="headings",
            style="Sky.Treeview", selectmode="browse",
        )
        for col in FLIGHT_COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100, stretch=True)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10, side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Action buttons
        action_row = ctk.CTkFrame(wrap, fg_color="transparent")
        action_row.pack(fill="x", pady=(12, 0))
        update_btn = secondary_button(action_row, "Update Selected", self._update_flight, width=160)
        update_btn.pack(side="left")
        delete_btn = danger_button(action_row, "Delete Selected", self._delete_flight, width=160)
        delete_btn.pack(side="left", padx=(10, 0))

    # ------------------------------------------------------------------
    def refresh(self):
        query = self.search_var.get().strip().lower()
        result = self.system.view_flights()
        flights = result.get("data", []) or []

        if query:
            flights = [f for f in flights if query in f["flight_number"].lower()]

        self.tree.delete(*self.tree.get_children())
        for flight in flights:
            values = (
                flight["flight_number"], flight["origin"], flight["destination"],
                flight["departure_time"], flight["arrival_time"], f"${flight['price']:.2f}",
                str(flight["total_seats"]), str(flight["Available_seats"]),
                flight["status"], flight["gate_number"], flight["terminal"],
            )
            self.tree.insert("", "end", iid=flight["flight_number"], values=values)

    def _selected_flight_number(self):
        selection = self.tree.selection()
        if not selection:
            return None
        return selection[0]

    def _add_flight(self):
        dialog = FlightFormDialog(self)
        values = dialog.show()
        if values is None:
            return

        try:
            price = float(values["price"])
        except (TypeError, ValueError):
            show_error(self, "Invalid Price", "Price must be numeric.")
            return
        try:
            total_seats = int(values["total_seats"])
        except (TypeError, ValueError):
            show_error(self, "Invalid Seats", "Total Seats must be a whole number.")
            return

        result = self.system.add_flight(
            values["flight_number"], values["origin"], values["destination"],
            values["departure_time"], values["arrival_time"], price,
            total_seats, values["status"], values["gate_number"], values["terminal"]
        )
        if result["success"]:
            show_success(self, "Flight Added", result["message"])
            self.refresh()
        else:
            show_error(self, "Add Flight Failed", result["message"])

    def _update_flight(self):
        flight_number = self._selected_flight_number()
        if not flight_number:
            show_error(self, "No Selection", "Please select a flight to update.")
            return
        result = self.system.search_flight(flight_number)
        if not result["success"]:
            show_error(self, "Not Found", result["message"])
            return

        dialog = FlightFormDialog(self, flight=result["data"])
        values = dialog.show()
        if values is None:
            return

        try:
            price = float(values["price"])
        except (TypeError, ValueError):
            show_error(self, "Invalid Price", "Price must be numeric.")
            return

        upd = self.system.update_flight(
            flight_number, values["origin"], values["destination"],
            values["departure_time"], values["arrival_time"], price
        )
        if upd["success"]:
            show_success(self, "Flight Updated", upd["message"])
            self.refresh()
        else:
            show_error(self, "Update Failed", upd["message"])

    def _delete_flight(self):
        flight_number = self._selected_flight_number()
        if not flight_number:
            show_error(self, "No Selection", "Please select a flight to delete.")
            return
        if confirm(self, "Confirm Delete", f"Delete flight {flight_number}? This cannot be undone."):
            result = self.system.delete_flight(flight_number)
            if result["success"]:
                show_success(self, "Flight Deleted", result["message"])
                self.refresh()
            else:
                show_error(self, "Delete Failed", result["message"])
