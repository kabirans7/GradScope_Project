#Insert values into DBeaver
# This deals with ETL 

from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_data

def run_etl():
    print("=" * 55)
    print("   GradScope ETL Pipeline")
    print("=" * 55)

    # Step 1: Extract
    print("Step 1: Extract (E)")
    df = extract_data()
    print(f"E complete: {len(df)} rows extracted from source.")

    # Step 2: Transform
    tables = transform_data(df)

    # Step 3: Load
    load_data(tables)

    print("=" * 55)
    print("   ETL Pipeline Complete")
    print("=" * 55)


if __name__ == "__main__":
    run_etl()