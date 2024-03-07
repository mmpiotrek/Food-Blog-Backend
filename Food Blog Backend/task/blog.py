import sqlite3
import argparse


class FoodBlogDataset:
    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)
        self.cursor = self.conn.cursor()

        self.serve_id = 0
        self.recipe_id = 0

        self.create_tables()
        self.insert_tables()

    @staticmethod
    def handle_sql_error(error, message):
        if "already exists" in str(error):
            print(f"Table already exists {message}")
        else:
            raise

    def create_tables(self):
        create_tables_query = '''
            PRAGMA foreign_keys = ON;
            
            CREATE TABLE IF NOT EXISTS meals(
                meal_id INT PRIMARY KEY,
                meal_name VARCHAR(255) UNIQUE NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS ingredients(
                ingredient_id INT PRIMARY KEY,
                ingredient_name VARCHAR(255) UNIQUE NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS measures(
                measure_id INT PRIMARY KEY,
                measure_name VARCHAR(255) UNIQUE
            );
            
            CREATE TABLE IF NOT EXISTS recipes(
               recipe_id INT PRIMARY KEY,
               recipe_name VARCHAR(255) NOT NULL,
               recipe_description VARCHAR(255)
            );
            
            CREATE TABLE IF NOT EXISTS serve(
                serve_id INT PRIMARY KEY,
                recipe_id INT NOT NULL,
                meal_id INT NOT NULL,
                FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id)
                FOREIGN KEY(meal_id) REFERENCES meals(meal_id)
            );
        '''

        self.cursor.executescript(create_tables_query)
        self.conn.commit()

    def insert_tables(self):
        data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
                "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
                "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

        meals_data = [
            (1, "breakfast"),
            (2, "brunch"),
            (3, "lunch"),
            (4, "supper")
        ]

        ingredients_data = [
            (1, "milk"),
            (2, "cacao"),
            (3, "strawberry"),
            (4, "blueberry"),
            (5, "blackberry"),
            (6, "sugar")
        ]

        measures_data = [
            (1, "ml"),
            (2, "g"),
            (3, "l"),
            (4, "cup"),
            (5, "tbsp"),
            (6, "tsp"),
            (7, "dsp"),
            (8, "")
        ]

        self.conn.executemany("INSERT OR REPLACE INTO meals VALUES (?, ?)", meals_data)
        self.conn.executemany("INSERT OR REPLACE INTO ingredients VALUES (?, ?)", ingredients_data)
        self.conn.executemany("INSERT OR REPLACE INTO measures VALUES (?, ?)", measures_data)
        self.conn.commit()

    def insert_recipe(self, name, description):
        try:
            self.cursor.execute("SELECT MAX(recipe_id) FROM recipes")
            self.conn.commit()
            last_id = self.cursor.fetchone()[0] or 0
        except sqlite3.OperationalError as e:
            self.handle_sql_error(e, "Error retrieving last recipe id")
            last_id = 0

        self.recipe_id = last_id + 1

        query = "INSERT INTO recipes VALUES (?, ?, ?);"
        try:
            self.cursor.execute(query, (self.recipe_id, name, description))
            self.conn.commit()
        except sqlite3.OperationalError as e:
            self.handle_sql_error(e, f"Error inserting recipe: {name}")

    def available_meals(self):
        sql_query = "SELECT * FROM meals"
        self.cursor.execute(sql_query)
        self.conn.commit()
        result = self.cursor.fetchall()
        for row in result:
            meal_id, meal_name = row
            print(f"{meal_id}) {meal_name}")

    def meals_to_serve(self, meal_ids: list):
        for meal_id in meal_ids:
            try:
                self.cursor.execute("SELECT MAX(serve_id) FROM serve")
                self.conn.commit()
                last_id = self.cursor.fetchone()[0] or 0
            except sqlite3.OperationalError as e:
                self.handle_sql_error(e, "Error retrieving last serve id")
                last_id = 0

            self.serve_id = last_id + 1

            query = "INSERT OR REPLACE INTO serve VALUES (?, ?, ?);"
            try:
                self.cursor.execute(query, (self.serve_id, self.recipe_id, meal_id))
                self.conn.commit()
            except sqlite3.OperationalError as e:
                self.handle_sql_error(e, f"Error inserting serve: {self.serve_id}")

    def close_connection(self):
        self.conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('database_name', default='food_blog.db')
    args = parser.parse_args()
    database = FoodBlogDataset(args.database_name)

    # MENU
    print("Pass the empty recipe to exit.")
    while True:
        recipe_name = input("Recipe name: ")
        if recipe_name == '':
            break
        recipe_description = input("Recipe description: ")
        database.insert_recipe(recipe_name, recipe_description)
        database.available_meals()
        service_time = list(map(int, input("When the dish can be served:").split(" ")))
        database.meals_to_serve(service_time)
    database.close_connection()
