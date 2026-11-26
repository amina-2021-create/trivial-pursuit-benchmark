
  
  create view "warehouse"."main"."stg_questions__dbt_tmp" as (
    

SELECT *
FROM read_parquet('/home/aaouari/projects/trivial-pursuit/silver/questions_clean.parquet')
  );
