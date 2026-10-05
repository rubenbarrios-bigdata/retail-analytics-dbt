# Retail & E-Commerce Analytics Engineering con dbt Core y Google BigQuery

[![dbt-core](https://img.shields.io/badge/dbt--core-v1.12.5-orange?logo=dbt)](https://www.getdbt.com/)
[![Google BigQuery](https://img.shields.io/badge/Google_Cloud-BigQuery-blue?logo=googlecloud)](https://cloud.google.com/bigquery)
[![Tests Passing](https://img.shields.io/badge/tests-28%2F28%20passing-brightgreen)](https://docs.getdbt.com/docs/build/data-tests)
[![SQL](https://img.shields.io/badge/SQL-Advanced%20Modeling-informational)](https://cloud.google.com/bigquery/docs/reference/standard-sql/en-US)
[![Methodology](https://img.shields.io/badge/Methodology-Kimball%20Dimensional%20Modeling-purple)](#arquitectura-y-modelo-dimensional)

---

## 📌 Resumen Ejecutivo del Proyecto

Este repositorio contiene un proyecto integral de **Analytics Engineering** implementado con **dbt Core** y **Google Cloud BigQuery**. El objetivo es transformar datos transaccionales crudos de ventas y clientes de una empresa de comercio minorista (*Retail & E-commerce*) en un modelo dimensional listo para la toma de decisiones empresariales y visualización en herramientas de Business Intelligence como **Power BI** o **Looker**.

El proyecto abarca el ciclo de vida completo de un pipeline ELT moderno:
* **Ingesta y reproducibilidad** mediante `dbt seed` (1,000 órdenes, 1,794 transacciones, 200 clientes y 35 productos).
* **Capa Staging** para limpieza, casteo de tipos y estandarización técnica (`views`).
* **Capa Marts** con modelado dimensional estrella (*Star Schema* con `tables`).
* **Modularidad avanzada** con macros en **Jinja** (`calculate_margin_pct`) para cálculos financieros seguros.
* **Control de calidad** con **28 pruebas automáticas** (`unique`, `not_null`, integridad referencial `relationships` y reglas de negocio `accepted_values`).
* **Catálogo y linaje de datos vivo** generado automáticamente con `dbt docs`.

---

## 🏗 Arquitectura y Flujo de Datos (DAG)

El linaje de datos sigue la estructura estándar de capas analíticas:

```mermaid
graph TD
    subgraph Raw Data / Seeds
        RC[(raw_customers)]
        RP[(raw_products)]
        RO[(raw_orders)]
        ROI[(raw_order_items)]
    end

    subgraph Staging Layer (Vistas)
        SC[stg_customers]
        SP[stg_products]
        SO[stg_orders]
        SOI[stg_order_items]
    end

    subgraph Marts Layer (Tablas Dimensionales)
        FO[(fct_orders)]
        DC[(dim_customers)]
        DP[(dim_products)]
    end

    subgraph BI & Reporting
        PBI[Power BI / Looker Dashboards]
        ADHOC[Analyses: Monthly Performance]
    end

    RC --> SC
    RP --> SP
    RO --> SO
    ROI --> SOI

    SO --> FO
    SOI --> FO

    SC --> DC
    FO --> DC

    SP --> DP
    SOI --> DP
    SO --> DP

    FO --> PBI
    DC --> PBI
    DP --> PBI
    FO --> ADHOC
```

---

## 📊 Modelo Dimensional de Negocio (Kimball)

### 1. `fct_orders` (Tabla de Hechos)
* **Grano:** Una fila por cada orden individual de compra.
* **Métricas:** Unidades totales vendidas, monto bruto (`gross_amount`), descuentos acumulados (`total_discount_amount`), facturación neta (`net_amount`) y bandera booleana `is_completed_order`.
* **Dimensiones asociadas:** `customer_id`, canal de venta (`channel`), fecha, año y mes.

### 2. `dim_customers` (Dimensión Clientes 360)
* **Grano:** Una fila por cliente registrado.
* **Métricas calculadas:**
  * Fecha de primera y última compra.
  * Total de órdenes históricas y órdenes completadas.
  * **Customer Lifetime Value (LTV)**: Facturación acumulada histórica.
  * **Ticket Promedio (AOV)**: Gasto promedio por pedido completado.
* **Segmentación analítica automática:**
  * `VIP`: Facturación acumulada superior o igual a $600.
  * `Frequent`: 3 o más compras completadas.
  * `Active`: Entre 1 y 2 compras completadas.
  * `Prospect`: Clientes registrados sin compras efectivas aún.

### 3. `dim_products` (Dimensión Catálogo y Rendimiento)
* **Grano:** Una fila por producto.
* **Atributos:** Categoría, costo unitario, precio de lista, margen unitario y margen porcentual.
* **Métricas de rendimiento:** Total de órdenes en que participó, unidades vendidas, ingresos netos generados y **ganancia total estimada**.

---

## 🛡 Calidad de Datos y Gobernanza (28 Tests)

La integridad del modelo se valida automáticamente contra BigQuery ejecutando `dbt test`:

| Tipo de Prueba | Columnas Auditadas | Propósito de Negocio |
| :--- | :--- | :--- |
| **`unique`** | `customer_id`, `product_id`, `order_id`, `order_item_id` | Garantiza ausencia total de duplicados en claves primarias. |
| **`not_null`** | Claves primarias, correos, montos netos y categorías | Evita registros huérfanos o fallos en visualizaciones BI. |
| **`relationships`** | `order_id` -> `orders`<br>`product_id` -> `products`<br>`customer_id` -> `customers` | Asegura **integridad referencial estricta** entre hechos y dimensiones. |
| **`accepted_values`** | `orders.status` in `['completed', 'returned', 'cancelled', 'processing', 'shipped']`<br>`dim_customers.customer_segment` in `['VIP', 'Frequent', 'Active', 'Prospect']` | Valida que los estados y clasificaciones sigan los catálogos de negocio. |

---

## ⚙️ Macros y Reusabilidad con Jinja

Para evitar lógica duplicada en cálculos de márgenes, se desarrolló la macro [`macros/calculate_margin_pct.sql`](file:///c:/Users/ismar/Downloads/dbt/macros/calculate_margin_pct.sql):

```sql
{% macro calculate_margin_pct(list_price, cost_price) %}
    round(safe_divide(cast({{ list_price }} as numeric) - cast({{ cost_price }} as numeric), cast({{ list_price }} as numeric)) * 100, 2)
{% endmacro %}
```
Esta macro utiliza `safe_divide` nativo de BigQuery para proteger los modelos contra divisiones por cero o valores nulos imprevistos.

---

## 🚀 Guía de Reproducción Local

Cualquier persona puede clonar este repositorio y ejecutar el pipeline completo en su propio entorno:

### 1. Clonar el repositorio y crear entorno virtual
```bash
git clone https://github.com/rubenbarrios-bigdata/retail-analytics-dbt.git
cd retail-analytics-dbt
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# Instalar dbt y conector de BigQuery:
pip install dbt-core dbt-bigquery
```

### 2. Configurar perfil de conexión (`profiles.yml`)
En `~/.dbt/profiles.yml` (en Windows: `C:\Users\<usuario>\.dbt\profiles.yml`):
```yaml
retail_analytics:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: TU_PROJECT_ID_GCP
      dataset: dbt_dev
      threads: 4
      keyfile: /ruta/segura/a/tu/clave_service_account.json
      location: US
```

### 3. Ejecutar el pipeline de dbt
```bash
# 1. Validar conexión
dbt debug

# 2. Cargar los datos crudos a BigQuery
dbt seed

# 3. Compilar y materializar modelos (vistas y tablas)
dbt run

# 4. Ejecutar las 28 pruebas de calidad de datos
dbt test

# 5. Generar y servir la documentación interactiva con el grafo DAG
dbt docs generate
dbt docs serve
```

---

## 📈 Conexión con Power BI
Los modelos finales en la capa **Marts** (`dim_customers`, `dim_products` y `fct_orders`) se conectan directamente desde Power BI mediante el conector nativo de **Google BigQuery**, permitiendo crear esquemas en estrella limpios sin necesidad de realizar transformaciones complejas en Power Query.
