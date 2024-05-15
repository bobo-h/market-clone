from fastapi import FastAPI,UploadFile,Form,Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import sqlite3

con=sqlite3.connect('db.db' ,check_same_thread=False)
# js에서 받아온 데이터를 db.db파일과 연결시키는 것
cur=con.cursor()
# db에 커서라는 개념이 있는데 그것을 이용해서 특정 인서트하거나 셀렉트 할 때 사용하기위해 작성함

cur.execute(f"""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,  
                title TEXT NOT NULL,
                image BLOB,
                price INTEGER NOT NULL,
                description TEXT,
                place TEXT NOT NULL,
                insertAt INTEGER NOT NULL
            );
            """)

app=FastAPI()

@app.post('/items')
async def create_item(image:UploadFile, 
                title:Annotated[str,Form()], 
                # 타이틀 정보가 Form데이터 형식으로 string(문자열)로 올것이라는 뜻
                price:Annotated[int,Form()], 
                description:Annotated[str,Form()], 
                place:Annotated[str,Form()],
                insertAT:Annotated[int,Form()]
                ):
    
    image_bytes = await image.read()
    # 받은 데이터를 넣어줄 건데 image는 블롭타입으로 굉장히 크게오기에 image데이터를 read할 시간이 필요하다.
    cur.execute(f"""
                INSERT INTO items(title,image,price,description,place,insertAT)
                VALUES 
                ('{title}','{image_bytes.hex()}',{price},'{description}','{place}',{insertAT})
                """)
    # 읽힌 정보를 db에 인설트 해줄 것이고 자바스크립트의 백틱같은 역할을 하는 f문자열이라 알려주는 것("""내용""")을 작성한다.
    # price는 숫자 str이기에 따옴표를 작성하지 않아도 된다.
    # 이미지는 바로위에서 image_bytes로 바꾸어 준 것을 가져온다. hex() 문법은 16진법으로 바꾸어 주는 것(db에서 확인가능)
    # INSERT INTO를 통해서 items(등등)테이블에 VALUS값을 넣어줄 것이라는 의미
    con.commit()
    return '200'
# 서버쪽에서 완료가 되면 200이라는 상태코드를 내려주는 로직

@app.get('/items')
async def get_items():
    con.row_factory = sqlite3.Row
    #컬럼명을 같이 가져오는 문법
    cur = con.cursor()
    #db를 가져오면서 connection의 현재 위치를 cursor라고 하는 위치를 업데이트 해줘야 데이터가 제대로 들어온다.
    rows = cur.execute(f"""
                       SELECT * from items;
                       """).fetchall()
    
    return JSONResponse(jsonable_encoder(dict(row)for row in rows))
# 데이터를 가져오는 로직. 데이터를 모두 가져오려면 SELECT문(SQL문)을 사용해야한다. SELECT all from 테이블명
# 가져오는 문법이기에 execute뒤에 fetch all을 작성해주면 좋다.
# 그리고 자바스크립트로 가져온 데이터를 JSON Response로 보내주는 것
# rows값을 그대로 응답해주는 것보다 컬럼명과 함께 id대로, 타이틀대로 구분지어 받아야한다.
# 그러면 object기능을 아는 dictionary라는 것을 이용하면 좋다.
# return JSONResponse(rows) - > return JSONResponse(dict(rows))
# rows = [['id',1],['title','사진'],['price',5000],['description','분홍하늘사진'],...]로 데이터를 받아오게된다.
# 그렇지만 이것은 array형식이고 각각의 array들을 앞 뒤로 객체로 만들어야 하는데
# rows중에 각각의 array를 돌면서 그 array를 dictionary, 객체 형태로 만들어주는 문법을 사용해야한다.(dict(row) for row in rows)
# {"id":1, "title":'사진', "price":5000, "decription":"분홍하늘사진"...} 그러면 이와같은 형식으로 바뛰어 데이터를 내려주게된다.
# 위 문법을 json형식으로 바꿔서 해야 response 할 수 있다.
# 맨위에 from fastapi.encoders import jsonable_encoder 추가, 아래에도 jsonable_encoder추가 작성

# 이미지 응답하는 API로 item_id를 같이 넣어서 보내주면 그 아이템에 맞는 이미지(hex, 16진법)를 불러오게 한다.
@app.get('/images/{item_id}')
async def get_image(item_id):
    cur = con.cursor()
    image_bytes = cur.execute(f"""
                              SELECT image from items WHERE id={item_id}
                              """).fetchone()[0]
    
    # hex이미지를 가져와 컨텐츠로 응답하겠다.
    return Response(content=bytes.fromhex(image_bytes))

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
# 루트 패쓰는 맨 밑에 작성하기