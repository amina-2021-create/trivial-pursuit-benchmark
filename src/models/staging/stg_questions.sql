{{ config(materialized='view') }}

SELECT *
FROM read_parquet('/home/aaouari/projects/trivial-pursuit/silver/questions_clean.parquet')