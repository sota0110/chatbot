# import platform
# import os
# import openai
# from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
import pymysql
from ..models import Article

class Sql:
    def __init__(self):
        pymysql.install_as_MySQLdb()
        answer = list(Article.objects.all().values())
        print(answer)