# extract.py
import pandas as pd
from .config import CSV_FILE


# Step 1: Extract Data (E)
def extract_data() -> pd.DataFrame:
    print("\nStep 1: Extract (E)")

    try:
        df = pd.read_csv(CSV_FILE)
        print(f"E complete: {len(df)} rows extracted from '{CSV_FILE}'.")
        print(f"  Columns: {df.columns.tolist()}")
        return df

    except FileNotFoundError:
        print(f"Error: '{CSV_FILE}' not found. Check the path in config.py.")
        raise SystemExit("ETL aborted! extraction failed.")

    except Exception as e:
        print(f"Error reading CSV: {e}")
        raise SystemExit("ETL aborted! extraction failed.")