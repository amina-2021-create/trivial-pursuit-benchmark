
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select difficulty
from "warehouse"."main"."mart_performance_difficulte"
where difficulty is null



  
  
      
    ) dbt_internal_test