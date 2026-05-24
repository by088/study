from fastapi import APIRouter

router = APIRouter(prefix="/v1/stories", tags=["stories"])


@router.get("")
def list_stage2_stories():
    return {
        "phase": "stage2",
        "stories": [
            "US-01 register",
            "US-02 login",
            "US-03 search rooms",
            "US-04 seat availability",
            "US-05 reserve seat",
            "US-06 cancel reservation",
            "US-07 check in",
            "US-09 role management",
            "US-10 role assignment",
            "US-15 system parameter management",
            "US-18 default handling"
        ]
    }
