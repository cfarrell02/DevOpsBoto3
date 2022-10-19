# !/usr/bin/python3
# Cian Farrell - 20094046
from curses import keyname
from fileinput import filename
from multiprocessing.connection import wait
import boto3
import sys
import webbrowser
import subprocess
import requests
from datetime import datetime
import time

ec2 = boto3.resource('ec2')
s3 = boto3.resource('s3')
sns = boto3.client('sns')
ce = boto3.client('ce')
timestamp  = datetime.now().strftime("%H:%M:%S")
datestamp = datetime.now().strftime("%Y-%m-%d")
try:
    userData = str(open("userdata.sh",'r'))
except Exception as error:
    print(f"Error loading userdata\n{error}")


#Methods

def send_email(content):
    # sns.publish(
    #     TopicArn="arn:aws:sns:us-east-1:159322282447:Devops",
    #     Message=content
    # )
    print(f"--Email--\n{content}\n")


def launch_url(url):
    while(True):
        try:
            requests.get(url,timeout=2)
        except Exception:
            continue
        break
    print("Launched!!\n\nAccess this webserver on:",url)
    webbrowser.open_new_tab(url)


def uploadToS3(bucketName, body,key,ACLType = 'private',content = 'text/html'):
    try:
        s3.Object(bucketName,key).put(Body = body,ACL=ACLType,ContentType = content)
        print('Success')
    except Exception as error:
        print(f"Error uploading file {key} to bucket:\n{error}")

        
def create_instance():
    print("Creating instance...")

    #Creating Instance
    try:
        new_instances = ec2.create_instances(
        ImageId='ami-026b57f3c383c2eec',
        KeyName='MyKey',
        SecurityGroupIds=['sg-0507b2904716b1982'],
        MinCount=1,
        MaxCount=1,
        UserData = userData,
        TagSpecifications=[
                {
                    'ResourceType': 'instance' ,
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': f'WebServer {timestamp}'
                        },
                    ]
                },
            ],
        InstanceType='t2.nano')
    except Exception as error:
        print(f"Error launching instance:\n{error}")
        return
    print("Waiting for instance to initialise...")

    #Waits for instance to initialise fully
    new_instances[0].wait_until_running()
    new_instances[0].reload()
    url = f"http://{new_instances[0].public_ip_address}"

    #Writes URL to txt file
    with open('cfarrellurls.txt','wt') as file:
        file.write(f'Instance URL: {url}\n')
    print("Instance is running!")
    print("Waiting for web server to launch...")

    #Launch URL after waiting
    launch_url(url = url)
    return new_instances[0]


def monitor(instance):
    try:
        copyCommand = f"scp -o StrictHostKeyChecking=no -i MyKey.pem monitor.sh ec2-user@{instance.public_ip_address}:."
        runScript = f"ssh -o StrictHostKeyChecking=no -i MyKey.pem ec2-user@{instance.public_ip_address} 'sudo sh monitor.sh'"

    
        #Copy and runs Monitor.sh file
        var = subprocess.run([copyCommand],shell = True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
        process = subprocess.run([runScript],shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
        return process.stdout
    except Exception as e:
        print(f"Error launching monitor script on instance\n{e}")



def downloadFile(url):
    try:
        file = requests.get(url,stream=True).content
    except Exception as e:
        print(f"Error downloading file from {url}:\n{e}")
        file = None
    return file


def create_bucket():
    print("Creating S3 Bucket...")
    #Creates bucket name using a substring from the timestamp
    bucket_name = f"cfarrell{str(time.time())[-6:]}"
    s3Url = f'http://{bucket_name}.s3-website-us-east-1.amazonaws.com'


    try:
        bucket = s3.create_bucket(ACL='public-read',Bucket=bucket_name)
        print (bucket)
    except Exception as error:
        print (f"Error creating bucket:\n{error}")


    #Configures static website on bucket
    website_configuration = {
    'ErrorDocument': {'Key': 'error.html'},
    'IndexDocument': {'Suffix': 'index.html'},
    }

    #Writes image tag to the HTML file
    with open('index.html','a') as index:
       index.write(f'<img src="{s3Url}/logo.jpg">')
    bucket_website = s3.BucketWebsite(bucket_name) 
    bucket_website.put(WebsiteConfiguration=website_configuration)
   
    #Downloads and saves image from URL
    try:
        with open('logo.jpg','wb') as file:
            file.write(downloadFile('http://devops.witdemo.net/logo.jpg'))
    except Exception as error:
        print(f"Error loading logo.jpg file:\n{error}")

    #Uploads index and logo image to Bucket
    try:
        uploadToS3(bucketName=bucket_name,body=open('index.html','rb'),key = 'index.html',ACLType='public-read')
        uploadToS3(bucketName=bucket_name,body=open('logo.jpg','rb'),key='logo.jpg',ACLType='public-read',content='image/jpeg')
    except Exception as error:
        print(f"Error uploading files to S3 Bucket:\n{error}")
    print("Bucket with static website support created!!")

    #Writes bucket url to TXT file
    with open('cfarrellurls.txt','a') as file:
        file.write(f'Bucket URL: {s3Url}')

    #Launches URL
    launch_url(s3Url)

    return bucket

def calculate_costs(start_date = '2022-09-02',end_date = datestamp):
    try:
        response = ce.get_cost_and_usage(
            TimePeriod = {
                'Start':start_date,
                'End':end_date
            },
            Metrics = ['BlendedCost'],
            Granularity = 'MONTHLY'
        )

        return response['ResultsByTime'][0]['Total']['BlendedCost']['Amount']
    except Exception as error:
        print(f"Error finding usage costs:\n{error}")
        return None
    


def delete_all_buckets():
    print('Deleting Buckets')
    for bucket in s3.buckets.all():
        for object in bucket.objects.all():
            bucket.delete_objects(Delete= {'Objects': [{'Key':object.key}]})
        bucket.delete()


def delete_all_instances():
    print('Deleting instances')
    for inst in ec2.instances.all():
	    inst.terminate()


def deleteLines(file,index = 0):
    lines = open('index.html','r')
    lines = lines.readlines()
    lines = lines[:index]
    try:
        with open('index.html','w') as file:
            for line in lines:
                file.write(line)
    except Exception as error:
        print(f"Error loading {file}:\n{error}")

def check_args(arg):
    for val in sys.argv:
        if(arg==val):
            return True
    return False
        

#Call methods here

if(check_args('-d')):
    delete_all_buckets()
    delete_all_instances()

else:
    deleteLines('index.html',-1)
    instance = create_instance()
    bucket = create_bucket()
    monitorInfo = str(monitor(instance))
    send_email(f"Your instance is up and running!\n{monitorInfo}")
    print(f"Total costs: ${calculate_costs()} USD")