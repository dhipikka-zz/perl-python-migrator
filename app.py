from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from translator import PerlToPythonMigrator
import tempfile
import os

app = FastAPI(title="AI Perl → Python Migrator")
#need to add openapikey security scheme later inside the parantheses
migrator = PerlToPythonMigrator()

class MigrationResponse(BaseModel):
    python_code: str
    confidence: float
    changes: list[str]
    warnings: list[str]

@app.post("/migrate", response_model=MigrationResponse)
async def migrate_perl(perl_file: UploadFile = File(...)):
    """Upload Perl file → Get Python migration"""
    if not perl_file.filename.endswith('.pl'):
        raise HTTPException(400, "Please upload a .pl file")
    
    perl_content = await perl_file.read()
    perl_code = perl_content.decode('utf-8')
    
    result = migrator.migrate(perl_code)
    
    return MigrationResponse(
        python_code=result['code'],
        confidence=result['confidence'],
        changes=result['changes'],
        warnings=result['warnings']
    )

@app.get("/migrate/text")
async def migrate_text(perl_code: str):
    """Paste Perl code directly"""
    result = migrator.migrate(perl_code)
    return {"python_code": result['code']}

@app.get("/examples/{filename}")
async def get_example(filename: str):
    return FileResponse(f"examples/{filename}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
