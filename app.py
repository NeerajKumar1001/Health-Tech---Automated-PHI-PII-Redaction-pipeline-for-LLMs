import os

os.environ["PYTHONUNBUFFERED"] = "1"


from fastapi import FastAPI, Header, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


from redactor import redact_text

from otp_service import save_otp, verify_otp
from email_service import send_otp_email

from auth import create_token, verify_token



app = FastAPI()



# ---------------- TEMPLATES ---------------- #

templates = Jinja2Templates(
    directory="templates"
)



# ---------------- TEMP USERS DB ---------------- #

users = {

    "doctor1": {
        "password": "1234",
        "role": "doctor"
    },

    "patient1": {
        "password": "1234",
        "role": "patient"
    }

}



# ---------------- REQUEST MODELS ---------------- #


class TextInput(BaseModel):

    text: str



class OTPRequest(BaseModel):

    email: str



class OTPVerify(BaseModel):

    email: str
    otp: str



class LoginRequest(BaseModel):

    username: str
    password: str





# ---------------- FRONTEND PAGES ---------------- #


@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(

        "index.html",

        {
            "request": request
        }

    )



@app.get("/dashboard")
def dashboard():

    return FileResponse(
        "templates/dashboard.html"
    )





# ---------------- OTP LOGIN ---------------- #


@app.post("/send-otp")
def send_otp(data: OTPRequest):


    otp = save_otp(
        data.email
    )


    send_otp_email(
        data.email,
        otp
    )


    return {

        "message":
        "OTP sent successfully",

        "email":
        data.email

    }





@app.post("/verify-otp")
def verify_otp_api(data: OTPVerify):


    if verify_otp(
        data.email,
        data.otp
    ):


        role = "patient"


        if "doctor" in data.email.lower():

            role = "doctor"



        token = create_token({

            "email":
            data.email,

            "role":
            role

        })


        return {


            "message":
            "Login successful",


            "token":
            token,


            "role":
            role

        }



    return {


        "error":
        "Invalid OTP"

    }







# ---------------- USER LOGIN ---------------- #


@app.post("/login")
def login(data: LoginRequest):


    user = users.get(
        data.username
    )



    if not user or user["password"] != data.password:


        return {

            "error":
            "Invalid credentials"

        }




    token = create_token({

        "username":
        data.username,


        "role":
        user["role"]

    })




    return {


        "token":
        token,


        "role":
        user["role"]

    }









# ---------------- PROTECTED REDACT API ---------------- #


@app.post("/redact")
def redact(

    data: TextInput,

    authorization: str = Header(None)

):


    # AUTH CHECK

    if not authorization:


        return {

            "error":
            "Unauthorized"

        }





    token = authorization.replace(

        "Bearer ",

        ""

    )



    user = verify_token(

        token

    )



    if not user:


        return {

            "error":
            "Invalid token"

        }





    # REDACTION ENGINE


    redacted_text, entities = redact_text(

        data.text

    )




    return {


        "user":
        user,


        "original":
        data.text,


        "redacted":
        redacted_text,


        "entities_found":
        len(entities),


        "entity_types":
        list(set(entities))

    }