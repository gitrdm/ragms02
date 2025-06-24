from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    """
    .. :no-index:

    Health check endpoint.
    Returns status ok if the service is running.
    """
    return {"status": "ok"}
