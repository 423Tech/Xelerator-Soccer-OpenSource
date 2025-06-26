# data.py | IntelliFusion Version 0.1.9(202308032000) Developer Alpha
from pathlib import Path
from peewee import *
import time
from . import config

# 基础类
Date = time.strftime("%Y%m", time.localtime())
RoBotName = config.QkJson().read("model","number")
APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
DATABASE_FILE = DATA_DIR / f"Xel-{RoBotName}.{Date}.sqlite"

db = SqliteDatabase(DATABASE_FILE)

class BaseModel(Model):
    class Meta:
        database = db

class Positions(BaseModel):
    XPosition = IntegerField(null=False, default="not_required")#To request Model
    YPosition = IntegerField(null=False, default="not_required")#To request Model
    ZPosition = IntegerField(null=False, default="not_required")#To request Model
    BallXPosition = IntegerField(null=False, default="not_required")#To request Model
    BallYPosition = IntegerField(null=False, default="not_required")#To request Model

    class Meta:
        # 定义表名
        table_name = 'Positions'

def SetupDatabase():
    db.create_tables([Positions])
