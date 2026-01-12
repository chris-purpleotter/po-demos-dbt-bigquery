FROM python:3.11-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/app

RUN pip install --no-cache-dir dbt-bigquery

COPY . .

RUN dbt deps

ENTRYPOINT ["dbt"]
CMD ["run"]