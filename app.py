from website.app import app, HOST, PORT, DEBUG

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("website.app:app", host=HOST, port=PORT, reload=False)