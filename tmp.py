import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_DATABASE')}"
print(DATABASE_URL)
