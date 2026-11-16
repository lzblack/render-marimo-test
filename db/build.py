import marimo

app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import duckdb

    # Builds db/database.duckdb from nothing, from the files in db/data/.
    database = mo.notebook_dir() / "database.duckdb"
    database.unlink(missing_ok=True)
    with duckdb.connect(database) as con:
        con.execute(f"CREATE TABLE sales AS SELECT * FROM read_parquet('{mo.notebook_dir() / 'data' / 'sales.parquet'}')")
        rows = con.sql("SELECT count(*) FROM sales").fetchall()[0][0]
    print(f"built {database.name} with {rows} rows in sales")
    return


if __name__ == "__main__":
    app.run()
