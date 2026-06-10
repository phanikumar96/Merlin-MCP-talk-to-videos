import tempfile
import torch

from fastapi import FastAPI, UploadFile, File, Form
from transformers import AutoModelForCausalLM

app = FastAPI()

MODEL_ID = "NemoStation/Marlin-2B"

print("Loading Marlin...")

marlin = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    trust_remote_code=True,
    dtype=torch.bfloat16,
    device_map={"": "cuda"},
)

marlin.compile()

print("Marlin loaded.")


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/describe")
async def describe_video(
    file: UploadFile = File(...)
):

    tmp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    )

    tmp.write(await file.read())
    tmp.close()

    result = marlin.caption(tmp.name)

    return {
        "caption": result["caption"],
        "scene": result["scene"],
        "events": result["events"]
    }


@app.post("/search")
async def search_video(
    file: UploadFile = File(...),
    query: str = Form(...)
):

    tmp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    )

    tmp.write(await file.read())
    tmp.close()

    result = marlin.find(
        tmp.name,
        event=query
    )

    return {
        "query": query,
        "raw": result["raw"],
        "span": result["span"],
        "format_ok": result["format_ok"]
    }