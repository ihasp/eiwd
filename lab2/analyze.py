import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re

# Set plotting style
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

print("Loading data...")
file_path = "lab2/relative_risks.xlsx"
df = pd.read_excel(file_path, header=None)

# Extract headers
headers = list(df.iloc[1])
sub_headers = list(df.iloc[2])

# We need columns 4 to 27 (age groups)
age_columns = sub_headers[4:28]

# Parse data rows
data_rows = df.iloc[3:]
records = []
current_risk = None

for idx, row in data_rows.iterrows():
    val_0 = row[0]
    val_1 = row[1]
    
    # Check if this is a Risk factor header row
    if pd.notna(val_0) and pd.isna(val_1):
        current_risk = val_0
        continue
        
    # Data row
    if pd.notna(val_1):
        outcome = val_0
        category = row[1]
        morbidity_mortality = row[2]
        sex = row[3]
        
        record = {
            "Risk": current_risk,
            "Outcome": outcome,
            "Category_Units": category,
            "Morbidity_Mortality": morbidity_mortality,
            "Sex": sex
        }
        
        # Parse age values
        for i, col_idx in enumerate(range(4, 28)):
            age_name = age_columns[i]
            cell_val = row[col_idx]
            
            # Extract the numeric value from "value\n(lower to upper)"
            num_val = np.nan
            if pd.notna(cell_val):
                cell_str = str(cell_val).strip()
                if cell_str:
                    # Take the first token before newline or space
                    parts = re.split(r'[\n\s]+', cell_str)
                    try:
                        num_val = float(parts[0])
                    except ValueError:
                        pass
            record[age_name] = num_val
            
        records.append(record)

cleaned_df = pd.DataFrame(records)
print(f"Cleaned DataFrame has {len(cleaned_df)} rows and {len(cleaned_df.columns)} columns.")

# Let's save the cleaned CSV
cleaned_df.to_csv("lab2/relative_risks_cleaned.csv", index=False)
print("Saved cleaned data to lab2/relative_risks_cleaned.csv")

# 1. Histogram of Relative Risks for 'All-age' group
plt.figure()
all_age_data = cleaned_df['All-age'].dropna()
sns.histplot(all_age_data, bins=30, kde=True, color='royalblue')
plt.title("Distribution of Relative Risks for 'All-age' Group")
plt.xlabel("Relative Risk (RR)")
plt.ylabel("Count")
plt.yscale('log') # since risks can span orders of magnitude
plt.tight_layout()
plt.savefig("lab2/histogram_all_age.png", dpi=150)
plt.close()
print("Generated and saved histogram_all_age.png")

# 2. Scatter Plot: Compare two age groups, e.g., '0-6 days' vs '7-27 days'
plt.figure()
scatter_data = cleaned_df[['0-6 days', '7-27 days']].dropna()
sns.scatterplot(data=scatter_data, x='0-6 days', y='7-27 days', alpha=0.6, color='darkorange')
# Draw y = x reference line
max_val = max(scatter_data['0-6 days'].max(), scatter_data['7-27 days'].max())
plt.plot([0, max_val], [0, max_val], 'r--', label='y = x (equal risk)')
plt.xscale('log')
plt.yscale('log')
plt.title("Comparison of Relative Risks: 0-6 days vs 7-27 days")
plt.xlabel("Relative Risk (0-6 days)")
plt.ylabel("Relative Risk (7-27 days)")
plt.legend()
plt.tight_layout()
plt.savefig("lab2/scatter_comparison.png", dpi=150)
plt.close()
print("Generated and saved scatter_comparison.png")

# 3. Line Plot / Scatter Plot: Relative Risk vs Category for 'Unsafe water source'
plt.figure()
water_df = cleaned_df[(cleaned_df['Risk'] == 'Unsafe water source') & (cleaned_df['Outcome'] == 'Diarrhoeal diseases')].copy()
# Let's melt age columns for visualization
melted_water = water_df.melt(
    id_vars=['Category_Units', 'Sex'], 
    value_vars=['All-age', '0-6 days', '7-27 days', '28-364 days', '1-4 years'],
    var_name='Age_Group', 
    value_name='Relative_Risk'
).dropna()

sns.barplot(data=melted_water, x='Category_Units', y='Relative_Risk', hue='Age_Group')
plt.xticks(rotation=45, ha='right')
plt.title("Relative Risk of Diarrhoeal Diseases from Unsafe Water Source by Category")
plt.xlabel("Water Source Category")
plt.ylabel("Relative Risk (RR)")
plt.tight_layout()
plt.savefig("lab2/water_source_risks.png", dpi=150)
plt.close()
print("Generated and saved water_source_risks.png")

print("Done! Data exploration and plotting finished.")
