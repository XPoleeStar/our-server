from fastapi import FastAPI, Request, HTTPException, status
# database
import sqlite3
connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    fullname TEXT NOT NULL,
    students_group TEXT NOT NULL,
    login TEXT NOT NULL PRIMARY KEY,
    password TEXT NOT NULL
)
''')

cursor.execute("DROP TABLE IF EXISTS present")

cursor.execute('''
CREATE TABLE present  (
    fullname TEXT NOT NULL,
    students_group TEXT NOT NULL
)
''')

connection.commit()

valid_key = None
app = FastAPI()

@app.post("/")
async def root(request: Request):
    global valid_key

    login = request.headers.get("user-login")
    if not login: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="login is null")

    password = request.headers.get("user-password")
    if not password: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="password is null")

    key = await request.body()
    if not key: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="key is null")

    # is teacher
    if login == "2" and password == "2":
        valid_key = key
        return

#database
    cursor.execute("SELECT password, fullname, students_group FROM students WHERE login = ?", (login,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="login not found")
    valid_password, fullname, group = result
    if password == valid_password:
        if key == valid_key:
            cursor.execute("INSERT INTO present(fullname, students_group) VALUES(?, ?)", (fullname, group))
            connection.commit()
        else: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="wrong key")
    else: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="wrong password")

#отключаем бд + сервер
@app.on_event("shutdown")
def shotdown():
    connection.close()
