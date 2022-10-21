import boto3

s3 = boto3.resource('s3')
ec2 = boto3.resource('ec2')

def delete_all_buckets():
    print('Deleting Buckets')
    for bucket in s3.buckets.all():
        print('Deleting Bucket: '+bucket.name)
        for object in bucket.objects.all():
            bucket.delete_objects(Delete= {'Objects': [{'Key':object.key}]})
        bucket.delete()


def delete_all_instances():
    print('Deleting Instances')
    for inst in ec2.instances.all():
        if(inst.state['Name'] == 'running'):
            print('Deleting Instance: '+inst.id)
            inst.terminate()

delete_all_instances()
delete_all_buckets()

