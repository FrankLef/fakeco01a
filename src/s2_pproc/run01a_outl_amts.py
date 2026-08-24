from flml.screener.rows.amts import AmtsScreener

from src._registry.main import feathr


def main(table_nm: str = "sales") -> None:
    data = feathr.load(table_nm)
    screenr = AmtsScreener(table_nm, data=data, alpha=0.05, kgstd=2)
    screenr.title = f"Outliers' stats for '{table_nm}'"
    screenr.execute()
    screenr.print()
    # print(screenr)
    feathr.save(screenr.summ, name="survey_amts")
    screenr.tabl.show()
    # cols=("sales_qty_lg", "sales_amt_lg")
