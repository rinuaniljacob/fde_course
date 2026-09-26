from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# Request schema
class EmailRequest(BaseModel):
    email_content: str


@app.get("/")
def home():
    return {"message": "Email Routing API is running"}

@app.post("/route-email")
def route_email(request: EmailRequest):
    email_text = request.email_content

    prompt = f"""
You are an email routing assistant.

Your task:
Classify the email into ONE of these departments:

1. Sales
   - Pricing inquiries
   - Product demos
   - Partnerships
   - New customer interest

2. Customer Support
   - Refund requests
   - Complaints
   - Order issues
   - Delivery issues

3. Technical Support
   - Login issues
   - Bugs
   - API issues
   - Product crashes

4. Billing & Finance
   - Payment failures
   - Invoice requests
   - Subscription issues

5. HR & Recruitment
   - Job applications
   - Hiring related queries

6. General Inquiry
   - Anything unclear

Return output STRICTLY in JSON format:
{{
    "Department": "",
    "Confidence": "",
    "Reason": ""
}}  

Email:
{email_text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        result = response.choices[0].message.content

        # Convert string response into JSON
        parsed_result = json.loads(result)

        return parsed_result

    except Exception as e:
        return {"error": str(e)}