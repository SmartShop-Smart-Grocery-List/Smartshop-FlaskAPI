import pandas as pd
import numpy as np


class Recommender:
    """
    Class for providing recommendations based on user preferences and context.

    Attributes:
        DVP_HIGH (float): High daily value percentage.
        DVP_MED (float): Medium daily value percentage.
        DVP_LOW (float): Low daily value percentage.
        context_weight (float): Weight for context in recommendation calculation.
        rec_weight (float): Weight for recommendation in recommendation calculation.

    Methods:
        __init__(self, weight=(0.75, 0.25)): Initializes the Recommender object.
        sigmoid(self, x, k=1, x0=0): Computes the sigmoid function.
        parse_pdv(self, dvp, multiplier): Parses the daily value percentage (DVP) based on multiplier.
        calculate_weighted_prediction(self, bayesian_avg, colab_prediction, count_items_rated): Calculates weighted prediction.
        get_exercise_with_configuration(self, exercises, user_id, user_ratings_count, colab_filter=None, type=None, body_part=None, equipment=None, level=None): Retrieves exercises with specified configuration.
        get_recipes_with_configuration(self, recipes, user_id, user_ratings_count, colab_filter=None, calories=None, daily=2000, fat="NULL", sat_fat="NULL", sugar="NULL", sodium="NULL", protein="NULL", carbs="NULL", tags=[]): Retrieves recipes with specified configuration.
        get_lifestyle_score(self, personalization): Calculates lifestyle score.
        get_recommendation(self, context, personalization): Generates recommendation based on context and personalization.
    """

    def __init__(self,  weight=(0.75, 0.25)):
        """
        Initializes the Recommender object.

        Args:
            weight (tuple): Tuple containing weights for context and recommendation.
        """
        self.DVP_HIGH = 40.0
        self.DVP_MED = 25.0
        self.DVP_LOW = 10.0
        self.context_weight, self.rec_weight = weight

    def sigmoid(self, x, k=1, x0=0):
        """
        Computes the sigmoid function.

        Args:
            x (float): Input value.
            k (float, optional): Sigmoid function parameter. Defaults to 1.
            x0 (float, optional): Sigmoid function parameter. Defaults to 0.

        Returns:
            float: Sigmoid function output.
        """
        return 1 / (1 + np.exp(-k * (x - x0)))

    def parse_pdv(self, dvp, multiplier):
        """
        Parses the daily value percentage (DVP) based on multiplier.

        Args:
            dvp (str): Daily value percentage category ('high', 'med', or 'low').
            multiplier (float): Value multiplier.

        Returns:
            tuple: Tuple containing low and high limits of the DVP.
        """
        low = 0.0
        high = float("inf")
        match dvp:
            case "high":
                low = self.DVP_HIGH * multiplier
            case "med":
                high = self.DVP_HIGH * multiplier
                low = self.DVP_LOW * multiplier
            case "low":
                high = self.DVP_MED * multiplier
        return low, high

    def calculate_weighted_prediction(self, bayesian_avg, colab_prediction, count_items_rated):
        """
        Calculates weighted prediction.

        Args:
            bayesian_avg (float): Bayesian average.
            colab_prediction (float): Collaborative filtering prediction.
            count_items_rated (int): Count of items rated by the user.

        Returns:
            float: Weighted prediction.
        """
        max_colab_weight = 0.95
        min_colab_weight = 0.2
        max_count = 100

        colab_weight = min_colab_weight + (max_colab_weight - min_colab_weight) * self.sigmoid(count_items_rated, k=0.1,
                                                                                               x0=max_count / 2)

        weighted_prediction = (bayesian_avg * (1 - colab_weight)) + (colab_prediction * colab_weight)
        return weighted_prediction

    def get_exercise_with_configuration(self, exercises, user_id, user_ratings_count, colab_filter=None, type=None,
                                        body_part=None,
                                        equipment=None, level=None):
        """
        Retrieves exercises with specified configuration.

        Args:
            exercises (DataFrame): DataFrame containing exercise data.
            user_id (int): User ID.
            user_ratings_count (int): Count of items rated by the user.
            colab_filter (object, optional): Collaborative filtering model. Defaults to None.
            type (str, optional): Exercise type. Defaults to None.
            body_part (str, optional): Body part targeted by the exercise. Defaults to None.
            equipment (str, optional): Equipment used in the exercise. Defaults to None.
            level (str, optional): Difficulty level of the exercise. Defaults to None.

        Returns:
            DataFrame: DataFrame containing exercises that match the specified configuration.
        """

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
                            weighted_predictions.append(
                                (exercise_id, self.calculate_weighted_prediction(colab_prediction, user_ratings_count)))
                        weighted_predictions = sorted(weighted_predictions, key=lambda x: x[1], reverse=True)
                        sorted_exercise_ids = [pred[0] for pred in weighted_predictions]
                        exercises_found = exercises_found.reindex(sorted_exercise_ids)

                    return exercises_found

            return exercises
        
    def get_time_tags(self):
        from datetime import datetime
        tags = []

        month = int(datetime.today().strftime("%m"))
        if 3 <= month <= 5:
            tags.append('spring')
        elif 6 <= month <= 8:
            tags.append('summer')
        elif 9 <= month <= 11:
            tags.append('fall')
        else:
            tags.append('winter')

        hour_of_day = int(datetime.today().strftime("%H"))
        if 5 <= hour_of_day <= 12:
            tags.append('breakfast')
        if 11 <= hour_of_day <= 4:
            tags.append('lunch')
        return tags

    def get_recipes_with_configuration(self, recipes, user_id, user_ratings_count, colab_filter=None, calories=None,
                                       daily=2000,
                                       fat="NULL", sat_fat="NULL", sugar="NULL", sodium="NULL", protein="NULL",
                                       carbs="NULL",
                                       tags=[]):
        """
        Retrieves recipes with specified configuration.

        Args:
            recipes (DataFrame): DataFrame containing recipe data.
            user_id (int): User ID.
            user_ratings_count (int): Count of items rated by the user.
            colab_filter (object, optional): Collaborative filtering model. Defaults to None.
            calories (int, optional): Maximum calorie limit. Defaults to None.
            daily (int, optional): Daily calorie intake. Defaults to 2000.
            fat (str, optional): Fat category ('high', 'med', or 'low'). Defaults to "NULL".
            sat_fat (str, optional): Saturated fat category ('high', 'med', or 'low'). Defaults to "NULL".
            sugar (str, optional): Sugar category ('high', 'med', or 'low'). Defaults to "NULL".
            sodium (str, optional): Sodium category ('high', 'med', or 'low'). Defaults to "NULL".
            protein (str, optional): Protein category ('high', 'med', or 'low'). Defaults to "NULL".
            carbs (str, optional): Carbohydrates category ('high', 'med', or 'low'). Defaults to "NULL".
            tags (list, optional): List of recipe tags. Defaults to [].

        Returns:
            DataFrame: DataFrame containing recipes that match the specified configuration.
        """
        high_calorie_lim = float("inf")
        low_calorie_lim = 0

        multiplier = 2000 / daily

        if calories != None:
            high_calorie_lim = max(calories + 100, calories * 1.1)
            low_calorie_lim = min(calories - 100, calories * 0.9)

        low_fat_lim, high_fat_lim = self.parse_pdv(fat, multiplier)
        low_sat_fat_lim, high_sat_fat_lim = self.parse_pdv(sat_fat, multiplier)
        low_sugar_lim, high_sugar_lim = self.parse_pdv(sugar, multiplier)
        low_sodium_lim, high_sodium_lim = self.parse_pdv(sodium, multiplier)
        low_protein_lim, high_protein_lim = self.parse_pdv(protein, multiplier)
        low_carbs_lim, high_carbs_lim = self.parse_pdv(carbs, multiplier)

        recipes_filter = ((low_calorie_lim <= recipes['calories']) & (recipes['calories'] <= high_calorie_lim) &
                          (low_fat_lim <= recipes['total fat (PDV)']) & (recipes['total fat (PDV)'] <= high_fat_lim) &
                          (low_sat_fat_lim <= recipes['saturated fat (PDV)']) & (
                                  recipes['saturated fat (PDV)'] <= high_sat_fat_lim) &
                          (low_sugar_lim <= recipes['sugar (PDV)']) & (recipes['sugar (PDV)'] <= high_sugar_lim) &
                          (low_sodium_lim <= recipes['sodium (PDV)']) & (recipes['sodium (PDV)'] <= high_sodium_lim) &
                          (low_protein_lim <= recipes['protein (PDV)']) & (
                                  recipes['protein (PDV)'] <= high_protein_lim) &
                          (low_carbs_lim <= recipes['carbohydrates (PDV)']) & (
                                  recipes['carbohydrates (PDV)'] <= high_carbs_lim))

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

                weighted_predictions.append(
                    (recipe_id, self.calculate_weighted_prediction(bayesian_avg, colab_prediction, user_ratings_count)))
            predictions_sorted = sorted(weighted_predictions, key=lambda x: x[1], reverse=True)
            sorted_recipe_ids = [pred[0] for pred in predictions_sorted]
            recipes_found_sorted = recipes_found_sorted.reindex(sorted_recipe_ids)
        
        time_tags = self.get_time_tags()
        recipes_with_time_context = []
        for tag in time_tags:
            if tag in tags:
                continue
            recp = self.get_recipes_with_configuration(calories=calories, daily=daily, fat=fat, sat_fat=sat_fat, sugar=sugar, sodium=sodium, protein=protein, carbs=carbs, tags=tags + [tag])
            if not(type(recp) == bool and recp == False):
                recipes_with_time_context.append(recp[:5])

        if recipes_with_time_context == []:
            return recipes_found_sorted
        
        recipes_with_time_context = pd.concat(recipes_with_time_context, ignore_index=True)
        recipes_found_sorted = pd.concat([recipes_with_time_context[:2], recipes_found_sorted], ignore_index=True).drop_duplicates()

        return recipes_found_sorted

    def activity_coefficient(activity):
        match activity:
            case 'sedentary':
                return 1.2
            case 'lightly active':
                return 1.375
            case 'moderately active':
                return 1.55
            case 'very active':
                return 1.725
            case 'extra active':
                return 1.9
    def get_bmr(self, gender, height, weight, age):
        """
        Calculate Basal Metabolic Rate (BMR) based on gender, height, weight, and age.

        BMR is the number of calories required to keep your body functioning at rest.

        Args:
            gender (str): Gender of the individual ('m' for male, 'f' for female).
            height (float): Height of the individual in centimeters.
            weight (float): Weight of the individual in kilograms.
            age (int): Age of the individual in years.

        Returns:
            float: Basal Metabolic Rate (BMR) in calories per day.
        """
        if gender == 'm':
            return 66.473 + 13.7516 * weight + 5.0033 * height - 6.755 * age
        else:
            return 655.0955 + 9.5634 * weight + 1.8496 * height - 4.6756 * age
    def get_lifestyle_score(self, personalization):
        """
        Calculates lifestyle score.

        Args:
            personalization: Personalization data.

        Returns:
            dict: Dictionary containing lifestyle scores.
        """
        user_data = personalization


        age = user_data['age']
        height = user_data['height'] #cm
        weight = user_data['weight'] #kg
        gender = user_data['gender']
        cur_activity = user_data['current_level_of_activity']
        goal_activity = user_data['goal_level_of_activity']
        weight_goal = user_data['weight_goal']

        ratio = lambda x,y: self.activity_coefficient(x) / self.activity_coefficient(y)

        current_bmr = self.get_bmr(gender, height, weight, age) * self.activity_coefficient(cur_activity)
        ideal_bmr = self.get_bmr(gender, height, weight_goal, age) * self.activity_coefficient(goal_activity)



        wellness_score = round(5 - (abs(ideal_bmr - current_bmr))/ideal_bmr * 5,2)

        fitness = personalization.fit_data

        average_sleep = sum([fit.sleep for fit in fitness])/len(fitness)
        average_calories = sum([fit.calories for fit in fitness])/len(fitness)

        (fitness.sleep * 5 / 8) + (5 - (fitness.calories/ideal_bmr)*5)


        diet_score = 5 # when use is able to input stuff

        return {
            "wellness_score": wellness_score,
            "diet_score": 1,
            "fitness_score": 1,
            "lifestyle_score": round((wellness_score + diet_score + fitness_score) / 3, 2)
        }


    def get_recommendation(self, context, personalization):
        """
        Generates recommendation based on context and personalization.

        Args:
            context: Contextual information.
            personalization: Personalization data.

        Returns:
            dict: Dictionary containing recommendation scores.
        """
        return {
            "wellness_score": 1,
            "diet_score": 1,
            "fitness_score": 1,
            "lifestyle_score": 1
        }
