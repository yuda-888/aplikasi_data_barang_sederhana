import sqlite3
import pandas as pd
from fpdf import FPDF
from tkinter import messagebox, filedialog
from datetime import datetime

def get_formatted_filename(extension, report_type="Produk"):
    today = datetime.today()
    formatted_date = today.strftime('%A, %d %B %Y')
    file_name = f"Laporan {report_type}_{formatted_date}"
    return file_name + extension, file_name, today.strftime('%Y-%m-%d')  


def download_laporan_produk_excel_report():
    file_name, title, report_date = get_formatted_filename('.xlsx', "Produk")
    file_path = filedialog.asksaveasfilename(defaultextension='.xlsx', initialfile=file_name, filetypes=[("Excel Files", "*.xlsx")])
    if not file_path:
        return

    conn = sqlite3.connect('db/sales_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, code, name, category, stock, price, created_at FROM products")
    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=["ID", "Kode", "Nama", "Kategori", "Stok", "Harga", "Tanggal"])
    df["Harga"] = df["Harga"].apply(lambda x: f"Rp. {x:,.0f}".replace(',', '.'))

    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Laporan Produk")

        workbook = writer.book
        worksheet = writer.sheets["Laporan Produk"]

        format_header = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': 1})
        format_border = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})

        worksheet.merge_range('A1:G1', title, format_header)
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(1, col_num, value, format_header)

        for row_num, row_data in enumerate(df.values):
            for col_num, cell_value in enumerate(row_data):
                worksheet.write(row_num + 2, col_num, cell_value, format_border)

        worksheet.set_column('A:G', 20)

    messagebox.showinfo("Success", f"Laporan produk berhasil diunduh sebagai {file_path}.")


def download_laporan_produk_pdf_report():
    file_name, title, report_date = get_formatted_filename('.pdf', "Produk")
    file_path = filedialog.asksaveasfilename(defaultextension='.pdf', initialfile=file_name, filetypes=[("PDF Files", "*.pdf")])
    if not file_path:
        return

    conn = sqlite3.connect('db/sales_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, code, name, category, stock, price, created_at FROM products")
    rows = cursor.fetchall()
    conn.close()

    pdf = FPDF(orientation='L')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", size=16, style='B')
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=10, style='B')
    headers = ["ID", "Kode", "Nama", "Kategori", "Stok", "Harga", "Tanggal"]
    col_widths = [20, 30, 50, 40, 20, 30, 40]

    
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align='C')
    pdf.ln()

    pdf.set_font("Arial", size=10)
    for row in rows:
        for i, value in enumerate(row):
            if i == 5:  
                value = f"Rp. {value:,.0f}".replace(',', '.')
            pdf.cell(col_widths[i], 10, str(value), border=1, align='C')  
        pdf.ln()

    
    pdf.output(file_path)
    messagebox.showinfo("Success", f"Laporan produk berhasil diunduh sebagai {file_path}.")


def download_laporan_transaksi_excel_report():
    file_name, title, report_date = get_formatted_filename('.xlsx', "Transaksi")
    file_path = filedialog.asksaveasfilename(defaultextension='.xlsx', initialfile=file_name, filetypes=[("Excel Files", "*.xlsx")])
    if not file_path:
        return

    conn = sqlite3.connect('db/sales_app.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, p.name, p.category, t.quantity, t.total_price, t.transaction_type, t.date 
        FROM transactions t 
        JOIN products p ON t.product_id = p.id
        WHERE DATE(t.date) = ?  -- Filter berdasarkan tanggal
    """, (report_date,))
    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=["ID", "Nama Produk", "Kategori", "Jumlah", "Total Harga", "Jenis Transaksi", "Tanggal"])
    df["Total Harga"] = df["Total Harga"].apply(lambda x: f"Rp. {x:,.0f}".replace(',', '.'))

    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Laporan Transaksi")

        workbook = writer.book
        worksheet = writer.sheets["Laporan Transaksi"]

        format_header = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'border': 1})
        format_border = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})

        worksheet.merge_range('A1:G1', title, format_header)
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(1, col_num, value, format_header)

        for row_num, row_data in enumerate(df.values):
            for col_num, cell_value in enumerate(row_data):
                worksheet.write(row_num + 2, col_num, cell_value, format_border)

        worksheet.set_column('A:G', 20)

    messagebox.showinfo("Success", f"Laporan transaksi berhasil diunduh sebagai {file_path}.")


def download_laporan_transaksi_pdf_report():
    file_name, title, report_date = get_formatted_filename('.pdf', "Transaksi")
    file_path = filedialog.asksaveasfilename(defaultextension='.pdf', initialfile=file_name, filetypes=[("PDF Files", "*.pdf")])
    if not file_path:
        return

    conn = sqlite3.connect('db/sales_app.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, p.name, p.category, t.quantity, t.total_price, t.transaction_type, t.date 
        FROM transactions t 
        JOIN products p ON t.product_id = p.id
        WHERE DATE(t.date) = ?  -- Filter berdasarkan tanggal
    """, (report_date,))
    rows = cursor.fetchall()
    conn.close()

    pdf = FPDF(orientation='L')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", size=16, style='B')
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=10, style='B')
    headers = ["ID", "Nama Produk", "Kategori", "Jumlah", "Total Harga", "Jenis Transaksi", "Tanggal"]
    col_widths = [20, 50, 40, 25, 40, 50, 40]

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align='C')
    pdf.ln()

    pdf.set_font("Arial", size=10)
    for row in rows:
        for i, value in enumerate(row):
            if i == 4:  
                value = f"Rp. {value:,.0f}".replace(',', '.')
            pdf.cell(col_widths[i], 10, str(value), border=1, align='C')  
        pdf.ln()

    pdf.output(file_path)
    messagebox.showinfo("Success", f"Laporan transaksi berhasil diunduh sebagai {file_path}.")
