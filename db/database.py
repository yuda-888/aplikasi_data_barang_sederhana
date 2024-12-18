import sqlite3
import hashlib

def hash_password(password):
    # Fungsi untuk hash password menggunakan SHA-256
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    # Koneksi ke database SQLite
    conn = sqlite3.connect('db/sales_app.db')
    cursor = conn.cursor()

    # Tabel produk (diperbarui tanpa kolom initial_stock dan final_stock)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT,
        stock INTEGER NOT NULL,
        price REAL NOT NULL,
        created_at TEXT NOT NULL  -- Menambahkan kolom created_at untuk menyimpan waktu pembuatan produk
    )
    ''')

    # Tabel transaksi
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        transaction_type TEXT,
        date TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    # Tabel sementara transaksi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temp_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity INTEGER,
            total_price REAL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # Tabel pengguna (users)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL  -- "admin" 
    )
    ''')

    # Menambahkan akun admin dengan password yang di-hash
    admin_password = hash_password("admin123")
    
    # Menambahkan data pengguna admin jika belum ada
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password, role) VALUES
    ('admin', ?, 'Admin')
    ''', (admin_password,))  # Pastikan tanda koma di sini untuk membuat tuple

    # Menyimpan perubahan
    conn.commit()
    # Menutup koneksi
    conn.close()

if __name__ == "__main__":
    create_tables()
