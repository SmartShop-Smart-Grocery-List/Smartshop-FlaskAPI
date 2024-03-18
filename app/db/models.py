from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import List

db = SQLAlchemy()


class ExerciseRating(db.Model):
    """
    A class to represent the ratings given by users to exercises.

    Attributes:
        exercise_id (int): The unique identifier for the exercise.
        user_id (int): The unique identifier for the user who rated the exercise.
        rating (int): The rating given by the user to the exercise.
    """
    __tablename__ = 'exercise_ratings'
    exercise_id = Column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.user_id'), nullable=False)
    rating = Column(Integer, nullable=False)

    def __repr__(self):
        return f"ExerciseRating(User ID = {self.user_id}, RecipeID = {self.exercise_id}, Rating = {self.rating})"


class RecipeRating(db.Model):
    """
    A class to represent the ratings given by users to recipes.

    Attributes:
        recipe_id (int): The unique identifier for the recipe.
        user_id (int): The unique identifier for the user who rated the recipe.
        rating (int): The rating given by the user to the recipe.
    """
    __tablename__ = 'recipe_ratings'
    recipe_id = Column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.user_id'), nullable=False)
    rating = Column(Integer, nullable=False)

    def __repr__(self):
        return f"RecipeRating(User ID = {self.user_id}, RecipeID = {self.recipe_id}, Rating = {self.rating})"


class FitBit(db.Model):
    """
    A class to represent FitBit data for users.

    Attributes:
        user_id (int): The unique identifier for the user.
        date (str): The date of the FitBit data entry.
        distance (str): The distance covered.
        steps (str): The number of steps taken.
        sleep (str): The sleep data.
        calories (str): The calories burned.
        restingHeartRate (str): The resting heart rate.
        maxHeartRate (str): The maximum heart rate.
    """
    __tablename__ = 'fitbit_data'
    fitbit_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.user_id'), nullable=False)
    date = Column(Text)
    distance = Column(Text)
    steps = Column(Text)
    sleep = Column(Text)
    calories = Column(Text)
    restingHeartRate = Column(Text)
    maxHeartRate = Column(Text)


class User(db.Model):
    """
    A class to represent users.

    Attributes:
        user_id (int): The unique identifier for the user.
        username (str): The username of the user.
        current_daily_calories (int): The current daily calorie intake of the user.
        goal_daily_calories (int): The goal daily calorie intake of the user.
        name (str): The name of the user.
        age (int): The age of the user.
        height (int): The height of the user.
        weight (int): The weight of the user.
        gender (str): The gender of the user.
        current_level_of_activity (str): The current level of activity of the user.
        goal_level_of_activity (str): The goal level of activity of the user.
        weight_goal (str): The weight goal of the user.
        recipe_ratings (List[RecipeRating]): The list of recipe ratings given by the user.
        fitbit_data (List[FitBit]): The list of FitBit data entries for the user.
        exercise_ratings (List[ExerciseRating]): The list of exercise ratings given by the user.
    """
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    username = Column(Text, nullable=False)
    current_daily_calories = Column(Integer)
    goal_daily_calories = Column(Integer)
    name = Column(Text)
    age = Column(Integer)
    height = Column(Integer)
    weight = Column(Integer)
    gender = Column(Text)
    current_level_of_activity = Column(Text)
    goal_level_of_activity = Column(Text)
    weight_goal = Column(Text)
    recipe_ratings: Mapped[List["RecipeRating"]] = relationship()
    fitbit_data: Mapped[List["FitBit"]] = relationship()
    exercise_ratings: Mapped[List["ExerciseRating"]] = relationship()

    def __repr__(self):
        return f"""User(User ID = {self.user_id}, Username = {self.username}, Current Daily Calories = {self.current_daily_calories}, 
                Goal Daily Calories = {self.goal_daily_calories}, Name = {self.name}, Age = {self.age}, Height = {self.height}, 
                Weight = {self.weight}, Gender = {self.gender}, Current Level of Activity = {self.current_level_of_activity}, 
                Goal Level of Activity = {self.goal_level_of_activity}, Weight Goal = {self.weight_goal})"""
