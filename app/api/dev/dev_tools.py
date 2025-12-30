from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/.well-known/appspecific/com.chrome.devtools.json")
async def devtools_probe(request: Request):
    client_host = request.client.host
    print(f"Chrome DevTools probe detected from {client_host}")
    return {"devtools": "detected"}
