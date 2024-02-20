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
                    );''',
                   '''CREATE TABLE recipes(
                   recipe_id INT PRIMARY KEY,
                   recipe_name VARCHAR(255) NOT NULL,
                   recipe_description VARCHAR(255)
                   )''']

    for query in sql_queries:
        try:
            cursor.execute(query)
            conn.commit()
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
            query = (f"INSERT OR REPLACE INTO {key} "
                     f"VALUES ({ids}, '{name}');")
            print(query)
            try:
                curr.execute(query)
                conn.commit()
            except sqlite3.OperationalError as e:
                if "already exists" in str(e):
                    print(f"Table already exists {query}")
                else:
                    raise


def insert_recipe(conn, curr, name, description):
    last_id = 0
    id_query = f"SELECT MAX(recipe_id) FROM recipes"
    try:
        curr.execute(id_query)
        conn.commit()
        result = curr.fetchone()[0]
        if result is not None:
            last_id = result
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print(f"Table already exists {id_query}")
        else:
            raise

    query = (f"INSERT INTO recipes "
             f"VALUES ({last_id + 1}, '{name}', '{description}');")
    try:
        curr.execute(query)
        conn.commit()
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

    # MENU
    print("Pass the empty recipe to exit.")
    while True:
        recipe_name = input("Recipe name: ")
        if recipe_name == '':
            break
        recipe_description = input("Recipe description: ")
        insert_recipe(conn, curr, recipe_name, recipe_description)

    conn.close()
