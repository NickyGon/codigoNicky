import json
import boto3
import os

##s

users_table = os.environ['USERS_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(users_table)
client = boto3.client('sns')

def putAdopter(event, context):
    print(json.dumps({"running": True}))
    print(json.dumps(event))
    path = event["path"]
    user_id = path.split("/")[-1] # ["user", "id"]
    
    body = json.loads(event["body"])
    print(body)
    print(user_id)
   
    item = {
        'pk': user_id,
        'sk': 'profile',
        'nombre': body["nombre"],
        'apellido_paterno': body["apellido_paterno"],
        'apellido_materno': body["apellido_materno"],
        'edad': body["edad"],
        'sexo': body["sexo"],
        'email': body["email"]
    }
    
    email=body["email"]
    
    response = client.subscribe(
    TopicArn='arn:aws:sns:us-east-1:366482477391:AdoptionEmailSNS',
    Protocol='email',
    Endpoint=body["email"],
    ReturnSubscriptionArn=True
    )
    

    
    print(json.dumps(item))
    table.put_item(
       Item=item
    )
    
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
def getAdopter(event, context):
    print(json.dumps({"running": True}))
    print(json.dumps(event))
    path = event["path"]
    user_id = path.split("/")[-1] # ["user", "id"]
    
    response = table.get_item(
        Key={
            'pk': user_id,
            'sk': 'profile'
        }
    )
    item = response['Item']
    return {
        'statusCode': 200,
        'body': json.dumps(item)
    }

def createAdoption(event,context):
    print(json.dumps({"running": True}))
    print(json.dumps(event))
    path = event["path"]
    user_id = path.split("/")[-3]
    pet_id=path.split("/")[-1]# ["user", "id"]
    
    body = json.loads(event["body"])
    print(body)
    print(user_id)
   
    item = {
        'pk': user_id,
        'sk': pet_id,
        'house_type':body["house_type"]
    }
    
    
    print(json.dumps(item))
    table.put_item(
       Item=item
    )
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
def deleteAdoption(event,context):
    print(json.dumps({"running": True}))
    print(json.dumps(event))
    
    path = event["path"]
    user_id = path.split("/")[-3]
    pet_id=path.split("/")[-1]# ["user", "id"]
    
    response2 = table.get_item(
        Key={
            'pk': user_id,
            'sk': 'profile'
        }
    )
    
    
    item3=response2['Item']
    itemEm=response2['Item']['email']
    itemNa=response2['Item']['nombre']
    
    
    table.delete_item(
            Key={
                 'pk': user_id,
                 'sk': pet_id
            }
        )
        
        
    response = client.publish(
    TopicArn='arn:aws:sns:us-east-1:366482477391:AdoptionEmailSNS',
    Message='La adopcion por parte de '+itemNa+' ha sido realizada',
    Subject=itemEm
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(itemEm)
    }
    
   