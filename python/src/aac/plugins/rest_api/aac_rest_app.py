"""Module for configuring and maintaining the restful application and its routes."""
from fastapi import FastAPI

from aac.lang.active_context_lifecycle_manager import get_active_context

app = FastAPI()


@app.get("/")
def home():
    return {"Hello": "World"}


@app.get("/files")
def get_files():
    """Return a list of all files contributing definitions to the active context."""
    active_context = get_active_context()
    file_names = [definition.source_uri for definition in active_context.definitions]
    return {"files": set(file_names)}
