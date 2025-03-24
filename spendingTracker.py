import pandas as pd
import matplotlib.pyplot as plt
import csv
from category_mappings import descKeys

file_name = 'mar21-feb21USAA.csv'
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
            for key, value in descKeys.items():
                if key in description:
                    row[3] = value
                    break
                else:
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
category_totals = df[df['Amount'] < 0].groupby('Category')['Amount'].sum().abs()
category_percentages = (category_totals / total_spending * 100).round(2)

# Get date range
start_date = df['Date'].min().strftime('%Y-%m-%d')
end_date = df['Date'].max().strftime('%Y-%m-%d')
date_range = f"{start_date} to {end_date}"

# Filter categories with more than 2% of spending
major_categories = category_percentages[category_percentages > 2]

# Create pie chart
plt.figure(figsize=(8, 6))

# Add date range as a subtitle on the left side
plt.figtext(0.1, 0.95, f'Date Range: {date_range}', fontsize=10, ha='left')

# Add total spent and earned on the right side
plt.figtext(0.9, 0.95, f'Total Spent: ${total_spending:,.2f}\nTotal Earned: ${total_earned:,.2f}', 
            fontsize=10, ha='right')

# Calculate explode values (0.05 for all slices - reduced from 0.1)
explode = [0.05] * len(major_categories)

# Create labels with percentage and dollar amount
labels = [f"{cat}\n({pct:.1f}%)\n${amount:.2f}" 
          for cat, pct, amount in zip(major_categories.index, 
                                    major_categories.values, 
                                    category_totals[major_categories.index])]

# Create pie chart
plt.pie(major_categories, 
        labels=labels,
        explode=explode,
        autopct='',
        startangle=90)
plt.title('Major Spending Categories (>2%)')

# Adjust layout
plt.tight_layout()

plt.show()
