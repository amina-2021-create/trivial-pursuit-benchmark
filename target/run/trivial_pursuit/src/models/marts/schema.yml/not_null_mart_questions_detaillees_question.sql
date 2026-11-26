
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select question
from "warehouse"."main"."mart_questions_detaillees"
where question is null



  
  
      
    ) dbt_internal_test