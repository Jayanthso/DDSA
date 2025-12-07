import os
import glob
import mysql.connector

folder_path = r"C:\Users\sojay\DS\Project\Data-Driven Stock Analysis\output_csv"
files = glob.glob(os.path.join(folder_path, "*.csv"))

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="welcome1",
    database="ddsa",
    allow_local_infile=True
)
cursor = conn.cursor()

for file in files:
    file_for_sql = file.replace("\\", "\\\\")
    query = (
        "LOAD DATA LOCAL INFILE '{file}'\n"
        "INTO TABLE stock_price\n"
        "FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"'\n"
        "LINES TERMINATED BY '\\n'\n"
        "IGNORE 1 LINES\n"
        "(ticker, close_price, @price_date, high, low, price_month, open_price, volume)\n"
        "SET price_date = STR_TO_DATE(@price_date, '%Y-%m-%d');"
        ).format(file=file_for_sql)
    
    cursor.execute(query)
    conn.commit()

cursor.close()
conn.close()

print("All files loaded successfully!")
