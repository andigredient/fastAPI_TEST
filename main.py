from fastapi import FastAPI, HTTPException
from app.database import add_link, find_link_original, delete_expired_links, delete_last_accessed_links, update_url_db, get_stats_db, find_link_short, delete_link, following_links, delete_link
import random
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from typing import Optional
from datetime import datetime, timedelta
app = FastAPI()



class ShortenRequest(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class UpdateCodeRequest(BaseModel):
    new_code: str

URL = "http://localhost:8000/"
COUNT_DAYS_DELETED = 5
delete_expired_links()
delete_last_accessed_links()

@app.get("/")
async def read_root():
    return {"message": "Приложение запущено"}


def generate_short(original_url):
    count = 0
    short = ""
    expires_at = datetime.now() + timedelta(days=COUNT_DAYS_DELETED)

    if find_link_original(original_url):
        return find_link_original(original_url)
    else:
        while count <= 6:  
            rand =  random.randint(48, 122)
            if rand <= 57 or rand >= 97:
                short = short + chr(rand)
                count = count + 1
        add_link(original_url, short, expires_at)
        return short
    

@app.post("/links/shorten")
def create_short_link(request: ShortenRequest):
    expires_at = datetime.now() + timedelta(days=COUNT_DAYS_DELETED)
    alias = request.custom_alias
    original_url = request.original_url

    if not(alias):
        short_code = generate_short(original_url) 
        return short_code
    else:
        result = find_link_short(alias)
        if (result):
            return {"result": 0}
        else:
            add_link(original_url, alias, expires_at )
            return alias




@app.delete("/links/{short_code}")
def delete_short_link(short_code: str):
        delete_link(short_code) 
        print("Ссылка удалена")
        return {"Ссылка удалена"}


@app.get("/{short_code}")
def redirect_to_original_url(short_code:str):

    if find_link_short(short_code):
        print(short_code)
        following_links(short_code)
        return RedirectResponse(url=find_link_short(short_code))
    else:
        raise HTTPException(status_code=404, detail=f"Ссылка не найдена {find_link_short(short_code)}")


@app.get("/links/{short_code}/stats")
def get_stats(short_code:str):
    result = get_stats_db(short_code)
    if result:
        print(result)
        return result
    else:
        return {'result': "Данные не найдены"}


@app.get("/links/search")
def search_by_original_url(original_url: str):
    short_code = find_link_original(original_url)
    if not(short_code):
        return { "result": "Такого кода не существует"}
    else:
        return { "result": f"http://localhost:8000/{short_code}"}



@app.put("/links/{short_code_update}")
def update_url(short_code_update: str, request: UpdateCodeRequest):

    if find_link_short(short_code_update):
        if update_url_db(request.new_code, short_code_update):
            return {'result': "Код ссылки изменен"}
    else:
        return {'result': "Такого кода не существует"}