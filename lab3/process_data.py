import pandas as pd
import numpy as np
import os
import re

def clean_data():
    file_path = "lab2/relative_risks.xlsx"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file {file_path} does not exist. Please run from the project root directory.")

    print(f"Loading data from {file_path}...")
    df = pd.read_excel(file_path, header=None)

    # Extract headers and subheaders
    # Row index 1 has columns, Row index 2 has age subheaders
    headers = list(df.iloc[1])
    sub_headers = list(df.iloc[2])

    # Age columns span from column index 4 to 27
    age_columns = sub_headers[4:28]
    print(f"Detected {len(age_columns)} age groups: {age_columns}")

    # Parse rows
    data_rows = df.iloc[3:]
    records = []
    current_risk = None

    for idx, row in data_rows.iterrows():
        val_0 = row[0]
        val_1 = row[1]

        # If val_0 is not NaN and val_1 is NaN, it's a new Risk factor section header
        if pd.notna(val_0) and pd.isna(val_1):
            current_risk = str(val_0).strip()
            continue

        # If val_1 is not NaN, it's a data row (an outcome)
        if pd.notna(val_1):
            outcome = str(val_0).strip() if pd.notna(val_0) else ""
            category = str(row[1]).strip()
            morbidity_mortality = str(row[2]).strip()
            sex = str(row[3]).strip()

            record = {
                "Risk": current_risk,
                "Outcome": outcome,
                "Category_Units": category,
                "Morbidity_Mortality": morbidity_mortality,
                "Sex": sex
            }

            # Extract numeric value for each age group
            # Format in cell: "value\n(lower - upper)"
            for i, col_idx in enumerate(range(4, 28)):
                age_name = age_columns[i]
                cell_val = row[col_idx]
                num_val = np.nan

                if pd.notna(cell_val):
                    cell_str = str(cell_val).strip()
                    if cell_str:
                        # Extract the first token (numeric value)
                        parts = re.split(r'[\n\s]+', cell_str)
                        try:
                            # Replace any commas with dots just in case
                            cleaned_part = parts[0].replace(',', '.')
                            num_val = float(cleaned_part)
                        except ValueError:
                            pass
                record[age_name] = num_val

            records.append(record)

    cleaned_df = pd.DataFrame(records)
    
    # Ensure lab3 directory exists
    os.makedirs("lab3", exist_ok=True)
    
    output_path = "lab3/relative_risks_cleaned.csv"
    cleaned_df.to_csv(output_path, index=False)
    print(f"Successfully cleaned data. Rows: {len(cleaned_df)}, Columns: {len(cleaned_df.columns)}")
    print(f"Cleaned file saved to {output_path}")

if __name__ == "__main__":
    clean_data()
