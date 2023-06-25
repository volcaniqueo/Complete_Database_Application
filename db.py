import psycopg

# Connect to PostgreSQL
conn = psycopg.connect(host="localhost", port=5432, user="postgres", password="")

# Create a new database
conn.autocommit = True
cur = conn.cursor()
cur.execute("CREATE DATABASE moviedb;")

# Commit the transaction and close the connection
conn.commit()
conn.close()

conn = psycopg.connect(host="localhost", port=5432, user="postgres", password="", dbname="moviedb")

# Open and read the SQL file
with open('createTables.sql', 'r') as file:
    sql_script = file.read()

# Create a new cursor and execute the SQL script
cur = conn.cursor()
cur.execute(sql_script)

# Commit the transaction and close the connection
conn.commit()
conn.close()