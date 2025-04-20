from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from primer_logic import process_sequence, clean_fasta_sequence

app = FastAPI(title="Primer Design API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PrimerResponse(BaseModel):
    primers: List[dict]
    gc_plot: str

@app.post("/design", response_model=PrimerResponse)
async def design_primers(sequence: str = Form(...)):
    try:
        # Clean the input sequence
        cleaned_sequence = clean_fasta_sequence(sequence)
        if not cleaned_sequence:
            raise HTTPException(status_code=400, detail="Invalid FASTA sequence")
        
        # Process the sequence and get results
        result = process_sequence(cleaned_sequence)
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 
    return "Hello World"
 