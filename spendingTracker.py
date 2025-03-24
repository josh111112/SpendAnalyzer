import pandas as pd
import matplotlib.pyplot as plt
import csv
import os
from category_mappings import descKeys

file_name = 'csv/mar21-feb21USAA.csv'
# Read the original CSV and create a new one with updated categories
with open(file_name, 'r') as input_file, open(file_name + '_updated.csv', 'w', newline='') as output_file:
    reader = csv.reader(input_file)
    writer = csv.writer(output_file)
    
    # Write the header row
    header = next(reader)
    writer.writerow(header)
    
    # Process each row
    for row in reader:
        description = row[1].upper()
        # If category is pending update according to descKeys
        if row[3] == "Category Pending":
            category_found = False
            for key, value in descKeys.items():
                if key in description:
                    row[3] = value
                    category_found = True
                    break
            if not category_found:
                row[3] = "Uncategorized"
                print(f"Updated category for: {description}")
        writer.writerow(row)

print("CSV file has been updated!")

# Read the CSV file
df = pd.read_csv(file_name + '_updated.csv')

# Convert date strings to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Calculate total spending and category percentages
total_spending = abs(df[df['Amount'] < 0]['Amount'].sum())
total_earned = df[df['Amount'] > 0]['Amount'].sum()
# Filter out positive amounts and Paycheck category before calculating category totals
category_totals = df[(df['Amount'] < 0) & (df['Category'] != 'Paycheck')].groupby('Category')['Amount'].sum().abs()
category_percentages = (category_totals / total_spending * 100).round(2)

# Get date range
start_date = df['Date'].min().strftime('%Y-%m-%d')
end_date = df['Date'].max().strftime('%Y-%m-%d')
date_range = f"{start_date} to {end_date}"

# Filter categories with more than 2% of spending
major_categories = category_percentages[category_percentages > 2]

# Create pie chart with smaller figure size
plt.figure(figsize=(10, 8))

# Add date range as a subtitle on the left side
plt.figtext(0.1, 0.95, f'Date Range: {date_range}', fontsize=9, ha='left')

# Add total spent and earned on the right side
plt.figtext(0.9, 0.95, f'Total Spent: ${total_spending:,.2f}\nTotal Earned: ${total_earned:,.2f}', 
            fontsize=9, ha='right')

# Calculate explode values (0.05 for all slices - reduced from 0.1)
explode = [0.05] * len(major_categories)

# Create labels with percentage and dollar amount
labels = [f"{cat}\n({pct:.1f}%)\n${amount:.2f}" 
          for cat, pct, amount in zip(major_categories.index, 
                                    major_categories.values, 
                                    category_totals[major_categories.index])]

# Create pie chart with adjusted parameters
plt.pie(major_categories, 
        labels=labels,
        explode=explode,
        autopct='',
        startangle=90,
        labeldistance=1.1,  # Move labels slightly further out
        textprops={'fontsize': 8})  # Make label text smaller
plt.title('Major Spending Categories (>2%)', pad=20)  # Add padding to title

# Adjust layout with more space
plt.tight_layout(pad=3.0)  # Increase padding around the plot

# Create output directory if it doesn't exist
output_dir = 'Spending_Analysis'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Save the plot as PDF with date range in filename
output_filename = os.path.join(output_dir, f'spending_analysis_{start_date}_to_{end_date}.pdf')
plt.savefig(output_filename, bbox_inches='tight')
print(f"PDF saved as: {output_filename}")

plt.show()

# loop and print the uncategorized cases
for index, row in df.iterrows():
    if row['Category'] == 'Uncategorized':
        print(row['Description'], row['Amount'])
