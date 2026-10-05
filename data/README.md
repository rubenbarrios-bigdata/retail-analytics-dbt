# Raw Data / Datos Crudos de Origen

Esta carpeta contiene los archivos de datos originales en formato CSV antes de ser transformados por dbt en Google BigQuery.

## 📁 Archivos Disponibles

1. **`raw_retail_transactions.csv`**:
   * Dataset transaccional plano y consolidado (1,794 transacciones).
   * Contiene el histórico completo de pedidos, ítems comprados, información de cliente, precios, costos y descuentos en una sola tabla desnormalizada.

2. **Datasets Normalizados por Entidad**:
   * **`raw_customers.csv`** (200 filas): Registro de clientes con identificación, nombre, email, ciudad, país y fecha de alta.
   * **`raw_products.csv`** (36 filas): Catálogo de productos con categoría, costo y precio de lista.
   * **`raw_orders.csv`** (1,000 filas): Órdenes de compra con fecha, estado (`completed`, `returned`, `cancelled`, etc.) y canal de adquisición.
   * **`raw_order_items.csv`** (1,794 filas): Detalle línea por línea de productos adquiridos en cada orden con cantidades y descuentos.

> **Nota técnica:**  
> Para la ejecución del pipeline con dbt, las 4 tablas normalizadas se encuentran también en la carpeta `seeds/` para permitir su carga directa y automática en BigQuery mediante el comando `dbt seed`.
