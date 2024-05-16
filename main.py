from fastapi import FastAPI,UploadFile,Form,Response,Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from typing import Annotated
import sqlite3

con=sqlite3.connect('db.db' ,check_same_thread=False)
# js에서 받아온 데이터를 db.db파일과 연결시키는 것
cur=con.cursor()
# db에 커서라는 개념이 있는데 그것을 이용해서 특정 인서트하거나 셀렉트 할 때 사용하기위해 작성함

app=FastAPI()

SECRET = "coding-study"
manager = LoginManager(SECRET,'/login')

@manager.user_loader()
def query_user(data):
    WHERE_STATEMENTS = f'id="{data}"'
    if type(data) == dict:
        WHERE_STATEMENTS = f'id="{data['id']}"'
    # 객체 형태로 넘어오게 되면 그 안에 있는 id를 빼서 써야하기에 WHERE_STATEMENTS를 사용해야한다.
    con.row_factory = sqlite3.Row
    #컬럼명을 같이 가져오는 문법
    cur = con.cursor()
    #db를 가져오면서 connection의 현재 위치를 cursor라고 하는 위치를 업데이트 해줘야 데이터가 제대로 들어온다.
    user = cur.execute(f"""
                       SELECT * from users WHERE {WHERE_STATEMENTS}
                       """).fetchone()
    return user
# users테이블 안의 모든(*) 값을 조회하는데 
# 첫번째 WHERE_STATEMENTS 뜻 = 그냥 id, str값으로 넘어오게되면 바로 맨아래 {WHERE_STATEMENTS}값에 들어가고
# 두번째 WHERE_STATEMENTS 뜻 = 아까 수정한 id, name, email을 sub에 넣어준 값(dict)으로 오게 되면 그 안의 id를 찾고나서 위와 같은 곳에 들어간다.

@app.post('/login')
def login(id:Annotated[str,Form()],
            password:Annotated[str,Form()]):
    user = query_user(id)
    # 해당유저가 존재하는지 조회해보는 것
    if not user: 
        raise InvalidCredentialsException
        # 파이썬에서 에러메세지를 던지는 문법 = raise = 클라이언트 에러 상태코드 401을 자동으로 내려준다.
    elif password != user['password']:
        raise InvalidCredentialsException
    
    access_token = manager.create_access_token(data={
        'sub': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
    })
    
    return {'access_token':access_token}
    # 클라이언트에게 엑세스토큰을 부여하기 위해 값 변경
    # return "HI" 였다면
    # 리턴값이 보인다는 것은 정상작동이라는 것. 그렇기에 return을 HI로 해도 status는 상태코드 200을 내려준다.
    # f12의 network의 login의 response페이지에서 return값인 "HI"확인가능, headers에서는 상태코드 200 OK 확인가능

@app.post('/signup')
def signup(id:Annotated[str,Form()],
           password:Annotated[str,Form()],
           name:Annotated[str,Form()],
           email:Annotated[str,Form()]):
    cur.execute(f"""
                INSERT INTO users(id,name,email,password)
                VALUES ('{id}','{name}','{email}','{password}')
                """)
    con.commit()
    return '200'

@app.post('/items')
async def create_item(image:UploadFile, 
                title:Annotated[str,Form()], 
                # 타이틀 정보가 Form데이터 형식으로 string(문자열)로 올것이라는 뜻
                price:Annotated[int,Form()], 
                description:Annotated[str,Form()], 
                place:Annotated[str,Form()],
                insertAT:Annotated[int,Form()],
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
async def get_items(user=Depends(manager)):
    # user=Depends(manager) = 유저가 인증된 상태에서만 응답을 보낼 수 있게 하는 것(헤더에 엑세스토큰을 넣어서 보내야지 서버가 알 수 있을 것)
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