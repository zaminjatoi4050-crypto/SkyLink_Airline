<<<<<<< HEAD
# SkyLink Airlines Reservation System v2.0 — CustomTkinter Edition

An enterprise-style desktop application, rebuilt with **CustomTkinter**
(replacing the original PySide6 GUI) so it runs on Python versions
where PySide6/PyQt are unavailable, including **Python 3.14**.

All original business logic, validation rules, and data structures
remain untouched in `database.py`. Every other file is presentation
layer only — the GUI calls the exact same backend functions as before.

## What Changed

- **GUI framework**: PySide6 → CustomTkinter (+ `tkinter`/`ttk` for
  tables, since CustomTkinter has no native table widget).
- **Backend** (`database.py`): unchanged, byte-for-byte. No functions
  renamed, removed, or altered. No validation logic touched.
- Every feature from the PySide6 version is preserved: Admin Login,
  Customer Login, Customer Registration, Admin Dashboard, Customer
  Dashboard, Flight Management (Add/Search/Update/Delete), Passenger
  Directory, Booking Management, Booking Receipt, Revenue Report,
  Flight Statistics, Logout, sidebar navigation, modal dialogs, and
  scrollable forms/tables.

## Project Structure

```
SkyLink-Airlines/
├── assets/
│   ├── icons/
│   ├── images/
│   └── logo/
├── main.py          # Entry point: splash screen + window orchestration
├── login.py         # Login window (Admin / Customer / Register)
├── dashboard.py      # Admin & Customer dashboard shells (sidebar nav)
├── booking.py        # Customer flight browsing, booking, receipt
├── flight.py         # Admin flight management (CRUD)
├── reports.py         # Passengers, bookings, revenue, statistics
├── database.py         # SkyLinkSystem — original backend logic (UNCHANGED)
├── utils.py             # Shared CustomTkinter helpers (dialogs, theming)
├── requirements.txt
├── install.bat
├── run.bat
└── README.md
```

## Installation

### Windows
```bash
install.bat
```

### macOS / Linux
```bash
cd SkyLink-Airlines
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> CustomTkinter relies on the standard library's `tkinter`, which
> ships with most Python installations. On some Linux distributions
> you may need to install it separately, e.g.
> `sudo apt-get install python3-tk`.

## Running

### Windows
```bash
run.bat
```

### macOS / Linux
```bash
python3 main.py
```

## Default Admin Credentials

```
Username: admin@SkyAirline.com
Password: SkyAirline@786
```

## Notes

- The app must run after `pip install -r requirements.txt` and then
  `python main.py` with no further manual modifications.
- All data is stored in memory for the duration of the session
  (matching the original system's behavior) — there is no database
  file or persistence layer.
=======
# SkyLink_Airline
>>>>>>> f7179afcfea746ab928e50dcdba367287badc857
