import pdfplumber
import pandas as pd

# Load your PDF file
pdf_path = 'pdf.pdf'

# Define the columns you're looking for
columns = ["Trans ID", "Date", "Method", "Customer", "Type",
           "Batch ID", "Comment", "Status", "Amount", "Fee"]

# Initialize an empty list to store table rows
table_data = []

# Open the PDF with pdfplumber
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        # Extract tables on the page
        tables = page.extract_tables()

        # Loop through all the tables found on the page
        for table in tables:
            # Loop through each row in the table
            for row in table:
                if len(row) == len(columns):  # Ensure the row matches the expected column length
                    table_data.append(row)

# Convert the extracted data into a DataFrame for easy manipulation
df = pd.DataFrame(table_data, columns=columns)

# Display the DataFrame
print(df)

# Optionally, save the DataFrame to a CSV file
df.to_csv('extracted_table_data.csv', index=False)
