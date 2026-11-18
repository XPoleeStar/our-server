
import os
from io import BytesIO
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
load_dotenv()

import asyncio

EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(conf)

async def send_email(
    email: str, 
    subject: str, 
    body: str, 
    file_path: str = None, 
    filename: str = "report.xlsx"
):
    attachments = []
    if file_path:
        attachments.append({
            "file": file_path,
            "filename": os.path.basename(file_path),
            "mime_type": EXCEL_MIME
        })
    message = MessageSchema(
        subject=subject,
        recipients=["proshkimax2@gmail.com"],
        body=body,
        subtype=MessageType.html,
        attachments=attachments  
    )
    await fm.send_message(message)
