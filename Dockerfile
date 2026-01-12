FROM python:3.11-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/app

RUN python -m pip install --no-cache-dir dbt-core dbt-bigquery

COPY . .

RUN dbt deps

ENTRYPOINT ["dbt"]
CMD ["run"]