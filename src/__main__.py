import api
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api:api", host="0.0.0.0", port=8080, reload=True)