"""
login.py
--------
Entry-point window: lets the user choose Admin or Customer, log in, or
(for customers) register a new account. Wraps database.SkyLinkSystem
authentication logic without altering it.

This is a CustomTkinter rewrite of the original PySide6 LoginWindow.
It exposes two callback hooks (on_admin_authenticated /
on_customer_authenticated) that main.py wires up to show the correct
dashboard, replacing PySide6's Signal/slot mechanism with plain Python
callables.
"""

import customtkinter as ctk

from utils import COLORS, font, show_error, show_success, primary_button


class LoginWindow(ctk.CTkToplevel):
    """Landing window with Admin Login / Customer Login & Register tabs."""

    def __init__(self, master, system, on_admin_authenticated, on_customer_authenticated):
        super().__init__(master)
        self.system = system
        self.on_admin_authenticated = on_admin_authenticated
        self.on_customer_authenticated = on_customer_authenticated

        self.title("SkyLink Airlines - Sign In")
        self.geometry("960x600")
        self.minsize(860, 560)
        self.configure(fg_color=COLORS["bg_root"])
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()

    # ------------------------------------------------------------------
    def _on_close(self):
        # Closing the login window closes the whole application.
        self.master.destroy()

    # ------------------------------------------------------------------
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left brand panel
        brand = ctk.CTkFrame(self, width=380, fg_color=COLORS["bg_panel"], corner_radius=0)
        brand.grid(row=0, column=0, sticky="nsew")
        brand.grid_propagate(False)

        brand_inner = ctk.CTkFrame(brand, fg_color="transparent")
        brand_inner.pack(fill="both", expand=True, padx=40, pady=(60, 40))

        logo = ctk.CTkLabel(brand_inner, text="\u2708 SkyLink", font=font(30, "bold"),
                             text_color=COLORS["accent"], anchor="w")
        logo.pack(anchor="w")

        tagline = ctk.CTkLabel(brand_inner, text="Airlines Reservation System",
                                font=font(13), text_color=COLORS["text_muted"],
                                anchor="w", justify="left")
        tagline.pack(anchor="w", pady=(4, 0))

        desc = ctk.CTkLabel(
            brand_inner,
            text="\nEnterprise-grade flight booking and management "
                 "platform. Sign in to manage flights or book your "
                 "next journey.",
            font=font(12), text_color=COLORS["text_secondary"],
            anchor="w", justify="left", wraplength=300,
        )
        desc.pack(anchor="w", pady=(8, 0))

        # Right form panel
        right = ctk.CTkFrame(self, fg_color=COLORS["bg_root"], corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")

        right_inner = ctk.CTkFrame(right, fg_color="transparent")
        right_inner.pack(fill="both", expand=True, padx=60, pady=60)

        title = ctk.CTkLabel(right_inner, text="Welcome Back", font=font(24, "bold"),
                              text_color=COLORS["text_primary"], anchor="w")
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(right_inner, text="Sign in to continue to your dashboard",
                                 font=font(13), text_color=COLORS["text_muted"], anchor="w")
        subtitle.pack(anchor="w", pady=(2, 20))

        self.tabs = ctk.CTkTabview(
            right_inner, fg_color=COLORS["bg_card"], segmented_button_fg_color=COLORS["bg_card_alt"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["bg_card_alt"],
            text_color=COLORS["text_primary"], corner_radius=14,
        )
        self.tabs.pack(fill="both", expand=True)

        self.tabs.add("Admin")
        self.tabs.add("Customer Login")
        self.tabs.add("Register")

        self._build_admin_tab(self.tabs.tab("Admin"))
        self._build_customer_login_tab(self.tabs.tab("Customer Login"))
        self._build_customer_register_tab(self.tabs.tab("Register"))

    # ------------------------------------------------------------------
    def _labeled_entry(self, parent, label_text, show=None, placeholder=""):
        ctk.CTkLabel(parent, text=label_text, font=font(12, "bold"),
                     text_color=COLORS["text_secondary"], anchor="w").pack(anchor="w", pady=(10, 4))
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder, show=show, height=38,
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"], corner_radius=8,
        )
        entry.pack(fill="x")
        return entry

    # ------------------------------------------------------------------
    # ADMIN TAB
    # ------------------------------------------------------------------
    def _build_admin_tab(self, page):
        page.grid_columnconfigure(0, weight=1)
        wrap = ctk.CTkFrame(page, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=10, pady=10)

        self.admin_username = self._labeled_entry(
            wrap, "Username", placeholder="admin@SkyAirline.com")
        self.admin_password = self._labeled_entry(
            wrap, "Password", show="*", placeholder="Admin password")
        self.admin_password.bind("<Return>", lambda e: self._handle_admin_login())

        login_btn = primary_button(wrap, "Login as Admin", self._handle_admin_login, width=200)
        login_btn.pack(anchor="w", pady=(20, 0))

    def _handle_admin_login(self):
        result = self.system.admin_login(
            self.admin_username.get().strip(),
            self.admin_password.get(),
        )
        if result["success"]:
            self.on_admin_authenticated()
        else:
            show_error(self, "Login Failed", result["message"])

    # ------------------------------------------------------------------
    # CUSTOMER LOGIN TAB
    # ------------------------------------------------------------------
    def _build_customer_login_tab(self, page):
        wrap = ctk.CTkFrame(page, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=10, pady=10)

        self.cust_email = self._labeled_entry(wrap, "Email", placeholder="Email address")
        self.cust_password = self._labeled_entry(wrap, "Password", show="*", placeholder="Password")
        self.cust_password.bind("<Return>", lambda e: self._handle_customer_login())

        login_btn = primary_button(wrap, "Login", self._handle_customer_login, width=200)
        login_btn.pack(anchor="w", pady=(20, 0))

    def _handle_customer_login(self):
        result = self.system.login_passenger(
            self.cust_email.get().strip(),
            self.cust_password.get(),
        )
        if result["success"]:
            self.on_customer_authenticated()
        else:
            show_error(self, "Login Failed", result["message"])

    # ------------------------------------------------------------------
    # REGISTER TAB
    # ------------------------------------------------------------------
    def _build_customer_register_tab(self, page):
        scroll = ctk.CTkScrollableFrame(page, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=4, pady=4)

        self.reg_name = self._labeled_entry(scroll, "Full Name", placeholder="Full name")
        self.reg_email = self._labeled_entry(scroll, "Email", placeholder="Email address")
        self.reg_password = self._labeled_entry(scroll, "Password", show="*", placeholder="Password")
        self.reg_cnic = self._labeled_entry(scroll, "CNIC", placeholder="CNIC")
        self.reg_phone = self._labeled_entry(scroll, "Phone Number", placeholder="Phone number")

        row = ctk.CTkFrame(scroll, fg_color="transparent")
        row.pack(fill="x", pady=(10, 0))
        row.grid_columnconfigure((0, 1), weight=1)

        age_box = ctk.CTkFrame(row, fg_color="transparent")
        age_box.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(age_box, text="Age", font=font(12, "bold"),
                     text_color=COLORS["text_secondary"], anchor="w").pack(anchor="w", pady=(0, 4))
        self.reg_age = ctk.CTkEntry(
            age_box, placeholder_text="0-120", height=38, fg_color=COLORS["bg_input"],
            border_color=COLORS["border"], text_color=COLORS["text_primary"], corner_radius=8,
        )
        self.reg_age.pack(fill="x")

        gender_box = ctk.CTkFrame(row, fg_color="transparent")
        gender_box.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(gender_box, text="Gender", font=font(12, "bold"),
                     text_color=COLORS["text_secondary"], anchor="w").pack(anchor="w", pady=(0, 4))
        self.reg_gender = ctk.CTkOptionMenu(
            gender_box, values=["Male", "Female", "Other"], height=38,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"], text_color=COLORS["text_primary"],
            dropdown_fg_color=COLORS["bg_card_alt"], corner_radius=8,
        )
        self.reg_gender.set("Male")
        self.reg_gender.pack(fill="x")

        register_btn = primary_button(scroll, "Create Account", self._handle_register, width=200)
        register_btn.pack(anchor="w", pady=(20, 10))

    def _handle_register(self):
        age_text = self.reg_age.get().strip()
        result = self.system.register_passenger(
            self.reg_name.get().strip(),
            self.reg_email.get().strip(),
            self.reg_password.get(),
            self.reg_cnic.get().strip(),
            self.reg_phone.get().strip(),
            age_text if age_text != "" else 0,
            self.reg_gender.get(),
        )
        if result["success"]:
            show_success(self, "Registration Successful", result["message"])
            self.tabs.set("Customer Login")
            self.cust_email.delete(0, "end")
            self.cust_email.insert(0, self.reg_email.get().strip())
            self.reg_name.delete(0, "end")
            self.reg_email.delete(0, "end")
            self.reg_password.delete(0, "end")
            self.reg_cnic.delete(0, "end")
            self.reg_phone.delete(0, "end")
            self.reg_age.delete(0, "end")
            self.reg_gender.set("Male")
        else:
            show_error(self, "Registration Failed", result["message"])
