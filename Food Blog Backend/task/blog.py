import argparse
from foodblogdataset import FoodBlogDataset


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('database_name', default='food_blog.db')
    parser.add_argument('--ingredients')
    parser.add_argument('--meals')
    args = parser.parse_args()
    database = FoodBlogDataset(args.database_name)

    start_menu = True

    if not args.ingredients is None:
        user_ingredients = args.ingredients.split(",")
        database.find_recipe(user_ingredients)
        database.close_connection()
        start_menu = False

    # MENU
    print("Pass the empty recipe to exit.")

    while start_menu:
        recipe_name = input("Recipe name: ")

        if recipe_name == '':
            break

        recipe_description = input("Recipe description: ")
        database.insert_recipe(recipe_name, recipe_description)
        database.available_meals()
        service_time = list(map(int, input("When the dish can be served:").split(" ")))
        database.meals_to_serve(service_time)

        # SUBMENU
        while True:
            user_ingredient_input = input("Input quantity of ingredient <press enter to stop>:").split(" ")

            if user_ingredient_input == ['']:
                break

            if len(user_ingredient_input) == 3:
                user_quantity = user_ingredient_input[0]
                user_measure = user_ingredient_input[1]
                user_ingredient = user_ingredient_input[2]

                selected_measure_id = None

                for m in database.available_measures():
                    measure_id, measure_name = m
                    if measure_name.startswith(user_measure):
                        if selected_measure_id is not None:
                            selected_measure_id = None
                            break
                        selected_measure_id = measure_id

                if selected_measure_id is None:
                    print("The measure is not conclusive!")
                    continue

            elif len(user_ingredient_input) == 2:
                user_quantity = user_ingredient_input[0]
                selected_measure_id = None

                for m in database.available_measures():
                    measure_id, measure_name = m
                    if measure_name == '':
                        if selected_measure_id is not None:
                            selected_measure_id = None
                            break
                        selected_measure_id = measure_id

                user_ingredient = user_ingredient_input[1]

            else:
                print("Wrong input")
                continue

            selected_ingredient_id = None

            for i in database.available_ingredients():
                ingredient_id, ingredient_name = i
                if user_ingredient in ingredient_name:
                    if selected_ingredient_id is not None:
                        selected_ingredient_id = None
                        break
                    selected_ingredient_id = ingredient_id

            if selected_ingredient_id is None:
                print("The ingredient is not conclusive!")
                continue

            database.insert_quantity(int(selected_measure_id), int(selected_ingredient_id), int(user_quantity))

    database.close_connection()
