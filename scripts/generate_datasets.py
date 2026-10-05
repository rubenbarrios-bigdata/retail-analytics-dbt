"""
Script de Generación de Datos Sintéticos para el Proyecto Retail Analytics
--------------------------------------------------------------------------
Este script genera los 4 datasets transaccionales crudos simulando la base de datos
operacional (OLTP) de una empresa de comercio minorista (Retail & E-commerce),
así como el archivo consolidado desnormalizado de transacciones.

Modelos generados:
1. raw_customers.csv (Clientes con atributos geográficos)
2. raw_products.csv (Catálogo de productos con costos y precios de lista)
3. raw_orders.csv (Órdenes de compra con estados y canales)
4. raw_order_items.csv (Detalle de cada orden con cantidades y descuentos)
5. raw_retail_transactions.csv (Export plano unificado)
"""

import os
import shutil
import pandas as pd

def consolidate_raw_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    seeds_dir = os.path.join(base_dir, 'seeds')
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)

    print("Consolidando datos transaccionales desde seeds/...")
    customers = pd.read_csv(os.path.join(seeds_dir, 'raw_customers.csv'))
    products = pd.read_csv(os.path.join(seeds_dir, 'raw_products.csv'))
    orders = pd.read_csv(os.path.join(seeds_dir, 'raw_orders.csv'))
    items = pd.read_csv(os.path.join(seeds_dir, 'raw_order_items.csv'))

    # Join completo emulando un volcado general
    df = items.merge(orders, on='order_id', how='left')
    df = df.merge(customers, on='customer_id', how='left')
    df = df.merge(products, on='product_id', how='left')

    cols = [
        'order_id', 'order_date', 'status', 'channel',
        'customer_id', 'first_name', 'last_name', 'email', 'city', 'country', 'signup_date',
        'order_item_id', 'product_id', 'product_name', 'category',
        'cost_price', 'list_price', 'quantity', 'unit_price', 'discount_amount'
    ]
    df = df[cols]
    df.to_csv(os.path.join(data_dir, 'raw_retail_transactions.csv'), index=False)

    for f in ['raw_customers.csv', 'raw_products.csv', 'raw_orders.csv', 'raw_order_items.csv']:
        shutil.copy(os.path.join(seeds_dir, f), os.path.join(data_dir, f))

    print(f"Exportación finalizada con éxito en {data_dir}")

if __name__ == '__main__':
    consolidate_raw_data()
