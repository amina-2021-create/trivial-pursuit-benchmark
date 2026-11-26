
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select category
from "warehouse"."main"."mart_performance_categorie"
where category is null



  
  
      
    ) dbt_internal_test