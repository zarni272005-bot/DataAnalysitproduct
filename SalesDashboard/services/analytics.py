
import pandas as pd

def analyze_sales(df):
    if df.empty:
        return {
            "revenue": 0,
            "orders": 0,
            "products": 0,
            "average": 0,
            "best_product": "No Data"
        }

    df = df.copy()
    df["total"] = df["quantity"] * df["price"]

    return {
        "revenue": df["total"].sum(),
        "orders": len(df),
        "products": df["product"].nunique(),
        "average": df["total"].mean(),
        "best_product": (
            df.groupby("product")["quantity"]
            .sum()
            .idxmax()
        )
    }

def monthly_analysis(df):
    if df.empty:
        return pd.DataFrame(columns=["month", "revenue"])

    df = df.copy()
    df["total"] = df["quantity"] * df["price"]
    df["sale_date"] = pd.to_datetime(df["sale_date"])

    result = (
        df.groupby(df["sale_date"].dt.to_period("M"))["total"]
        .sum()
        .reset_index()
    )

    result["month"] = result["sale_date"].astype(str)

    return result.rename(columns={"total": "revenue"})[
        ["month", "revenue"]
    ]
