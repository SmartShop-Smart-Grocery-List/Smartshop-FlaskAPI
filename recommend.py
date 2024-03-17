import pandas as pd
import numpy as np

DVP_HIGH = 40.0
DVP_MED = 25.0
DVP_LOW = 10.0

def parse_pdv(dvp, multiplier):
    low = 0.0
    high = float("inf")
    match dvp:
        case "high":
            low = DVP_HIGH * multiplier
        case "med":
            high = DVP_HIGH * multiplier
            low = DVP_LOW * multiplier
        case "low":
            high = DVP_MED * multiplier
    return low, high

def getRecipesWithConfiguration(recipes, user_id, user_ratings_count, colab_filter=None, calories=None, daily=2000, fat="NULL", sat_fat="NULL", sugar="NULL", sodium="NULL", protein="NULL", carbs="NULL", tags=[]):
    
    high_calorie_lim = float("inf")
    low_calorie_lim = 0

    multiplier = 2000 / daily

    if calories != None:
        high_calorie_lim = max(calories+100, calories * 1.1)
        low_calorie_lim = min(calories-100, calories * 0.9)        
    
    low_fat_lim, high_fat_lim = parse_pdv(fat, multiplier)
    low_sat_fat_lim, high_sat_fat_lim = parse_pdv(sat_fat, multiplier)
    low_sugar_lim, high_sugar_lim = parse_pdv(sugar, multiplier)
    low_sodium_lim, high_sodium_lim = parse_pdv(sodium, multiplier)
    low_protein_lim, high_protein_lim = parse_pdv(protein, multiplier)
    low_carbs_lim, high_carbs_lim = parse_pdv(carbs, multiplier)

    recipes_filter = ((low_calorie_lim <= recipes['calories']) & (recipes['calories'] <= high_calorie_lim) &
                      (low_fat_lim <= recipes['total fat (PDV)']) & (recipes['total fat (PDV)'] <= high_fat_lim) &
                      (low_sat_fat_lim <= recipes['saturated fat (PDV)']) & (recipes['saturated fat (PDV)'] <= high_sat_fat_lim) &
                      (low_sugar_lim <= recipes['sugar (PDV)']) & (recipes['sugar (PDV)'] <= high_sugar_lim) &
                      (low_sodium_lim <= recipes['sodium (PDV)']) & (recipes['sodium (PDV)'] <= high_sodium_lim) &
                      (low_protein_lim <= recipes['protein (PDV)']) & (recipes['protein (PDV)'] <= high_protein_lim) &
                      (low_carbs_lim <= recipes['carbohydrates (PDV)']) & (recipes['carbohydrates (PDV)'] <= high_carbs_lim))

    tags_filter = pd.Series(True, index=recipes.index)

    if tags:
        for tag in tags:
            if type(tag) != str:
                continue
            tags_filter = tags_filter & recipes['tags'].str.contains(tag, case=False)

        recipes_filter = recipes_filter & tags_filter
    
    recipes_found = recipes[recipes_filter]
    recipes_found_sorted = recipes_found.sort_values(by='bayesian_avg', ascending=False)

    if colab_filter:
        recipe_ids = recipes_found['id'].tolist()
        weighted_predictions = []
        for recipe_id in recipe_ids:
            bayesian_avg = recipes_found[recipes_found['id'] == recipe_id]['bayesian_avg'].values[0]
            colab_prediction = colab_filter.predict(user_id, recipe_id)
            
            weighted_predictions.append((recipe_id, calculate_weighted_prediction(bayesian_avg, colab_prediction, user_ratings_count)))
        predictions_sorted = sorted(weighted_predictions, key=lambda x: x[1], reverse=True)
        sorted_recipe_ids = [pred[0] for pred in predictions_sorted]
        recipes_found_sorted = recipes_found_sorted.reindex(sorted_recipe_ids)

    return recipes_found_sorted

def getExerciseWithConfiguration(exercises, user_id, user_ratings_count, colab_filter=None, type=None, body_part=None, equipment=None, level=None):
    conditions = []
    if not (type is None):
        conditions.append(f"Type == '{type}'")
    if not (body_part is None):
        conditions.append(f"BodyPart == '{body_part}'")
    if not (equipment is None):
        conditions.append(f"Equipment == '{equipment}'")
    if not (level is None):
        conditions.append(f"Level == '{level}'")

    query_string = " and ".join(conditions)

    if query_string:
        exercises_found = exercises.query(query_string).sort_values(by='Rating', ascending=False)
        if exercises_found:
            if colab_filter:
                exercise_ids = exercises_found['id'].tolist()
                weighted_predictions = []
                for exercise_id in exercise_ids:
                    colab_prediction = colab_filter.predict(user_id, exercise_id)
                    weighted_predictions.append((exercise_id, calculate_weighted_prediction(colab_prediction, user_ratings_count)))
                weighted_predictions = sorted(weighted_predictions, key=lambda x: x[1], reverse=True)
                sorted_exercise_ids = [pred[0] for pred in weighted_predictions]
                exercises_found = exercises_found.reindex(sorted_exercise_ids)
            
            return exercises_found
            
    return exercises

def sigmoid(x, k=1, x0=0):
    return 1 / (1 + np.exp(-k*(x-x0)))

def calculate_weighted_prediction(bayesian_avg, colab_prediction, count_items_rated):
    max_colab_weight = 0.95
    min_colab_weight = 0.2
    max_count = 100
    
    colab_weight = min_colab_weight + (max_colab_weight - min_colab_weight) * sigmoid(count_items_rated, k=0.1, x0=max_count/2)
    
    weighted_prediction = (bayesian_avg * (1 - colab_weight)) + (colab_prediction * colab_weight)    
    return weighted_prediction

def get_seasons():
    from datetime import datetime
    month = datetime.today().strftime("%m")
    
    print(month)