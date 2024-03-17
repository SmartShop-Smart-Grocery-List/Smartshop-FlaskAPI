import pandas as pd
from app.db.models import db
from surprise import Dataset, Reader, SVD


data = None


class DataManager:
    def __init__(self) -> None:
        self.recipes = pd.merge(pd.read_csv("../data/Recipes.csv"), pd.read_csv("../data/Recipe_Bayesian_Ratings.csv"),
                                how='left', left_on='id', right_on='id', suffixes=(False, False))
        self.user_interactions = pd.concat([pd.read_csv("../data/Interactions.csv"),
                                            read_recipe_ratings_db().rename(columns={'recipe_id': 'id'}, inplace=True)],
                                           ignore_index=True)
        self.recipe_colab_filter = None
        self.recipe_colab_filter_trainset = None

    def setup_recipe_colab_filter(self):
        data = Dataset.load_from_df(self.user_interactions[["user_id", "id", "rating"]], Reader(rating_scale=(0, 5)))
        self.recipe_colab_filter_trainset = data.build_full_trainset()
        self.recipe_colab_filter = SVD(n_factors=1, n_epochs=1, biased=True, lr_all=0.005, reg_all=0.2)
        self.recipe_colab_filter.fit(self.recipe_colab_filter_trainset)

    def is_user_in_filter(self, ruid):
        try:
            self.recipe_colab_filter_trainset.knows_user(ruid)
            return True
        except ValueError:
            return False


def read_recipe_ratings_db():
    return pd.read_sql_table('recipe_ratings', con=db)
