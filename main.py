import uvicorn

from src.bootstrap import bootstrap

app = bootstrap().start_app()

if __name__ == '__name__':
    uvicorn.run('main:app', reload=True)