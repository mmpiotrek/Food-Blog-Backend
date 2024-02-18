import sqlite3
import argparse


def create_or_open_database(database_name):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    sql_queries = ['''CREATE TABLE meals(
                    meal_id INT PRIMARY KEY,
                    meal_name VARCHAR(255) UNIQUE NOT NULL
                    );''',
                   '''CREATE TABLE ingredients(
                    ingredient_id INT PRIMARY KEY,
                    ingredient_name VARCHAR(255) UNIQUE NOT NULL
                    );''',
                   '''CREATE TABLE measures(
                    measure_id INT PRIMARY KEY,
                    measure_name VARCHAR(255) UNIQUE
                    );''']

    for query in sql_queries:
        try:
            result = cursor.execute(query)
            conn.commit()
            print(result)
        except sqlite3.OperationalError as e:
            if "already exists" in str(e):
                print(f"Table already exists {query}")
            else:
                raise

    return conn, cursor


def insert_table(conn, curr):
    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

    for key in data.keys():
        for ids, name in enumerate(data[key]):
            query = (f"INSERT INTO {key} "
                     f"VALUES ({ids}, '{name}');")
            try:
                result = curr.execute(query)
                conn.commit()
                print(result)
            except sqlite3.OperationalError as e:
                if "already exists" in str(e):
                    print(f"Table already exists {query}")
                else:
                    raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('database_name', default='food_blog.db')
    args = parser.parse_args()

    conn, curr = create_or_open_database(args.database_name)
    insert_table(conn, curr)
    conn.close()
