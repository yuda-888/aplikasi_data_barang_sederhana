import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox
from datetime import datetime

def input_transaction(app):
    transaction_window = tk.Tk()
    transaction_window.title("Input Transaksi")
    transaction_window.geometry("600x800")

    # Frame untuk form input
    input_frame = tk.Frame(transaction_window)
    input_frame.pack(pady=10, padx=10, fill="x")

    tk.Label(input_frame, text="Pilih Produk:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    product_combobox = ttk.Combobox(input_frame, state="readonly")
    product_combobox.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="Jumlah:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    quantity_entry = tk.Entry(input_frame)
    quantity_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="Jenis Transaksi:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    transaction_type_combobox = ttk.Combobox(input_frame, state="readonly", values=["Cash", "E-wallet", "Transfer"])
    transaction_type_combobox.grid(row=2, column=1, padx=5, pady=5)

    # Frame untuk tabel sementara
    table_frame = tk.Frame(transaction_window)
    table_frame.pack(pady=10, padx=10, fill="both", expand=True)

    tk.Label(table_frame, text="Informasi Produk:", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=5)

    # Tabel sementara
    temp_table = ttk.Treeview(table_frame, columns=("Produk", "Jumlah", "Harga", "Total"), show="headings")
    temp_table.heading("Produk", text="Produk")
    temp_table.heading("Jumlah", text="Jumlah")
    temp_table.heading("Harga", text="Harga")
    temp_table.heading("Total", text="Total Harga")

    temp_table.column("Produk", anchor="center", width=150)
    temp_table.column("Jumlah", anchor="center", width=80)
    temp_table.column("Harga", anchor="center", width=120)
    temp_table.column("Total", anchor="center", width=150)

    temp_table.pack(fill="both", expand=True, padx=5, pady=5)

    def format_price(price):
        price_str = f"{price:,.0f}"
        return f"Rp. {price_str.replace(',', '.')}"

    def add_product_to_table():
        product = product_combobox.get()
        quantity = quantity_entry.get()

        if not product or not quantity:
            messagebox.showwarning("Input Error", "Lengkapi data produk dan jumlah!")
            return

        try:
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Input Error", "Jumlah harus berupa angka!")
            return

        conn = sqlite3.connect('db/sales_app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, stock, price FROM products WHERE name=?", (product,))
        product_data = cursor.fetchone()

        if not product_data:
            messagebox.showerror("Error", "Produk tidak ditemukan!")
            conn.close()
            return

        product_id, stock, price = product_data

        if quantity > stock:
            messagebox.showerror("Error", "Stok tidak mencukupi!")
            conn.close()
            return

        total_price = price * quantity

        temp_table.insert("", "end", values=(product, quantity, format_price(price), format_price(total_price)))

        cursor.execute("INSERT INTO temp_transactions (product_id, quantity, total_price) VALUES (?, ?, ?)",
                       (product_id, quantity, total_price))
        conn.commit()
        conn.close()

        product_combobox.set('')
        quantity_entry.delete(0, tk.END)

    def proses_transaction():
        conn = sqlite3.connect('db/sales_app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM temp_transactions")
        temp_data = cursor.fetchall()

        if not temp_data:
            messagebox.showwarning("Input Error", "Tidak ada produk yang dipilih atau informasi tidak lengkap!")
            conn.close()
            return

        transaction_type = transaction_type_combobox.get()

        if not transaction_type:
            messagebox.showwarning("Input Error", "Pilih jenis transaksi!")
            conn.close()
            return

        transaction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for data in temp_data:
            product_id, quantity, total_price = data[1], data[2], data[3]

            cursor.execute("SELECT stock FROM products WHERE id=?", (product_id,))
            stock = cursor.fetchone()[0]

            if quantity > stock:
                messagebox.showwarning("Error", "Stok tidak mencukupi untuk salah satu produk!")
                conn.close()
                return

            new_stock = stock - quantity
            cursor.execute("UPDATE products SET stock=? WHERE id=?", (new_stock, product_id))
            cursor.execute("INSERT INTO transactions (product_id, quantity, transaction_type, total_price, date) VALUES (?, ?, ?, ?, ?)",
                           (product_id, quantity, transaction_type, total_price, transaction_date))

        cursor.execute("DELETE FROM temp_transactions")
        conn.commit()
        conn.close()

        messagebox.showinfo("Transaksi Berhasil", "Transaksi berhasil dilakukan!")

        if hasattr(app, 'transaction_completed'):
            app.transaction_completed()

        product_combobox.set('')
        quantity_entry.delete(0, tk.END)
        transaction_type_combobox.set('')

        for row in temp_table.get_children():
            temp_table.delete(row)

        load_products()

    def load_products():
        conn = sqlite3.connect('db/sales_app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM products")
        products = cursor.fetchall()
        product_combobox['values'] = [product[0] for product in products]
        conn.close()

    load_products()

    # Frame untuk tombol
    button_frame = tk.Frame(transaction_window)
    button_frame.pack(pady=10, padx=10, fill="x")

    add_button = tk.Button(button_frame, text="Tambahkan Produk", command=add_product_to_table, bg="blue", fg="white", width=20)
    add_button.grid(row=0, column=0, padx=10)

    process_button = tk.Button(button_frame, text="Proses Transaksi", command=proses_transaction, bg="green", fg="white", width=20)
    process_button.grid(row=0, column=1, padx=10)

    transaction_window.mainloop()
