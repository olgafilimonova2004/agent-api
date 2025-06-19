import uvicorn

from src.bootstrap import bootstrap

app = bootstrap().start_app()

if __name__ == '__main__':    
    uvicorn.run('main:app', host='127.0.0.1', reload=True)