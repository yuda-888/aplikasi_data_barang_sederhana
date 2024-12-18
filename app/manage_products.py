import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import locale
import download_laporan  # Import the file for downloading reports

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

set_locale()

# Translate day and month to Indonesian if locale is unavailable
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

    day = date_obj.strftime('%A')
    month = date_obj.strftime('%B')

    translated_day = days.get(day, day)
    translated_month = months.get(month, month)

    return date_obj.strftime(f"{translated_day}, %d {translated_month} %Y %H:%M:%S")

# Format date with day name and time
def format_date_with_day_and_time(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    today = datetime.today().date()
    formatted_time = date_obj.strftime('%H:%M:%S')

    if date_obj.date() == today:
        if locale.getlocale(locale.LC_TIME)[0] == 'id_ID':
            return f"Hari ini, {date_obj.strftime('%A, %d %B %Y')} {formatted_time}"
        else:
            return f"Hari ini, {translate_to_indonesian(date_obj)}"
    else:
        if locale.getlocale(locale.LC_TIME)[0] == 'id_ID':
            return date_obj.strftime('%A, %d %B %Y %H:%M:%S')
        else:
            return translate_to_indonesian(date_obj)

# Format price as Rupiah
def format_price(price):
    price_str = f"{price:,.0f}"
    return f"Rp. {price_str.replace(',', '.')}"

# Format price input during typing
def format_price_input(event, entry_widget):
    price = entry_widget.get().replace('.', '')
    if price.isdigit():
        formatted_price = f"{int(price):,}".replace(',', '.')
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, formatted_price)

def manage_products():
    # Create main window
    manage_products_frame = tk.Tk()
    manage_products_frame.title("Manajemen Produk")
    manage_products_frame.geometry("900x700")

    # Title Label
    title_label = tk.Label(
        manage_products_frame, 
        text="Manajemen Produk",
        font=("Arial", 16, "bold"),
        pady=10
    )
    title_label.pack()
    # Frame for table
    table_frame = tk.Frame(manage_products_frame)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Product table
    tree = ttk.Treeview(
        table_frame,
        columns=("ID", "Kode", "Nama", "Kategori", "Stok", "Harga", "Tanggal"),
        show="headings"
    )

    # Scrollbar for table
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(pady=10, fill=tk.BOTH, expand=True)

    # Define table headings
    for col, width, anchor in zip(
        ["ID", "Kode", "Nama", "Kategori", "Stok", "Harga", "Tanggal"],
        [50, 100, 200, 100, 50, 100, 150],
        ["center", "center", "w", "center", "center", "e", "center"]):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor=anchor)

    # Load data from database
    def load_data():
        for item in tree.get_children():
            tree.delete(item)
        conn = sqlite3.connect('db/sales_app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, code, name, category, stock, price, created_at FROM products")
        for row in cursor.fetchall():
            formatted_price = format_price(row[5])
            formatted_date = format_date_with_day_and_time(row[6])
            tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], formatted_price, formatted_date))
        conn.close()

    load_data()

    # Add new product
    def add_product():
        def save_product():
            code, name, category = code_entry.get(), name_entry.get(), category_entry.get()
            stock, price = stock_entry.get(), price_entry.get().replace('.', '')

            if not (code and name and category and stock and price):
                messagebox.showwarning("Input Error", "Semua kolom harus diisi!")
                return

            try:
                stock, price = int(stock), float(price)
            except ValueError:
                messagebox.showwarning("Input Error", "Stok harus angka dan Harga harus valid!")
                return

            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect('db/sales_app.db')
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO products (code, name, category, stock, price, created_at) VALUES (?, ?, ?, ?, ?, ?)''',
                (code, name, category, stock, price, created_at)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Produk berhasil ditambahkan!")
            add_product_window.destroy()
            load_data()

        # Add product window
        add_product_window = tk.Toplevel(manage_products_frame)
        add_product_window.title("Tambah Produk")

        labels = ["Kode Produk:", "Nama Produk:", "Kategori:", "Stok:", "Harga:"]
        entries = []
        for i, label in enumerate(labels):
            tk.Label(add_product_window, text=label).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(add_product_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        code_entry, name_entry, category_entry, stock_entry, price_entry = entries
        price_entry.bind("<KeyRelease>", lambda event: format_price_input(event, price_entry))

        tk.Button(add_product_window, text="Simpan", command=save_product).grid(row=5, column=1, pady=10)

    # Edit selected product
    def edit_product():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Pilih produk yang ingin diedit!")
            return

        selected_product = tree.item(selected_item)["values"]
        product_id = selected_product[0]

        def save_changes():
            code, name, category, stock = code_entry.get(), name_entry.get(), category_entry.get(), stock_entry.get()

            if not (code and name and category and stock):
                messagebox.showwarning("Input Error", "Semua kolom harus diisi!")
                return

            try:
                stock = int(stock)
            except ValueError:
                messagebox.showwarning("Input Error", "Stok harus angka yang valid!")
                return

            conn = sqlite3.connect('db/sales_app.db')
            cursor = conn.cursor()
            cursor.execute(
                '''UPDATE products SET code = ?, name = ?, category = ?, stock = ? WHERE id = ?''',
                (code, name, category, stock, product_id)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Produk berhasil diperbarui!")
            edit_product_window.destroy()
            load_data()

        # Edit product window
        edit_product_window = tk.Toplevel(manage_products_frame)
        edit_product_window.title("Edit Produk")

        labels = ["Kode Produk:", "Nama Produk:", "Kategori:", "Stok:"]
        entries = []
        for i, label in enumerate(labels):
            tk.Label(edit_product_window, text=label).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(edit_product_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        code_entry, name_entry, category_entry, stock_entry = entries
        for entry, value in zip(entries, selected_product[1:5]):
            entry.insert(0, value)

        tk.Button(edit_product_window, text="Simpan Perubahan", command=save_changes).grid(row=4, column=1, pady=10)

    # Delete selected product
    def delete_product():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Pilih produk yang ingin dihapus!")
            return

        selected_product = tree.item(selected_item)["values"]
        product_id = selected_product[0]

        confirm = messagebox.askyesno("Konfirmasi Hapus", f"Apakah Anda yakin ingin menghapus produk '{selected_product[2]}'?")
        if confirm:
            conn = sqlite3.connect('db/sales_app.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Produk berhasil dihapus!")
            load_data()

    # Download product reports
    def download_excel():
        download_laporan.download_laporan_produk_excel_report()

    def download_pdf():
        download_laporan.download_laporan_produk_pdf_report()

    # Frame for buttons
    button_frame = tk.Frame(manage_products_frame)
    button_frame.pack(fill=tk.X, padx=10, pady=10)

    # Buttons
    buttons = [
        ("Tambah Produk", add_product),
        ("Edit Produk", edit_product),
        ("Hapus Produk", delete_product),
        ("Download Laporan Excel", download_excel),
        ("Download Laporan PDF", download_pdf)
    ]

    for text, command in buttons:
        tk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=5)

    manage_products_frame.mainloop()

if __name__ == "__main__":
    manage_products()
