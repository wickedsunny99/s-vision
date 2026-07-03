from fastapi import APIRouter, File, UploadFile

router = APIRouter()


@router.post("/process_frame")
async def process_frame(file: UploadFile = File(...)):
    if not file.filename.endswith(".png"):
        return {"error": "Only PNG files are supported"}

    # Process the file
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}
