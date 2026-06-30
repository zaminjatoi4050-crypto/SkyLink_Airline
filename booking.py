"""
booking.py
----------
Customer-facing booking page: browse/search flights, book a ticket,
view "My Bookings", cancel a booking, and display the professional
booking receipt. Wraps database.SkyLinkSystem booking methods without
altering their logic.
"""

import datetime
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from utils import (
    COLORS, font, show_error, show_success, confirm,
    primary_button, secondary_button, success_button, danger_button, make_card,
)

FLIGHT_COLUMNS = [
    "Flight No.", "Origin", "Destination", "Departure", "Arrival",
    "Price", "Available", "Status", "Gate", "Terminal"
]

MY_BOOKING_COLUMNS = ["Booking ID", "Flight No.", "Booking Date", "Status", "Price"]


class ReceiptDialog(ctk.CTkToplevel):
    """Beautiful, professional booking receipt shown after a booking."""

    def __init__(self, parent, booking, flight):
        super().__init__(parent)
        self.title("Booking Receipt")
        self.geometry("460x640")
        self.configure(fg_color=COLORS["bg_panel"])
        self.transient(parent)
        self.grab_set()

        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=16, pady=16)

        card = make_card(outer, fg_color=COLORS["bg_card"])
        card.pack(fill="both", expand=True)

        card_inner = ctk.CTkFrame(card, fg_color="transparent")
        card_inner.pack(fill="both", expand=True, padx=28, pady=24)

        header = ctk.CTkLabel(card_inner, text="\u2708 SKYLINK AIRLINES", font=font(18, "bold"),
                               text_color=COLORS["accent"], anchor="center")
        header.pack(fill="x")
        sub = ctk.CTkLabel(card_inner, text="BOOKING RECEIPT", font=font(11, "bold"),
                            text_color=COLORS["text_muted"], anchor="center")
        sub.pack(fill="x", pady=(0, 10))
        self._divider(card_inner)

        def row(label, value):
            r = ctk.CTkFrame(card_inner, fg_color="transparent")
            r.pack(fill="x", pady=3)
            ctk.CTkLabel(r, text=label, font=font(12), text_color=COLORS["text_muted"],
                         anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=str(value), font=font(12, "bold"), text_color=COLORS["text_primary"],
                         anchor="e").pack(side="right")

        row("Booking ID", booking["booking_id"])
        row("Passenger Name", booking["passenger_name"])
        row("Passenger Email", booking["passenger_email"])
        self._divider(card_inner)
        row("Flight Number", flight["flight_number"])
        row("Origin", flight["origin"])
        row("Destination", flight["destination"])
        row("Departure Time", flight["departure_time"])
        row("Arrival Time", flight["arrival_time"])
        row("Gate", flight["gate_number"])
        row("Terminal", flight["terminal"])
        self._divider(card_inner)
        row("Booking Date", booking["booking_date"])
        row("Booking Status", booking["booking_status"])
        row("Ticket Price", f"${booking['price']:.2f}")
        self._divider(card_inner)

        footer = ctk.CTkLabel(
            card_inner, text="Thank you for choosing SkyLink Airlines!\nHave a Safe Journey.",
            font=font(11), text_color=COLORS["text_muted"], justify="center",
        )
        footer.pack(fill="x", pady=(8, 0))

        close_btn = primary_button(outer, "Close", self.destroy, width=140)
        close_btn.pack(pady=(14, 0))

    def _divider(self, parent):
        line = ctk.CTkFrame(parent, height=1, fg_color=COLORS["border"])
        line.pack(fill="x", pady=8)


class BookTicketDialog(ctk.CTkToplevel):
    """Small dialog to confirm a booking date for a given flight."""

    def __init__(self, parent, flight_number):
        super().__init__(parent)
        self.result = None
        self.title(f"Book Flight {flight_number}")
        self.geometry("380x240")
        self.configure(fg_color=COLORS["bg_panel"])
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(wrap, text="Booking Date", font=font(12, "bold"),
                     text_color=COLORS["text_secondary"], anchor="w").pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(wrap, text="Format: YYYY-MM-DD", font=font(10),
                     text_color=COLORS["text_muted"], anchor="w").pack(anchor="w", pady=(0, 6))

        self.date_entry = ctk.CTkEntry(
            wrap, height=38, fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], corner_radius=8,
        )
        self.date_entry.insert(0, datetime.date.today().isoformat())
        self.date_entry.pack(fill="x")

        btn_row = ctk.CTkFrame(wrap, fg_color="transparent")
        btn_row.pack(fill="x", pady=(24, 0))
        secondary_button(btn_row, "Cancel", self._on_cancel, width=120).pack(side="left")
        success_button(btn_row, "Confirm Booking", self._on_confirm, width=160).pack(side="right")

    def _on_confirm(self):
        self.result = self.date_entry.get().strip()
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def show(self):
        self.wait_window(self)
        return self.result


class BookingPage(ctk.CTkFrame):
    """Customer page combining flight browsing/booking and my bookings."""

    def __init__(self, parent, system):
        super().__init__(parent, fg_color="transparent")
        self.system = system
        self._build_ui()
        self.refresh_flights()
        self.refresh_my_bookings()

    def refresh(self):
        """Called by the dashboard shell whenever this page is shown."""
        self.refresh_flights()
        self.refresh_my_bookings()

    def _build_ui(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=28, pady=24)

        ctk.CTkLabel(wrap, text="Flights & Bookings", font=font(24, "bold"),
                     text_color=COLORS["text_primary"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(wrap, text="Search flights, book tickets, and manage your bookings",
                     font=font(13), text_color=COLORS["text_muted"], anchor="w").pack(anchor="w", pady=(4, 14))

        self.tabs = ctk.CTkTabview(
            wrap, fg_color=COLORS["bg_card"], segmented_button_fg_color=COLORS["bg_card_alt"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["bg_card_alt"],
            text_color=COLORS["text_primary"], corner_radius=14,
        )
        self.tabs.pack(fill="both", expand=True)
        self.tabs.add("Available Flights")
        self.tabs.add("My Bookings")

        self._build_flights_tab(self.tabs.tab("Available Flights"))
        self._build_my_bookings_tab(self.tabs.tab("My Bookings"))

    # ------------------------------------------------------------------
    def _build_flights_tab(self, page):
        page.grid_rowconfigure(1, weight=1)
        page.grid_columnconfigure(0, weight=1)

        search_row = ctk.CTkFrame(page, fg_color="transparent")
        search_row.grid(row=0, column=0, sticky="ew", pady=(4, 10))
        self.flight_search_var = tk.StringVar()
        self.flight_search_var.trace_add("write", lambda *a: self.refresh_flights())
        search_entry = ctk.CTkEntry(
            search_row, textvariable=self.flight_search_var,
            placeholder_text="Search by flight number...", height=36,
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], corner_radius=8,
        )
        search_entry.pack(fill="x")

        table_frame = ctk.CTkFrame(page, fg_color=COLORS["bg_card_alt"], corner_radius=12)
        table_frame.grid(row=1, column=0, sticky="nsew")

        self.flight_tree = ttk.Treeview(
            table_frame, columns=FLIGHT_COLUMNS, show="headings",
            style="Sky.Treeview", selectmode="browse",
        )
        for col in FLIGHT_COLUMNS:
            self.flight_tree.heading(col, text=col)
            self.flight_tree.column(col, anchor="center", width=95, stretch=True)
        self.flight_tree.pack(fill="both", expand=True, padx=8, pady=8, side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.flight_tree.yview)
        self.flight_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", pady=8)

        book_btn = primary_button(page, "Book Selected Flight", self._book_selected, width=220)
        book_btn.grid(row=2, column=0, sticky="w", pady=(10, 0))

    def refresh_flights(self):
        query = self.flight_search_var.get().strip().lower()
        result = self.system.view_flights()
        flights = result.get("data", []) or []
        if query:
            flights = [f for f in flights if query in f["flight_number"].lower()]

        self.flight_tree.delete(*self.flight_tree.get_children())
        for flight in flights:
            values = (
                flight["flight_number"], flight["origin"], flight["destination"],
                flight["departure_time"], flight["arrival_time"], f"${flight['price']:.2f}",
                str(flight["Available_seats"]), flight["status"],
                flight["gate_number"], flight["terminal"],
            )
            self.flight_tree.insert("", "end", iid=flight["flight_number"], values=values)

    def _book_selected(self):
        selection = self.flight_tree.selection()
        if not selection:
            show_error(self, "No Selection", "Please select a flight to book.")
            return
        flight_number = selection[0]

        dialog = BookTicketDialog(self, flight_number)
        booking_date = dialog.show()
        if booking_date is None:
            return

        result = self.system.book_ticket(flight_number, booking_date)
        if result["success"]:
            booking = result["data"]["booking"]
            flight = result["data"]["flight"]
            show_success(self, "Booking Confirmed", result["message"])
            ReceiptDialog(self, booking, flight)
            self.refresh_flights()
            self.refresh_my_bookings()
        else:
            show_error(self, "Booking Failed", result["message"])

    # ------------------------------------------------------------------
    def _build_my_bookings_tab(self, page):
        page.grid_rowconfigure(0, weight=1)
        page.grid_columnconfigure(0, weight=1)

        table_frame = ctk.CTkFrame(page, fg_color=COLORS["bg_card_alt"], corner_radius=12)
        table_frame.grid(row=0, column=0, sticky="nsew", pady=(4, 10))

        self.bookings_tree = ttk.Treeview(
            table_frame, columns=MY_BOOKING_COLUMNS, show="headings",
            style="Sky.Treeview", selectmode="browse",
        )
        for col in MY_BOOKING_COLUMNS:
            self.bookings_tree.heading(col, text=col)
            self.bookings_tree.column(col, anchor="center", width=110, stretch=True)
        self.bookings_tree.pack(fill="both", expand=True, padx=8, pady=8, side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", pady=8)

        cancel_btn = danger_button(page, "Cancel Selected Booking", self._cancel_selected, width=220)
        cancel_btn.grid(row=1, column=0, sticky="w")

    def refresh_my_bookings(self):
        result = self.system.My_Bookings()
        bookings = result.get("data", []) or []
        self.bookings_tree.delete(*self.bookings_tree.get_children())
        for booking in bookings:
            values = (
                str(booking["booking_id"]), booking["flight_number"],
                booking["booking_date"], booking["booking_status"],
                f"${booking['price']:.2f}",
            )
            # iid encodes both booking id and flight number so cancel
            # can recover the flight number without re-querying.
            self.bookings_tree.insert(
                "", "end", iid=f"{booking['booking_id']}::{booking['flight_number']}", values=values
            )

    def _cancel_selected(self):
        selection = self.bookings_tree.selection()
        if not selection:
            show_error(self, "No Selection", "Please select a booking to cancel.")
            return
        flight_number = selection[0].split("::", 1)[1]
        if confirm(self, "Confirm Cancellation", f"Cancel booking for flight {flight_number}?"):
            result = self.system.cancel_booking(flight_number)
            if result["success"]:
                show_success(self, "Booking Cancelled", result["message"])
                self.refresh_my_bookings()
                self.refresh_flights()
            else:
                show_error(self, "Cancellation Failed", result["message"])
