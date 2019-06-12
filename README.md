"# scrape_use_request"
 
## Basic Setting Values 

        thread_count = 2            # thread count
        time_period = 60 * 1        # time to wait for restarting script if network disconnected
        start_date = '01-01-1989'   # start date
        end_date = '12-01-1989'     # end date
        saveDir = './playground'    # root folder
        log_location = './logs'     # log folder
        
        
## Introduce Python Script Files

### - thread_date_scope.py

        It operates as multi-thread method over date scope.
        If internet disconnected then it wait for time_period , request again about that page.
        It record all states. 
        
### - thread_today.py

        It operates as multi-thread method about today's articles.
        If internet disconnected then it wait for time_period , request again about that page.
        It record all states. 