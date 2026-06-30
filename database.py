"""
database.py
------------
Backend / business-logic layer for SkyLink Airlines Reservation System.

This module is a direct, faithful refactor of the original console
application. Every validation rule, field name, and piece of business
logic from the original script has been preserved exactly. The only
change is structural: instead of calling input()/print() directly,
each method accepts plain arguments and returns a result dictionary
of the form:

    {"success": bool, "message": str, "data": <optional>}

so that a GUI layer (PySide6) can drive the same logic that used to be
driven by the console menus.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


class SkyLinkSystem:
    """Holds all application state and business logic for SkyLink Airlines.

    Mirrors the original module-level globals:
        FLIGHTS, PASSENGERS, BOOKINGS, Current_Passenger, NEXT_BOOKING_ID
    """

    ADMIN_USERNAME = "admin@SkyAirline.com"
    ADMIN_PASSWORD = "SkyAirline@786"

    def __init__(self):
        self.FLIGHTS: List[Dict] = []
        self.PASSENGERS: List[Dict] = []
        self.BOOKINGS: List[Dict] = []
        self.Current_Passenger: Optional[Dict] = None
        self.NEXT_BOOKING_ID: int = 1

    # ------------------------------------------------------------------
    # ADMIN AUTHENTICATION
    # ------------------------------------------------------------------
    def admin_login(self, username: str, password: str) -> Dict:
        """Validate admin credentials. Logic preserved from original."""
        if username == self.ADMIN_USERNAME and password == self.ADMIN_PASSWORD:
            return {"success": True, "message": "Admin login successful!"}
        return {"success": False, "message": "Invalid admin credentials."}

    # ------------------------------------------------------------------
    # FLIGHT MANAGEMENT (Admin)
    # ------------------------------------------------------------------
    def add_flight(self, flight_number, origin, destination, departure_time,
                    arrival_time, price, total_seats, status, gate_number,
                    terminal) -> Dict:
        """Add a new flight. Preserves duplicate flight-number and
        origin != destination validation from the original script."""

        if any(flight['flight_number'] == flight_number for flight in self.FLIGHTS):
            return {"success": False,
                    "message": "Flight number already exists. Please enter a unique flight number."}

        if origin == destination:
            return {"success": False,
                    "message": "Origin and destination cannot be the same. Please enter different values."}

        try:
            price = float(price)
            total_seats = int(total_seats)
        except (TypeError, ValueError):
            return {"success": False, "message": "Price and Total Seats must be numeric."}

        available_seats = total_seats

        flight = {
            "flight_number": flight_number,
            "origin": origin,
            "destination": destination,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "price": price,
            "total_seats": total_seats,
            "Available_seats": available_seats,
            "status": status,
            "gate_number": gate_number,
            "terminal": terminal,
        }

        self.FLIGHTS.append(flight)
        return {"success": True, "message": "Flight added successfully!", "data": flight}

    def view_flights(self) -> Dict:
        if not self.FLIGHTS:
            return {"success": False, "message": "No flights available.", "data": []}
        return {"success": True, "message": "", "data": self.FLIGHTS}

    def search_flight(self, flight_number: str) -> Dict:
        for flight in self.FLIGHTS:
            if flight['flight_number'] == flight_number:
                return {"success": True, "message": "", "data": flight}
        return {"success": False, "message": "Flight not found.", "data": None}

    def update_flight(self, flight_number, origin, destination,
                       departure_time, arrival_time, price) -> Dict:
        for flight in self.FLIGHTS:
            if flight['flight_number'] == flight_number:
                flight['origin'] = origin
                flight['destination'] = destination
                flight['departure_time'] = departure_time
                flight['arrival_time'] = arrival_time
                try:
                    flight['price'] = float(price)
                except (TypeError, ValueError):
                    return {"success": False, "message": "Price must be numeric."}
                return {"success": True, "message": "Flight updated successfully!", "data": flight}
        return {"success": False, "message": "Flight not found."}

    def delete_flight(self, flight_number: str) -> Dict:
        for flight in self.FLIGHTS:
            if flight['flight_number'] == flight_number:
                self.FLIGHTS.remove(flight)
                return {"success": True, "message": "Flight deleted successfully!"}
        return {"success": False, "message": "Flight not found."}

    # ------------------------------------------------------------------
    # PASSENGER MANAGEMENT (Admin view)
    # ------------------------------------------------------------------
    def view_passengers(self) -> Dict:
        if not self.PASSENGERS:
            return {"success": False, "message": "No passengers registered.", "data": []}
        return {"success": True, "message": "", "data": self.PASSENGERS}

    def search_passenger(self, passenger_email: str) -> Dict:
        for passenger in self.PASSENGERS:
            if passenger['passenger_email'] == passenger_email:
                return {"success": True, "message": "", "data": passenger}
        return {"success": False, "message": "Passenger not found.", "data": None}

    # ------------------------------------------------------------------
    # BOOKING MANAGEMENT (Admin view)
    # ------------------------------------------------------------------
    def view_all_bookings(self) -> Dict:
        if not self.BOOKINGS:
            return {"success": False, "message": "No bookings found.", "data": []}
        return {"success": True, "message": "", "data": self.BOOKINGS}

    # ------------------------------------------------------------------
    # REPORTS (Admin)
    # ------------------------------------------------------------------
    def revenu_report(self) -> Dict:
        total_revenue = sum(booking['price'] for booking in self.BOOKINGS)
        return {"success": True, "message": "", "data": total_revenue}

    def flight_statics(self) -> Dict:
        stats = {
            "Total Flights": len(self.FLIGHTS),
            "Total Passengers": len(self.PASSENGERS),
            "Total Bookings": len(self.BOOKINGS),
            "Available Seats": sum(flight['Available_seats'] for flight in self.FLIGHTS),
            "Booked Seats": sum(flight['total_seats'] - flight['Available_seats'] for flight in self.FLIGHTS),
        }
        return {"success": True, "message": "", "data": stats}

    # ------------------------------------------------------------------
    # PASSENGER REGISTRATION / AUTHENTICATION
    # ------------------------------------------------------------------
    def register_passenger(self, passenger_name, passenger_email, passenger_password,
                            passenger_CNIC, passenger_phone, passenger_age,
                            passenger_gender) -> Dict:

        if passenger_name == "":
            return {"success": False, "message": "Name cannot be empty. Please enter a valid name."}

        if any(p['passenger_email'] == passenger_email for p in self.PASSENGERS):
            return {"success": False, "message": "Email already registered. Please use a different email."}

        if any(p['passenger_CNIC'] == passenger_CNIC for p in self.PASSENGERS):
            return {"success": False, "message": "CNIC already registered. Please use a different CNIC."}

        if any(p['passenger_phone'] == passenger_phone for p in self.PASSENGERS):
            return {"success": False, "message": "Phone number already registered. Please use a different phone number."}

        try:
            passenger_age = int(passenger_age)
        except (TypeError, ValueError):
            return {"success": False, "message": "Invalid age. Please enter a valid age."}

        if passenger_age < 0 or passenger_age > 120:
            return {"success": False, "message": "Invalid age. Please enter a valid age."}

        passenger = {
            "passenger_name": passenger_name,
            "passenger_email": passenger_email,
            "passenger_password": passenger_password,
            "passenger_CNIC": passenger_CNIC,
            "passenger_phone": passenger_phone,
            "passenger_age": passenger_age,
            "passenger_gender": passenger_gender,
        }

        self.PASSENGERS.append(passenger)
        return {"success": True, "message": "Passenger registered successfully!", "data": passenger}

    def login_passenger(self, passenger_email, passenger_password) -> Dict:
        for passenger in self.PASSENGERS:
            if passenger['passenger_email'] == passenger_email and passenger['passenger_password'] == passenger_password:
                self.Current_Passenger = passenger
                return {"success": True, "message": "Passenger login successful!", "data": passenger}
        return {"success": False, "message": "Invalid email or password."}

    def logout_passenger(self) -> Dict:
        self.Current_Passenger = None
        return {"success": True, "message": "Passenger logged out successfully."}

    # ------------------------------------------------------------------
    # BOOKING MANAGEMENT (Customer)
    # ------------------------------------------------------------------
    def book_ticket(self, flight_number: str, booking_date: str) -> Dict:
        if self.Current_Passenger is None:
            return {"success": False, "message": "Please login first."}

        if not self.FLIGHTS:
            return {"success": False, "message": "No flights available for booking."}

        for flight in self.FLIGHTS:
            if flight["flight_number"] == flight_number:

                if flight["Available_seats"] <= 0:
                    return {"success": False, "message": "No available seats on this flight."}

                booking = {
                    "booking_id": self.NEXT_BOOKING_ID,
                    "flight_number": flight["flight_number"],
                    "passenger_name": self.Current_Passenger["passenger_name"],
                    "passenger_email": self.Current_Passenger["passenger_email"],
                    "booking_date": booking_date,
                    "booking_status": "Confirmed",
                    "price": flight["price"],
                }

                self.BOOKINGS.append(booking)
                flight["Available_seats"] -= 1
                self.NEXT_BOOKING_ID += 1

                return {
                    "success": True,
                    "message": "Ticket booked successfully!",
                    "data": {"booking": booking, "flight": flight},
                }

        return {"success": False, "message": "Flight not found."}

    def My_Bookings(self) -> Dict:
        if self.Current_Passenger is None:
            return {"success": False, "message": "Please login first.", "data": []}

        my_bookings = [b for b in self.BOOKINGS
                       if b['passenger_email'] == self.Current_Passenger["passenger_email"]]

        if not my_bookings:
            return {"success": False, "message": "No bookings found for the current passenger.", "data": []}

        return {"success": True, "message": "", "data": my_bookings}

    def cancel_booking(self, flight_number: str) -> Dict:
        if self.Current_Passenger is None:
            return {"success": False, "message": "Please login first."}

        for booking in self.BOOKINGS:
            if (booking["flight_number"] == flight_number and
                    booking["passenger_email"] == self.Current_Passenger["passenger_email"]):

                self.BOOKINGS.remove(booking)

                for flight in self.FLIGHTS:
                    if flight["flight_number"] == flight_number:
                        flight["Available_seats"] += 1
                        break

                return {"success": True, "message": "Booking canceled successfully!"}

        return {"success": False, "message": "Booking not found."}

    # ------------------------------------------------------------------
    # RECEIPT
    # ------------------------------------------------------------------
    def booking_receipt(self, booking: Dict, flight: Dict) -> str:
        """Builds the same text receipt as the original console version,
        returned as a string so the GUI can render it in a dialog."""
        lines = [
            "===================================================",
            "                 SKYLINK AIRLINES",
            "                  BOOKING RECEIPT",
            "===================================================",
            f"Booking ID       : {booking['booking_id']}",
            f"Passenger Name   : {booking['passenger_name']}",
            f"Passenger Email  : {booking['passenger_email']}",
            "-----------------------------------------------",
            f"Flight Number    : {flight['flight_number']}",
            f"Origin           : {flight['origin']}",
            f"Destination      : {flight['destination']}",
            f"Departure Time   : {flight['departure_time']}",
            f"Arrival Time     : {flight['arrival_time']}",
            f"Gate Number      : {flight['gate_number']}",
            f"Terminal         : {flight['terminal']}",
            "-----------------------------------------------",
            f"Booking Date     : {booking['booking_date']}",
            f"Booking Status   : {booking['booking_status']}",
            f"Ticket Price     : $ {booking['price']}",
            "-----------------------------------------------",
            "Thank you for choosing SkyLink Airlines!",
            "Have a Safe Journey.",
            "===================================================",
        ]
        return "\n".join(lines)
