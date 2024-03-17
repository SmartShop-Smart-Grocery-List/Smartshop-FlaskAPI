import os

class Config:
    SUPABASE_PROJECT_URL: str = os.getenv('SUPABASE_PROJECT_URL')
    SUPABASE_API_KEY: str = os.getenv('SUPABASE_API_KEY')
    SQLALCHEMY_DATABASE_URI: str = os.getenv('SQLALCHEMY_DATABASE_URI')

