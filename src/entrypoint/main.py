import uvicorn

from src.entrypoint.bootstrap import setup

app = setup().start_app()


def main():
    uvicorn.run("src.entrypoint.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
