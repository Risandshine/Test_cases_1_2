import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # For better styling of widgets
import uuid
from datetime import datetime
import logging

from db import create_user, find_user_by_email, fetch_available_cars, create_reservation
from security import hash_password, verify_password

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("car_rental_system.log"),
        logging.StreamHandler()
    ]
)

class CarRentalSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Car Rental System")
        self.geometry("500x700")
        self.configure(bg="#e0f7fa")  # Light blue background
        self.resizable(False, False)
        self.current_user = None
        self.show_login_page()

    def show_login_page(self):
        self.clear_screen()
        login_frame = self.create_frame()

        tk.Label(login_frame, text="Car Reservation", font=("Arial", 18, "bold"), bg="#00695c", fg="white").pack(pady=10, fill='x')

        tk.Label(login_frame, text="Email", anchor="w", bg="#e0f7fa").pack(pady=5, anchor='w')
        self.email_entry = tk.Entry(login_frame, width=30)
        self.email_entry.pack(pady=5)

        tk.Label(login_frame, text="Password", anchor="w", bg="#e0f7fa").pack(pady=5, anchor='w')
        self.password_entry = tk.Entry(login_frame, show='*', width=30)
        self.password_entry.pack(pady=5)

        tk.Button(login_frame, text="Login", command=self.login, width=15, bg="#00796b", fg="white").pack(pady=10)
        tk.Button(login_frame, text="Sign Up", command=self.show_signup_page, width=15, bg="#004d40", fg="white").pack(pady=5)
        tk.Button(login_frame, text="Forgot Username/Password?", command=self.forgot_password, width=25, bg="#004d40", fg="white").pack(pady=5)

    def show_signup_page(self):
        self.clear_screen()
        signup_frame = self.create_frame()

        tk.Label(signup_frame, text="Sign Up", font=("Arial", 18, "bold"), bg="#00695c", fg="white").pack(pady=10, fill='x')

        tk.Label(signup_frame, text="Name", anchor="w", bg="#e0f7fa").pack(pady=5, anchor='w')
        self.name_entry = tk.Entry(signup_frame, width=30)
        self.name_entry.pack(pady=5)

        tk.Label(signup_frame, text="Address", anchor="w", bg="#e0f7fa").pack(pady=5, anchor='w')
        self.address_entry = tk.Entry(signup_frame, width=30)
        self.address_entry.pack(pady=5)

        tk.Label(signup_frame, text="Email", anchor="w", bg="#e0f7fa").pack(pady=5, anchor='w')
        self.email_entry = tk.Entry(signup_frame, width=30)
        self.email_entry.pack(pady=5)

        tk.Label(signup_frame, text="Phone", anchor="w", bg="#e0f7fa").pack(pady=5, anchor='w')
        self.phone_entry = tk.Entry(signup_frame, width=30)
        self.phone_entry.pack(pady=5)

        tk.Label(signup_frame, text="Password", anchor="w", bg="#e0f7fa").pack(pady=5, anchor='w')
        self.password_entry = tk.Entry(signup_frame, show='*', width=30)
        self.password_entry.pack(pady=5)

        tk.Button(signup_frame, text="Create Account", command=self.signup, width=15, bg="#00796b", fg="white").pack(pady=10)
        tk.Button(signup_frame, text="Back to Login", command=self.show_login_page, width=15, bg="#004d40", fg="white").pack()

    def signup(self):
        name = self.name_entry.get()
        address = self.address_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        password = self.password_entry.get()

        if not all([name, address, email, phone, password]):
            logging.warning("Signup failed due to missing fields.")
            messagebox.showerror("Error", "All fields are required")
            return

        hashed_password = hash_password(password)
        success = create_user(name, address, email, phone, hashed_password)
        if success:
            logging.info(f"User '{email}' signed up successfully.")
            messagebox.showinfo("Success", "Account created successfully")
            self.show_login_page()
        else:
            logging.error(f"Failed to create account for '{email}'.")
            messagebox.showerror("Error", "Failed to create account")

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not all([email, password]):
            logging.warning("Login failed due to missing fields.")
            messagebox.showerror("Error", "Please enter both email and password")
            return

        user = find_user_by_email(email)
        if not user:
            logging.warning(f"Login failed: Email '{email}' not found.")
            messagebox.showerror("Error", "Invalid username (email not found)")
            return

        if not verify_password(user[5], password):
            logging.warning(f"Login failed: Wrong password for '{email}'.")
            messagebox.showerror("Error", "Wrong password")
            return

        logging.info(f"User '{email}' logged in successfully.")
        self.current_user = user
        messagebox.showinfo("Success", f"Welcome, {user[1]}!")
        self.show_dashboard(user[0])

    def forgot_password(self):
        self.clear_screen()
        forgot_frame = self.create_frame()

        tk.Label(forgot_frame, text="Recover Account", font=("Arial", 18, "bold"), bg="#00695c", fg="white").pack(pady=10, fill='x')

        tk.Label(forgot_frame, text="Enter your registered email", bg="#e0f7fa").pack(pady=5)
        self.recovery_email_entry = tk.Entry(forgot_frame, width=30)
        self.recovery_email_entry.pack(pady=5)

        tk.Button(forgot_frame, text="Recover", command=self.recover_account, width=15, bg="#00796b", fg="white").pack(pady=10)
        tk.Button(forgot_frame, text="Back to Login", command=self.show_login_page, width=15, bg="#004d40", fg="white").pack()

    def recover_account(self):
        email = self.recovery_email_entry.get()
        user = find_user_by_email(email)

        if not user:
            logging.warning(f"Recovery failed: Email '{email}' not found.")
            messagebox.showerror("Error", "Email not found")
            return

        logging.info(f"Recovery email sent to '{email}'.")
        messagebox.showinfo("Success", "Recovery email has been sent. Check your inbox.")
        self.show_login_page()

    def show_dashboard(self, user_id):
        self.clear_screen()
        dashboard_frame = self.create_frame()

        tk.Label(dashboard_frame, text="Car Rental Dashboard", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(dashboard_frame, text="View User Info", command=lambda: self.view_user_info(user_id), width=30).pack(pady=5)
        tk.Button(dashboard_frame, text="Make a Reservation", command=lambda: self.make_reservation(user_id), width=30).pack(pady=5)
        tk.Button(dashboard_frame, text="Check Reservations", command=lambda: self.check_reservations(user_id), width=30).pack(pady=5)
        tk.Button(dashboard_frame, text="Log Out", command=self.show_login_page, width=30).pack(pady=20)

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_frame(self):
        frame = tk.Frame(self, bg="#e0f7fa")
        frame.pack(pady=20)
        return frame


if __name__ == "__main__":
    app = CarRentalSystem()
    app.mainloop()
