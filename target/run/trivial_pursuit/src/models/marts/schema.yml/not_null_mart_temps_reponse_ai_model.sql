
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select ai_model
from "warehouse"."main"."mart_temps_reponse"
where ai_model is null



  
  
      
    ) dbt_internal_test