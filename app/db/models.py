from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import List

db = SQLAlchemy()


class ExerciseRating(db.Model):
    __tablename__ = 'exercise_ratings'
    exercise_id = Column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.user_id'), nullable=False)
    rating = Column(Integer, nullable=False)

    def __repr__(self):
        return f"ExerciseRating(User ID = {self.user_id}, RecipeID = {self.exercise_id}, Rating = {self.rating})"


class RecipeRating(db.Model):
    __tablename__ = 'recipe_ratings'
    recipe_id = Column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.user_id'), nullable=False)
    rating = Column(Integer, nullable=False)

    def __repr__(self):
        return f"RecipeRating(User ID = {self.user_id}, RecipeID = {self.recipe_id}, Rating = {self.rating})"


class FitBit(db.Model):
    __tablename__ = 'fitbit_data'
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.user_id'), primary_key=True, nullable=False)
    date = Column(Text)
    distance = Column(Text)
    steps = Column(Text)
    sleep = Column(Text)
    calories = Column(Text)
    restingHeartRate = Column(Text)
    maxHeartRate = Column(Text)


class User(db.Model):
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
