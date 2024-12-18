import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox
from datetime import datetime
import locale
import download_laporan  # Import functions

# Set locale to Indonesian
def set_locale():
    try:
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')  # Linux/macOS
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'Indonesian_Indonesia.1252')  # Windows
        except locale.Error:
            messagebox.showwarning(
                "Locale Error",
                "Pengaturan bahasa Indonesia tidak tersedia di sistem Anda. "
                "Nama hari dan bulan akan tetap dalam bahasa default (biasanya Inggris)."
            )

# Call the function to set locale
set_locale()

# Function to translate day and month to Indonesian if locale is unavailable
def translate_to_indonesian(date_obj):
    days = {
        'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
        'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
    }
    months = {
        'January': 'Januari', 'February': 'Februari', 'March': 'Maret',
        'April': 'April', 'May': 'Mei', 'June': 'Juni', 'July': 'Juli',
        'August': 'Agustus', 'September': 'September', 'October': 'Oktober',
        'November': 'November', 'December': 'Desember'
    }

    day = date_obj.strftime('%A')  # Get day in English
    month = date_obj.strftime('%B')  # Get month in English

    translated_day = days.get(day, day)
    translated_month = months.get(month, month)

    return date_obj.strftime(f"{translated_day}, %d {translated_month} %Y %H:%M:%S")

# Function to format date with day name and time
def format_date_with_day_and_time(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')  # Ensure date format matches
    today = datetime.today().date()
    formatted_time = date_obj.strftime('%H:%M:%S')

    if date_obj.date() == today:
        if locale.getlocale(locale.LC_TIME)[0] == 'id_ID':  # Check if Indonesian locale is set
            return f"Hari ini, {date_obj.strftime('%A, %d %B %Y')} {formatted_time}"
        else:
            return f"Hari ini, {translate_to_indonesian(date_obj)}"
    else:
        if locale.getlocale(locale.LC_TIME)[0] == 'id_ID':  # Check if Indonesian locale is set
            return date_obj.strftime('%A, %d %B %Y %H:%M:%S')
        else:
            return translate_to_indonesian(date_obj)

# Function to format price as Rupiah with dot as thousands separator
def format_price(price):
    price_str = f"{price:,.0f}"
    return f"Rp. {price_str.replace(',', '.')}"

# Main function to manage transactions
def manage_transactions():
    manage_transactions_frame = tk.Tk()
    manage_transactions_frame.title("Manajemen Transaksi")
    manage_transactions_frame.geometry("900x600")

    # Title Label
    title_label = tk.Label(
        manage_transactions_frame, 
        text="Manajemen Transaksi",
        font=("Arial", 16, "bold"),
        pady=10
    )
    title_label.pack()

    # Frame for the table
    table_frame = tk.Frame(manage_transactions_frame, pady=10)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10)

    # Table to show transactions
    tree = ttk.Treeview(
        table_frame, 
        columns=("ID", "Nama Produk", "Kategori", "Jumlah", "Total Harga", "Jenis Transaksi", "Tanggal"), 
        show="headings"
    )
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tree.heading("ID", text="ID")
    tree.heading("Nama Produk", text="Nama Produk")
    tree.heading("Kategori", text="Kategori")
    tree.heading("Jumlah", text="Jumlah")
    tree.heading("Total Harga", text="Total Harga")
    tree.heading("Jenis Transaksi", text="Jenis Transaksi")
    tree.heading("Tanggal", text="Tanggal")

    tree.column("ID", width=50, anchor="center")
    tree.column("Nama Produk", width=150, anchor="w")
    tree.column("Kategori", width=100, anchor="center")
    tree.column("Jumlah", width=50, anchor="center")
    tree.column("Total Harga", width=100, anchor="e")
    tree.column("Jenis Transaksi", width=100, anchor="center")
    tree.column("Tanggal", width=200, anchor="center")

    # Scrollbar for the table
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Function to load data from DB
    def load_data():
        try:
            conn = sqlite3.connect('db/sales_app.db')
            cursor = conn.cursor()
            cursor.execute(""" 
                SELECT t.id, p.name, p.category, t.quantity, t.total_price, t.transaction_type, t.date 
                FROM transactions t 
                JOIN products p ON t.product_id = p.id
            """)
            rows = cursor.fetchall()

            for item in tree.get_children():
                tree.delete(item)

            for row in rows:
                formatted_date = format_date_with_day_and_time(row[6])  # Using the updated function
                formatted_price = format_price(row[4])  # Format price as Rupiah with dot separator
                tree.insert("", "end", values=(row[0], row[1], row[2], row[3], formatted_price, row[5], formatted_date))
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Terjadi kesalahan: {e}")
        finally:
            conn.close()

    load_data()

    # Refresh data every 3 seconds
    def auto_refresh():
        load_data()
        manage_transactions_frame.after(3000, auto_refresh)  # Refresh every 3000 milliseconds (3 seconds)

    auto_refresh()

    # Button Frame
    btn_frame = tk.Frame(manage_transactions_frame, pady=10)
    btn_frame.pack()

    # Buttons for downloading reports
    btn_download_excel = tk.Button(
        btn_frame, 
        text="Download Laporan Transaksi Excel", 
        command=download_laporan.download_laporan_transaksi_excel_report,
        width=30
    )
    btn_download_excel.pack(side=tk.LEFT, padx=10)

    btn_download_pdf = tk.Button(
        btn_frame, 
        text="Download Laporan Transaksi PDF", 
        command=download_laporan.download_laporan_transaksi_pdf_report,
        width=30
    )
    btn_download_pdf.pack(side=tk.LEFT, padx=10)

    manage_transactions_frame.mainloop()

if __name__ == "__main__":
    manage_transactions()
