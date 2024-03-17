from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ExerciseRating(db.Model):
    __tablename__ = 'exercise_ratings'
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    exercise_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"ExerciseRating(User ID = {self.user_id}, RecipeID = {self.exercise_id}, Rating = {self.rating})"


class RecipeRating(db.Model):
    __tablename__ = 'recipe_ratings'
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"RecipeRating(User ID = {self.user_id}, RecipeID = {self.recipe_id}, Rating = {self.rating})"


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(128), nullable=False)
    current_daily_calories = db.Column(db.Integer)
    goal_daily_calories = db.Column(db.Integer)
    name = db.Column(db.String(256))
    age = db.Column(db.Integer)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    gender = db.Column(db.String(1))
    current_level_of_activity = db.Column(db.String(20))
    goal_level_of_activity = db.Column(db.String(20))
    weight_goal = db.Column(db.String(10))

    def __repr__(self):
        return f"""User(User ID = {self.user_id}, Username = {self.username}, Current Daily Calories = {self.current_daily_calories}, 
                Goal Daily Calories = {self.goal_daily_calories}, Name = {self.name}, Age = {self.age}, Height = {self.height}, 
                Weight = {self.weight}, Gender = {self.gender}, Current Level of Activity = {self.current_level_of_activity}, 
                Goal Level of Activity = {self.goal_level_of_activity}, Weight Goal = {self.weight_goal})"""
