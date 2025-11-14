import logging
import os
import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app.services.pipeline_runner import run_pipeline
from app.stages.stage_1_idea_engine import suggest_niche_via_model
from pydantic import BaseModel
from app.config import (
    AUTOVIDAI_DEV_MODE,
    GEMINI_API_KEY,
    PEXELS_API_KEY,
    ELEVENLABS_API_KEY,
    SHOTSTACK_API_KEY,
)

class PipelineRequest(BaseModel):
    niche: str
    upload: bool = False
    verbose: bool = False

class PipelineResponse(BaseModel):
    job_id: str | None = None  # placeholder for future queue integration
    stage: str | None
    final_video_url: str | None
    uploaded: bool
    error: str | None


class SuggestResponse(BaseModel):
    niche: str | None = None
    error: str | None = None

app = FastAPI(title="AutoVidAI Backend", version="0.1.0")

@app.on_event("startup")
def startup():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/deps")
def health_deps(live: bool = Query(False, description="Perform non-destructive live checks against providers")):
    """Report dependency readiness.

    live=true performs minimal, non-destructive calls when feasible to verify credentials.
    """
    result = {"dev_mode": AUTOVIDAI_DEV_MODE}

    # Gemini
    gemini = {"ok": False, "message": "", "model": os.getenv("GEMINI_MODEL", "")}
    if not GEMINI_API_KEY:
        gemini.update(message="GEMINI_API_KEY missing")
    else:
        if live:
            model = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
            try:
                r = requests.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}",
                    params={"key": GEMINI_API_KEY}, timeout=10
                )
                if r.status_code == 404:
                    # Fetch available models to suggest correct ones.
                    suggest = []
                    try:
                        rlist = requests.get(
                            "https://generativelanguage.googleapis.com/v1beta/models",
                            params={"key": GEMINI_API_KEY}, timeout=10
                        )
                        if rlist.ok:
                            data = rlist.json()
                            for m in data.get("models", [])[:10]:
                                name = m.get("name", "")
                                if "/models/" in name:
                                    name = name.split("/models/")[-1]
                                if name.startswith("gemini-2.5") or name.startswith("gemini-2.0"):
                                    suggest.append(name)
                    except Exception:
                        pass
                    gemini.update(ok=False, message=f"Model {model} 404", suggestions=suggest)
                else:
                    gemini.update(ok=r.ok, message=f"HTTP {r.status_code}")
            except Exception as e:
                gemini.update(ok=False, message=str(e))
        else:
            gemini.update(ok=True, message="Key present")
    result["gemini"] = gemini

    # Pexels
    pexels = {"ok": False, "message": ""}
    if not PEXELS_API_KEY:
        pexels.update(message="PEXELS_API_KEY missing")
    else:
        if live:
            try:
                r = requests.get(
                    "https://api.pexels.com/videos/search",
                    headers={"Authorization": PEXELS_API_KEY},
                    params={"query": "nature", "per_page": 1}, timeout=10,
                )
                pexels.update(ok=r.ok, message=f"HTTP {r.status_code}")
            except Exception as e:
                pexels.update(ok=False, message=str(e))
        else:
            pexels.update(ok=True, message="Key present")
    result["pexels"] = pexels

    # ElevenLabs
    elabs = {"ok": False, "message": ""}
    if not ELEVENLABS_API_KEY:
        elabs.update(message="ELEVENLABS_API_KEY missing")
    else:
        if live:
            try:
                r = requests.get(
                    "https://api.elevenlabs.io/v1/models",
                    headers={"xi-api-key": ELEVENLABS_API_KEY}, timeout=10
                )
                elabs.update(ok=r.ok, message=f"HTTP {r.status_code}")
            except Exception as e:
                elabs.update(ok=False, message=str(e))
        else:
            elabs.update(ok=True, message="Key present")
    result["elevenlabs"] = elabs

    # Shotstack (presence check; sandbox/prod both allowed; 404 status treated as neutral)
    shotstack = {"ok": False, "message": "", "stage": os.getenv("SHOTSTACK_STAGE", "v1")}
    if not SHOTSTACK_API_KEY:
        shotstack.update(message="SHOTSTACK_API_KEY missing")
    else:
        if live:
            try:
                # Stage or production status endpoint; tolerate 404
                stage = os.getenv("SHOTSTACK_STAGE", "v1")
                r = requests.get(f"https://api.shotstack.io/{stage}/status", timeout=10)
                if r.status_code == 404:
                    shotstack.update(ok=True, message="Status endpoint 404 (tolerated)")
                else:
                    shotstack.update(ok=r.ok, message=f"HTTP {r.status_code}")
            except Exception as e:
                shotstack.update(ok=True, message=f"Key present; ping failed: {e}")
        else:
            shotstack.update(ok=True, message="Key present")
    result["shotstack"] = shotstack

    return result


@app.get("/providers/gemini/models")
def gemini_models():
    """Return the list of model names available to the configured GEMINI_API_KEY."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY missing")
    try:
        r = requests.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            params={"key": GEMINI_API_KEY}, timeout=15
        )
        if not r.ok:
            return {"ok": False, "status": r.status_code, "body": r.text}
        data = r.json()
        names = []
        for m in data.get("models", []):
            name = m.get("name")
            # Names sometimes include full resource path; extract final segment after '/models/'.
            if name:
                if "/models/" in name:
                    name = name.split("/models/")[-1]
                names.append(name)
        return {"ok": True, "models": names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/providers/gemini/ping")
def gemini_ping(model: str = Query(..., description="Model name to ping, e.g., gemini-1.5-flash")):
    """Ping a specific Gemini model with a GET to the models/{model} endpoint."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY missing")
    try:
        r = requests.get(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}",
            params={"key": GEMINI_API_KEY}, timeout=15
        )
        return {"ok": r.ok, "status": r.status_code, "body": r.text[:400]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pipeline", response_model=PipelineResponse)
def pipeline(req: PipelineRequest):
    if req.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    result = run_pipeline(req.niche, upload=req.upload)
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])
    return PipelineResponse(
        job_id=None,
        stage=result.get("stage"),
        final_video_url=result.get("final_video_url"),
        uploaded=result.get("uploaded", False),
        error=result.get("error"),
    )


@app.post("/pipeline/suggest", response_model=SuggestResponse)
def suggest():
    """Return a single suggested niche/topic generated by the model.

    This endpoint is intended for the opt-in 'Suggest a niche' flow in the UI.
    """
    suggestion = suggest_niche_via_model()
    if not suggestion:
        raise HTTPException(status_code=500, detail="Could not generate a suggestion")
    return SuggestResponse(niche=suggestion)
