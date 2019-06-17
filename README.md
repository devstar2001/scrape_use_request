
## Basic Setting Values 

        thread_count = 2            # thread count
        today_repeat_time = 60 * 60 * 8   # every 8 hours repeat scrapping about today's data in thread_today.py
        network_repeat_time = 60 * 60 * 2   # time to wait for restarting script if network disconnected
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
        It can be excuted forever.
        e.g, scrape once every two hours
            While True:
                .....
                logger.info(str(today_date) + ": all success!")
                time.sleep(60*60*2)
                
# Running script on AWS EC2

## Create Ubuntu EC2 Instance

1. Log in AWS and then go to AWS EC2
2. Choose Instances/INSTANCES one the left panel.
3. Click Launch Instance on the right panel.
4. Select Ubuntu Server 18.04 LTS (HVM), SSD Volume Type(Free tier eligible)
5. Check t2.micro CPU type and click Review Launch
6. Create a new key pair , or choose an existing key pair if you already have some key pair.
 
## Connect to EC2 Instance with putty 
Please refer to this url.
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/putty.html?icmpid=docs_ec2_console

1. login with putty

        Session/
            ip address : ip or domain name 
            e.g: ec2-18-191-201-102.us-east-2.compute.amazonaws.com
        Connection/SSH/Auth
            private key file for authentication:    ppk file name
            e.g: first.ppk
        
2. user name : ubuntu

## Run Script

1. Check if python3 is installed.
        
        ubuntu@ip-172-31-25-106:~$ python3
        
        Python 3.6.8 (default, Jan 14 2019, 11:02:34)
        [GCC 8.0.1 20180414 (experimental) [trunk revision 259383]] on linux
        Type "help", "copyright", "credits" or "license" for more information.
        >>>

2. Check if pip3 is installed.  
        
        ubuntu@ip-172-31-25-106:~$ pip3 --version
        pip 9.0.1 from /usr/lib/python3/dist-packages (python 3.6)
        
        #if not , install pip3
        
        sudo apt install python3-pip
        sudo apt-get update

3. Download source from github.

        git clone https://github.com/devstar2001/scrape_use_request.git
    
4. Install packages required.

        pip3 install -r requirements.txt
       
5. Run Screen command and run script. 
    A user close putty and then script running is stopped.
    To solve this , use screen command.
    Please refer to this url.
    
    https://linuxize.com/post/how-to-use-linux-screen/ 

        screen -S t2
        
        python3 thread_date_scope.py
        
        # to exit screen
         press ctrl + a , d
        
        # to check log and files download
        cd playground && ls
        
        # to enter into t2 screen
        screen -r t2         

6. Download file from remote to local 
    
    [scp command usage:]    

        D:\Work>scp ubuntu@ec2-18-191-201-102.us-east-2.compute.amazonaws.com:/home/ubuntu/scrape_use_request/playground/* .
        06-16-2019.csv                                                                        100% 9593KB   1.3MB/s   00:07
        06-17-2019.csv                                                                        100%  300KB 299.5KB/s   00:01        
    
    [FTP/SFTP]