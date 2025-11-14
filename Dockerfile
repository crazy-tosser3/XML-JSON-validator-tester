FROM python:3.13-slim

WORKDIR /app

RUN pip3 install uv --break-system-packages

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

EXPOSE 8000

CMD ["uv", "run", "main_server.py"]
