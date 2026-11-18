from fastapi import FastAPI, Request, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd #ипорт в зеленую хуйню
import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.exceptions import InvalidSignature
from mailer import send_email

# database
import sqlite3
connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    fullname TEXT NOT NULL,
    students_group TEXT NOT NULL,
    login TEXT NOT NULL PRIMARY KEY,
    password TEXT NOT NULL,
    public_key TEXT
)
''')

cursor.execute("DROP TABLE IF EXISTS present")

cursor.execute('''
CREATE TABLE present  (
    login TEXT NOT NULL PRIMARY KEY,
    fullname TEXT NOT NULL,
    students_group TEXT NOT NULL
)
''')

connection.commit()

try:
    os.remove("result.xlsx")
except FileNotFoundError:
    pass

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"]
)

valid_key = None

@app.post("/")
async def root(request: Request):
    global valid_key

    login = request.headers.get("user-login")
    if not login: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Укажите логин")

    password = request.headers.get("user-password")
    if not password: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Укажите пароль")

    key = await request.body()
    if not key: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="key is null")

    # is teacher
    if login == os.getenv("TEACHER_LOGIN") and password == os.getenv("TEACHER_PASSWORD"):
        valid_key = key
    
    signature = request.headers.get("user-signature")
    if not signature: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="signature is null")

    public_key = request.headers.get("user-public-key")
    if not public_key: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="public_key is null")

#database
    cursor.execute("UPDATE students SET public_key = ? WHERE login = ? AND (public_key IS NULL OR public_key = '')", (public_key, login))
    connection.commit()
    cursor.execute("SELECT password, fullname, students_group, public_key, login FROM students WHERE login = ?", (login,))
    result = cursor.fetchone()
    
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="login not found")
    valid_password, fullname, group, public_key_b64, students_login = result
    if password == valid_password:
        if key == valid_key:
            verify_signature(public_key_b64, signature, key, login, fullname, group)  
        else: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="wrong key")
    else: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="wrong password")

def verify_signature(public_key_b64: str, signature_b64: str, signed_data: str, login, fullname, group):
    print(public_key_b64, signature_b64)
    public_key_bytes = base64.b64decode(public_key_b64)
    signature_bytes = base64.b64decode(signature_b64)

    public_key = ec.EllipticCurvePublicKey.from_encoded_point(
        curve=ec.SECP256R1(),
        data=public_key_bytes
    )

    r = int.from_bytes(signature_bytes[:32], byteorder="big")
    s = int.from_bytes(signature_bytes[32:], byteorder="big")
    der_signature = utils.encode_dss_signature(r, s)
    try:
        public_key.verify(
        signature=der_signature,
        data=signed_data,
        signature_algorithm=ec.ECDSA(hashes.SHA256())
        ) 
        cursor.execute("INSERT INTO present(login, fullname, students_group) VALUES(?, ?, ?) ON CONFLICT(login) DO NOTHING", (login, fullname, group))
        connection.commit()
    except InvalidSignature: return 

@app.post("/recovery")
async def recovery(request):
    login = request.headers.get("user-login")
    if not login: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Укажите логин")

    password = request.headers.get("user-password")
    if not password: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Укажите пароль")

    public_key = request.headers.get("user-public-key")
    if not public_key: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="public_key is null")

    cursor.execute("SELECT password FROM students WHERE login = ?", (login,))
    result = cursor.fetchone()
    if not result: return
    valid_password = result[0]
    if password == valid_password:
        cursor.execute("UPDATE students SET public_key = ? WHERE login = ?", (public_key, login))
    else: return

@app.on_event("shutdown")
async def shutdown():
#import to green xyinia
    df = pd.read_sql_query("SELECT students_group, fullname FROM present", connection)
    df = df.sort_values(
    by=["Группа", "ФИО"],
    key=lambda s: s.str.lower().str.replace("ё", "е")
)
    df.to_excel("result.xlsx", index=False)
    connection.close()
    #send a mail
 
    await send_email("", "test 3", "результат посещаемости", "result.xlsx")
