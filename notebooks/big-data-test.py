import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import psutil

    return duckdb, mo, psutil


@app.cell
def _(mo):
    mo.md("""
    # Big Data Test

    A deployment test: one million sales rows on a free Render instance (512 MB).
    """)
    return


@app.cell
def _(duckdb, mo):
    database = mo.notebook_dir().parent / "db" / "database.duckdb"

    def ask(sql, params=None):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql, params=params).pl()

    return (ask,)


@app.cell
def _(psutil):
    def memory_mb():
        return round(psutil.Process().memory_info().rss / 1_000_000)

    return (memory_mb,)


@app.cell
def _(ask, mo):
    stores = ask("SELECT DISTINCT store FROM sales ORDER BY store")["store"].to_list()
    store_picker = mo.ui.dropdown(options=stores, value=stores[0], label="Store")
    rows_picker = mo.ui.dropdown(
        options=["1000", "10000", "100000", "500000", "1000000"],
        value="1000",
        label="Rows to load into the table",
    )
    mo.hstack([store_picker, rows_picker], justify="start")
    return rows_picker, store_picker


@app.cell
def _(ask, memory_mb, mo, store_picker):
    # 1. A query that aggregates in DuckDB: a small result from a million rows.
    by_month = ask(
        """
        SELECT strftime(order_date, '%Y-%m') AS month,
               count(*) AS orders,
               round(sum(quantity * unit_price), 2) AS revenue
        FROM sales
        WHERE store = ?
        GROUP BY month
        ORDER BY month
        """,
        [store_picker.value],
    )
    mo.vstack([
        mo.md(f"**Aggregated:** {by_month.height} months for {store_picker.value}. Memory after: {memory_mb()} MB"),
        mo.ui.table(by_month, selection=None),
    ])
    return


@app.cell
def _(ask, memory_mb, mo, rows_picker):
    # 2. Rows pulled into polars and shown as they are.
    raw_rows = ask("SELECT * FROM sales LIMIT ?", [int(rows_picker.value)])
    mo.vstack([
        mo.md(f"**Raw rows:** {raw_rows.height:,} loaded. Memory after: {memory_mb()} MB"),
        mo.ui.table(raw_rows, selection=None),
    ])
    return


if __name__ == "__main__":
    app.run()
