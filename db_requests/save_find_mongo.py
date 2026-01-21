from local_settings import MONGODB_URL_EDIT
from pymongo import MongoClient
import datetime

client = MongoClient(MONGODB_URL_EDIT)
db = client["ich_edit"]
queries_collection = db["010825-ptm_Kirill_Vigutov"]


def get_popular_queries():
    return list(queries_collection.find().sort("count", -1).limit(5))

def get_recent_queries():
    return list(queries_collection.find().sort("last_used", -1).limit(5))



def save_query(query_type, key, result_count=None):
    queries_collection.update_one(
        {
            "query_type": query_type,
            "keyword": key
            },
    {
            "$inc": {"count": 1}, #Увеличивает значение поля count на 1
            "$set": {
                "last_used": datetime.datetime.utcnow() #Устанавливает поле last_used равным текущему времени
            },
            "$setOnInsert": { #Эти поля будут установлены только при вставке нового документа
                "created_at": datetime.datetime.utcnow(),
                "result_count": result_count}
            },
            upsert=True)

#Если документ найден и обновлён, $setOnInsert ничего не делает.
#
# Если документ не найден и создаётся новый, $setOnInsert устанавливает поля только при этой вставке.