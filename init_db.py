# init_db.py
import sqlite3
import pandas as pd

def init_enterprise_db():
    conn = sqlite3.connect("enterprise_data.db")
    # 1. 创建订单表
    conn.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        product_id TEXT,
        sales_rep_id TEXT,
        amount REAL,
        order_date DATE
    )""")
    # 2. 创建产品表
    conn.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        product_name TEXT,
        category TEXT,
        unit_price REAL
    )""")
    # 3. 插入模拟数据
    # 这里插入一些真实感的数据
    data = [
        (1, 'P001', 'S01', 1200.5, '2025-01-10'),
        (2, 'P002', 'S01', 800.0, '2025-01-12'),
        (3, 'P001', 'S02', 1500.0, '2025-02-05')
    ]
    conn.executemany("INSERT OR REPLACE INTO orders VALUES (?,?,?,?,?)", data)
    
    products = [
        ('P001', '智能传感器', '硬件', 500.0),
        ('P002', '数据看板系统', '软件', 8000.0)
    ]
    conn.executemany("INSERT OR REPLACE INTO products VALUES (?,?,?,?)", products)
    
    conn.commit()
    print("✅ 企业级数据库已就绪: enterprise_data.db")
    conn.close()

if __name__ == "__main__":
    init_enterprise_db()