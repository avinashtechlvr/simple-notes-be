from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import time

from models import User, Note
from db import (
    is_email_available,
    create_user,
    delete_user,
    create_post,
    delete_post,
    get_user_by_username,
    get_post_by_id,
    get_all_posts,
    update_post
)
from manage import create_access_token, verify_token, authenticate_user

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Configure CORS
origins = [
    "http://localhost:4321",  
    "simple-notes-ui.pages.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "*"
    ],  # Allow all methods or specify specific ones ["GET", "POST", ...]
    allow_headers=["*"],  # Allow all headers or specify specific ones
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
def root():
    return {"message": "Hello World"}


class userCreate(BaseModel):
    name: str
    email: str
    password: str


class userResponse(BaseModel):
    id: int
    name: str
    email: str


class CreateNote(BaseModel):
    title: str
    content: str
    user_id: int

class UpdateNote(BaseModel):
    title: str
    content: str
    post_id: int


class DeleteNote(BaseModel):
    id: int
    user_id: int


class NoteResponse(BaseModel):
    user_id: int
    id: int


@app.post("/user/register", response_model=userResponse)
async def register_user(user_data: userCreate):
    email_available = is_email_available(user_data=user_data)
    print("Email available", email_available)
    if email_available:
        raise HTTPException(status_code=400, detail="Email already exists")
    new_user = create_user(user_data)
    return new_user

@app.get("/user/getdetails", response_model=userResponse)
async def get_user_details(token: str = Depends(oauth2_scheme)):
    username = verify_token(
        token,
        credentials_exception=HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )
    user = await get_user_by_username(username)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail=f"user id with {user.id} not found")
    

@app.delete("/user/{user_id}")
async def remove_user(user_id: int, token: str = Depends(oauth2_scheme)):
    username = verify_token(
        token,
        credentials_exception=HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )
    user = await get_user_by_username(username)
    if user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Operation not permitted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    res = delete_user(user_id)
    if res:
        return {"message": "successfully deleted user"}
    else:
        raise HTTPException(status_code=400, detail=f"user id with {user_id} not found")


@app.post("/user/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    print("FormData", form_data)
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/notes/create")
async def create_new_post(form_data: CreateNote, token: str = Depends(oauth2_scheme)):
    username = verify_token(
        token,
        credentials_exception=HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )
    print("Usernmae", form_data)
    created = create_post(form_data)
    return created

@app.post("/notes/update")
async def update_note(form_data: UpdateNote, token: str = Depends(oauth2_scheme)):
    print("FormData", form_data)
    username = verify_token(
        token,
        credentials_exception=HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )
    user = await get_user_by_username(username)
    post = await get_post_by_id(form_data.post_id)
    if post is None:
        raise HTTPException(
            status_code=400, detail=f"post with postid: {form_data.post_id} not found"
        )
    if user.id != post.user_id:
        raise HTTPException(
            status_code=403,
            detail="Operation not permitted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    created = update_post(post_data=form_data)
    if created:
        return {"message": "successfully updated post"}
    else:
        raise HTTPException(status_code=400, detail="unable to update post")
    
    pass

@app.delete("/notes/delete/{postId}")
async def remove_post(postId: int, token: str = Depends(oauth2_scheme)):
    username = verify_token(
        token,
        credentials_exception=HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )
    user = await get_user_by_username(username)
    post = await get_post_by_id(postId)
    if post is None:
        raise HTTPException(
            status_code=400, detail=f"post with postid: {postId} not found"
        )
    if user.id != post.user_id:
        raise HTTPException(
            status_code=403,
            detail="Operation not permitted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    created = delete_post(postId)
    if created:
        return {"message": "successfully deleted post"}
    else:
        raise HTTPException(status_code=400, detail="unable to delete post")


@app.get("/users/{user_id}/notes")
async def read_user_notes(user_id: int, token: str = Depends(oauth2_scheme)):
    username = verify_token(
        token,
        credentials_exception=HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )

    # Fetch the user based on the username from the token's payload
    user = await get_user_by_username(username)

    # Optionally, check if the user is requesting their own notes or has permission to view others' notes
    if user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Operation not permitted",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get all notes for the user
    notes = get_all_posts(user_id)

    return notes
