import sqlite3


class FoodBlogDataset:
    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)
        self.cursor = self.conn.cursor()

        self.serve_id = 0
        self.recipe_id = 0
        self.quantity_id = 0

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

            CREATE TABLE IF NOT EXISTS quantity(
                quantity_id INT PRIMARY KEY,
                measure_id INT NOT NULL,
                ingredient_id INT NOT NULL,
                quantity INT NOT NULL,
                recipe_id INT NOT NULL,
                FOREIGN KEY(measure_id) REFERENCES measures(measure_id)
                FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id)
                FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id)
            );
        '''

        self.cursor.executescript(create_tables_query)
        self.conn.commit()

    def insert_tables(self):
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

    def insert_quantity(self, user_measure_id, user_ingredient_id, quantity):
        try:
            self.cursor.execute("SELECT MAX(quantity_id) FROM quantity")
            self.conn.commit()
            last_id = self.cursor.fetchone()[0] or 0
        except sqlite3.OperationalError as e:
            self.handle_sql_error(e, "Error retrieving last quantity id")
            last_id = 0

        self.quantity_id = last_id + 1

        query = "INSERT INTO quantity VALUES (?, ?, ?, ?, ?);"
        try:
            self.cursor.execute(query,
                                (self.quantity_id, user_measure_id, user_ingredient_id, quantity, self.recipe_id))
            self.conn.commit()
        except sqlite3.OperationalError as e:
            self.handle_sql_error(e, f"Error inserting quantity: {quantity}")

    def available_meals(self):
        sql_query = "SELECT * FROM meals"
        self.cursor.execute(sql_query)
        self.conn.commit()
        result = self.cursor.fetchall()
        for row in result:
            meal_id, meal_name = row
            print(f"{meal_id}) {meal_name}")

    def available_measures(self):
        sql_query = "SELECT * FROM measures"
        self.cursor.execute(sql_query)
        self.conn.commit()
        return self.cursor.fetchall()

    def available_ingredients(self):
        sql_query = "SELECT * FROM ingredients"
        self.cursor.execute(sql_query)
        self.conn.commit()
        return self.cursor.fetchall()

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

    def find_recipe(self, ingredients):
        join_query = ("SELECT quantity.recipe_id, recipe_name, ingredient_name "
                      "FROM quantity "
                      "LEFT JOIN ingredients "
                      "ON quantity.ingredient_id = ingredients.ingredient_id "
                      "LEFT JOIN recipes "
                      "ON recipes.recipe_id = quantity.recipe_id;")

        self.cursor.execute(join_query)
        self.conn.commit()
        recipe_ingredient_list = self.cursor.fetchall()

        recipes_dict = {}

        for recipe_id, recipe_name, ingredient in recipe_ingredient_list:
            if (recipe_id, recipe_name) in recipes_dict:
                recipes_dict[(recipe_id, recipe_name)].append(ingredient)
            else:
                recipes_dict[(recipe_id, recipe_name)] = [ingredient]

        found_recipes = []
        for key, value in recipes_dict.items():
            if set(ingredients).issubset(set(value)):
                found_recipes.append(key[1])

        if found_recipes:
            print(f"Recipes selected for you: {', '.join(found_recipes)}")
        else:
            print("There are no such recipes in the database.")

    def close_connection(self):
        self.conn.close()
