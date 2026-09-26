from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.get("/hello")
def say_hello():
    return {"message": "Hello from FastAPI"}