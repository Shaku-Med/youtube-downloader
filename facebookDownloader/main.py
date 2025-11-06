import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

# Support running as a script: `python main.py`
if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(__file__))
    from router import router as facebook_router  # type: ignore
else:
    from .router import router as facebook_router


app = FastAPI(title="Facebook Downloader", version="1.0.0")
app.include_router(facebook_router, prefix="/facebook", tags=["facebook"])


TEMPLATES_DIR = str(Path(__file__).resolve().parent / "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)

