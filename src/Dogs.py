import json
import boto3
import os

users_table = os.environ['USERS_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(users_table)
client = boto3.client('sns')

def updatePet(event, context):
    print(json.dumps({"running": True}))
    print(json.dumps(event))
    path = event["path"]
    account_id = path.split("/")[-1]
    
    
    body = json.loads(event["body"])
    print(body)
    
    item={
        'pk': account_id,
        'sk': 'profile',
        'nombre': body["nombre"],
        'estado_de_salud': body["estado_de_salud"],
        'edad': body["edad"],
        'ubicacion':body["ubicacion"],
        'IMG_1':body["IMG_1"],
        'IMG_2':body["IMG_2"],
        'IMG_3':body["IMG_3"],
        'IMG_4':body["IMG_4"]
    }
    
    table.put_item(
       Item=item
    )
    
def getPet(event,context):
    print(json.dumps({"running": True}))
    print(json.dumps(event))
    path = event["path"]
    pet_id = path.split("/")[-1] # ["user", "id"]
    
    response = table.get_item(
        Key={
            'pk': pet_id,
            'sk': 'profile'
        }
    )
    
    item = response['Item']
    return {
        'statusCode': 200,
        'body': json.dumps(item)
    }
    
def deletePet(event, context):
    print(json.dumps({"running": True}))
    print(json.dumps(event))
    
    path = event["path"]
    pet_id=path.split("/")[-1]# ["user", "id"]
    
    response2 = table.get_item(
        Key={
            'pk': pet_id,
            'sk': 'profile'
        }
    )
    
    
    table.delete_item(
            Key={
                 'pk': pet_id,
                 'sk':'profile'
            }
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }