"""
Project Description:

"""
import psycopg2

# Connect to an existing database
conn = psycopg2.connect(host="localhost", database="Movie", user="postgres", password="qw")

# Open a cursor to perform database operations
cur = conn.cursor()



# Execute a command: this creates a new table
cur.execute("DROP TABLE IF EXISTS test2")
cur.execute("CREATE TABLE IF NOT EXISTS test2 (id serial PRIMARY KEY, num integer, data varchar);")

# Pass data to fill a query placeholders and let Psycopg perform
# the correct conversion (no more SQL injections!)
cur.execute("INSERT INTO test2 (num, data) VALUES (%s, %s)", (100, "abc'def"))

# Query the database and obtain data as Python objects
cur.execute("SELECT * FROM test2;")
print(cur.fetchone())


# Make the changes to the database persistent
conn.commit()

# Close communication with the database
cur.close()
conn.close()
