# Ingestion — Pull, Convert, Land

A scheduled Cloud Run job pulls CSV from an external API, converts it to Parquet, and appends an immutable file to a GCS bucket — giving you a durable, replayable record of every fetch.

```mermaid
flowchart TB
    SRC[(source API)]
    CRON_A["Cloud Scheduler<br/>(ingestion cron)"]

    subgraph A["Ingestion (Cloud Run)"]
        direction LR
        FETCH["fetch CSV<br/>via API"] --> CONV["convert<br/>CSV → Parquet"]
    end

    BUCKET[("gs://parquets")]

    CRON_A -. "triggers" .-> A
    A -. "GET" .-> SRC
    SRC -- "CSV" --> A
    A --> BUCKET

    classDef ingest fill:#e1f5ff,stroke:#0288d1,color:#01579b
    class CRON_A,FETCH,CONV ingest
```

# Transformation — Scheduled dbt Pipeline

A separate Cloud Run job runs dbt build on its own schedule, reading raw Parquet from the bucket and producing modeled tables in BigQuery. dbt knows nothing about how the files got there; it just sees a raw layer to transform.

```mermaid
flowchart TB
    BUCKET[("gs://parquets")]
    CRON_B["Cloud Scheduler<br/>(dbt cron)"]

    subgraph B["Transformation (Cloud Run)"]
        direction LR
        DBT["dbt build"]
    end

    BQ[("BigQuery")]

    CRON_B -. "triggers" .-> B
    BUCKET --> B --> BQ

    classDef transform fill:#fff4e1,stroke:#f57c00,color:#e65100
    class CRON_B,DBT transform
```


# Independent & Orchestrated Ingestion + Transformation
Either pipeline can be redeployed, re-run, or replaced without the other knowing. And because the dbt job is decoupled, it can be wired to fire on a schedule, reactively when new Parquet lands (via Eventarc), or both.

```mermaid
flowchart TB
    SRC[(source API)]
    CRON_A["Cloud Scheduler<br/>(ingestion cron)"]
    CRON_B["Cloud Scheduler<br/>(dbt cron)"]
    EVT["Eventarc<br/>(GCS finalize)"]

    subgraph A["Ingestion (Cloud Run)"]
        direction LR
        FETCH["fetch CSV<br/>via API"] --> CONV["convert<br/>CSV → Parquet"]
    end

    subgraph B["Transformation (Cloud Run)"]
        direction LR
        DBT["dbt build"]
    end

    BUCKET[("gs://parquets")]
    BQ[("BigQuery")]

    CRON_A -. "triggers" .-> A
    CRON_B -. "triggers" .-> B
    BUCKET -. "new object" .-> EVT
    EVT -. "triggers" .-> B
    A -. "GET" .-> SRC
    SRC -- "CSV" --> A
    A --> BUCKET --> B --> BQ

    classDef ingest fill:#e1f5ff,stroke:#0288d1,color:#01579b
    classDef transform fill:#fff4e1,stroke:#f57c00,color:#e65100
    classDef eventbus fill:#ede7f6,stroke:#5e35b1,color:#311b92
    class CRON_A,FETCH,CONV ingest
    class CRON_B,DBT transform
    class EVT eventbus
```