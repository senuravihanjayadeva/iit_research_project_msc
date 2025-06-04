from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from langchain_logic import get_recommendation
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Dental Recommendation App")
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
class SymptomInput(BaseModel):
    symptoms: str

class RecommendationResponse(BaseModel):
    recommendation: str

@app.post("/recommendation", response_model=RecommendationResponse)
def recommend_dental_treatment(input: SymptomInput, role: str = Header(...)):
    if role.lower() != "dentist":
        raise HTTPException(status_code=403, detail="Only Dentists can access this")

    recommendation = get_recommendation(input.symptoms)
    return {"recommendation": recommendation}
