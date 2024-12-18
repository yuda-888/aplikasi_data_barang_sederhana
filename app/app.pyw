import tkinter as tk
from tkinter import messagebox
from login import check_login  
from manage_products import manage_products  
from input_transaction import input_transaction  
from manage_transactions import manage_transactions  
import sqlite3
from datetime import datetime

class SalesApp:
    def __init__(self, root):
        
        self.root = root
        self.root.title("Aplikasi Data Barang Sederhana")
        self.root.geometry("1000x600")
        self.root.configure(bg="#A2D5F2")  

        
        self.user_role = None
        self.sales_summary_frame = None
        self.sales_summary_labels = {}

        
        self.show_login()

    def clear_frame(self):
        """Menghapus semua elemen dalam frame utama."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        """Menampilkan halaman login."""
        self.clear_frame()
        
        
        tk.Label(self.root, text="Aplikasi Data Barang Sederhana", font=("Arial", 24, "bold"), bg="#A2D5F2").pack(pady=70)
        
        check_login(self)  

    def show_dashboard(self):
        """Menampilkan dashboard berdasarkan role user."""
        self.clear_frame()
        if self.user_role == "Admin":
            self.create_admin_dashboard()
       
    def create_admin_dashboard(self):
        """Dashboard untuk Admin."""
        self.clear_frame()
        self.root.configure(bg="#A2D5F2")  

        tk.Label(
            self.root, text="Dashboard Admin", font=("Arial", 28, "bold"), bg="#A2D5F2"
        ).pack(pady=20)

        
        self.sales_summary_frame = tk.Frame(self.root, bg="#f0f0f0", bd=2, relief="ridge")
        self.sales_summary_frame.pack(pady=10, fill="x", padx=20)

        self.show_sales_summary()

        
        button_style = {"font": ("Arial", 14), "bg": "#0073e6", "fg": "white", "padx": 10, "pady": 5}
        
        tk.Button(self.root, text="Manajemen Produk", command=manage_products, **button_style).pack(pady=10)
        tk.Button(self.root, text="Manajemen Transaksi", command=manage_transactions, **button_style).pack(pady=10)
        tk.Button(self.root, text="Input Transaksi", command=lambda: input_transaction(self), **button_style).pack(pady=10)
        tk.Button(self.root, text="Keluar", command=self.show_login, bg="#ff4d4d", fg="white", font=("Arial", 14), padx=10, pady=5).pack(pady=10)

    def format_price(self, price):
        """Format angka ke mata uang dengan 'Rp'."""
        price_str = f"{price:,.0f}"
        return f"Rp. {price_str.replace(',', '.')}"

    def show_sales_summary(self):
        """Menampilkan ringkasan data penjualan."""
        tk.Label(
            self.sales_summary_frame, 
            text="Ringkasan Data Penjualan", 
            font=("Arial", 18, "bold"), 
            bg="#f0f0f0"
        ).pack(pady=10)

        
        self.sales_summary_labels['total_transactions'] = tk.Label(self.sales_summary_frame, text="", font=("Arial", 14), bg="#f0f0f0")
        self.sales_summary_labels['total_transactions'].pack(pady=5)

        self.sales_summary_labels['best_selling_product'] = tk.Label(self.sales_summary_frame, text="", font=("Arial", 14), bg="#f0f0f0")
        self.sales_summary_labels['best_selling_product'].pack(pady=5)

        self.sales_summary_labels['total_revenue'] = tk.Label(self.sales_summary_frame, text="", font=("Arial", 14), bg="#f0f0f0")
        self.sales_summary_labels['total_revenue'].pack(pady=5)

        self.update_sales_summary()

    def update_sales_summary(self):
        """Memperbarui data ringkasan penjualan."""
        total_transactions = self.get_total_transactions_today()
        best_selling_product = self.get_best_selling_product()
        total_revenue = self.get_total_revenue_today()

        # Update teks label
        self.sales_summary_labels['total_transactions'].config(
            text=f"Total Transaksi Hari Ini   : {total_transactions} transaksi"
        )
        self.sales_summary_labels['best_selling_product'].config(
            text=f"Produk Terlaris      : {best_selling_product}"
        )
        self.sales_summary_labels['total_revenue'].config(
            text=f"Total Pendapatan Hari Ini  : {self.format_price(total_revenue)}"
        )

    def get_total_transactions_today(self):
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            conn = sqlite3.connect('db/sales_app.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE date LIKE ?", (today + '%',))
            total_transactions = cursor.fetchone()[0]
            conn.close()
            return total_transactions
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Terjadi kesalahan pada database: {e}")
            return 0

    def get_best_selling_product(self):
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            conn = sqlite3.connect('db/sales_app.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.name, SUM(t.quantity) as total_sales
                FROM transactions t
                JOIN products p ON t.product_id = p.id
                WHERE t.date LIKE ?
                GROUP BY p.name
                ORDER BY total_sales DESC
                LIMIT 1
            ''', (today + '%',))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else "Tidak ada transaksi"
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Terjadi kesalahan pada database: {e}")
            return "Tidak ada data"

    def get_total_revenue_today(self):
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            conn = sqlite3.connect('db/sales_app.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT SUM(t.quantity * p.price) 
                FROM transactions t
                JOIN products p ON t.product_id = p.id
                WHERE t.date LIKE ?
            ''', (today + '%',))
            total_revenue = cursor.fetchone()[0]
            conn.close()
            return total_revenue if total_revenue else 0
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Terjadi kesalahan pada database: {e}")
            return 0

    def transaction_completed(self):
        """Dipanggil setelah transaksi selesai."""
        self.update_sales_summary()


if __name__ == "__main__":
    root = tk.Tk()
    app = SalesApp(root)
    root.mainloop()
