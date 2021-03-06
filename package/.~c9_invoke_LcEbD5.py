import json
import boto3
import os

users_table = os.environ['USERS_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(users_table)


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
    user_id = path.split("/")[-1]
    pet_id=path.split("/")[-3]# ["user", "id"]
    
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