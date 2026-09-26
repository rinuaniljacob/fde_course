import os
import base64
import json

from dotenv import load_dotenv
from openai import OpenAI

from fastapi import FastAPI, UploadFile, File

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app = FastAPI()


@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):

    image_bytes = await file.read()

    base64_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    prompt = """
    Identify all visible objects.

    Return only JSON.

    Example:

    {
        "person": 2,
        "chair": 4
    }
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )

    result = response.choices[0].message.content

    return {
        "result": result
    }