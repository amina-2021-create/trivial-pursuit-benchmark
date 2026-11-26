
  
  create view "warehouse"."main"."int_questions__dbt_tmp" as (
    

SELECT
    question,
    category,
    difficulty,
    type,
    incorrect_answers,
    correct_answer,
    ai_answer,
    ai_correct,
    response_time,
    ai_model,
    source_file,

    CASE
        WHEN ai_answer IS NULL
          OR TRIM(ai_answer) = ''
        THEN TRUE
        ELSE FALSE
    END AS is_unanswered,

    CASE
        WHEN ai_correct = TRUE THEN 'Correcte'
        WHEN ai_correct = FALSE THEN 'Incorrecte'
        ELSE 'Non évaluée'
    END AS answer_status,

    CASE
        WHEN response_time IS NULL
          OR response_time < 0
        THEN NULL
        ELSE response_time
    END AS clean_response_time

FROM "warehouse"."main"."stg_questions"
  );
