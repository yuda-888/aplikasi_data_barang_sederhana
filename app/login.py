import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(app):
    # Membuat frame untuk login
    login_frame = tk.Frame(app.root)
    
    login_frame.place(relx=0.5, rely=0.5, anchor="center") 

   
    tk.Label(login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
    username_entry = tk.Entry(login_frame)
    username_entry.grid(row=0, column=1, padx=5, pady=5)

   
    tk.Label(login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
    password_entry = tk.Entry(login_frame, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    def handle_login():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Username dan Password harus diisi!")
            return

        conn = sqlite3.connect('db/sales_app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and user[2] == hash_password(password):
            app.user_role = user[3]
            app.show_dashboard()
        else:
            messagebox.showerror("Login Error", "Username atau Password salah!")

    tk.Button(login_frame, text="Login", command=handle_login).grid(row=2, column=1, pady=10)
