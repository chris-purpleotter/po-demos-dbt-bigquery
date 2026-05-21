FROM python:3.11-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv pip install --system --no-cache dbt-core dbt-bigquery google-cloud-storage pyarrow

COPY . .

RUN dbt deps 

RUN chmod +x run.sh

ENTRYPOINT ["./run.sh"]