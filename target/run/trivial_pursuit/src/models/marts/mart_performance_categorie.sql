
    

    create  table
      "warehouse"."main"."mart_performance_categorie__dbt_tmp"
  
    
    as (
      

SELECT
    ai_model,
    category,

    COUNT(*) AS total_questions,

    SUM(CASE WHEN ai_correct = TRUE THEN 1 ELSE 0 END)
        AS correct_answers,

    SUM(CASE WHEN ai_correct = FALSE THEN 1 ELSE 0 END)
        AS incorrect_answers,

    SUM(CASE WHEN ai_correct IS NOT NULL THEN 1 ELSE 0 END)
        AS evaluated_questions,

    ROUND(
        100.0 * SUM(CASE WHEN ai_correct = TRUE THEN 1 ELSE 0 END)
        / NULLIF(
            SUM(CASE WHEN ai_correct IS NOT NULL THEN 1 ELSE 0 END),
            0
        ),
        2
    ) AS accuracy_percent

FROM "warehouse"."main"."int_questions"

GROUP BY
    ai_model,
    category
    );
    
  