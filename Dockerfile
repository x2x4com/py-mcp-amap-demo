FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /app

COPY . /app/

RUN uv sync

EXPOSE 3001

CMD ["uv", "run", "main.py"]