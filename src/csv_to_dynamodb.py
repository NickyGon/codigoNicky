import json
import csv
import boto3


def handler(event, context):
    
    region ='us-east-1'
    record_list = []
    
    try:
        
        s3 = boto3.client('s3')
        
        dynamodb = boto3.client('dynamodb',region_name = region )
        
        
        
        bucket = event['Records'][0]['s3']['bucket']['name']
        
        key = event['Records'][0]['s3']['object']['key']
        
        print('Bucket' , bucket , 'Key',key)
        
        csv_file = s3.get_object(Bucket = bucket ,Key = key )
        
        record_list = csv_file['Body'].read().decode('utf-8').split('\n')
        
        csv_reader = csv.reader(record_list,delimiter=',',quotechar='"')
        
        bucket_name = "csv-dynamodb-lambda2"
        
        for row in csv_reader:
            animal_id = row[0]
            health_status = row[1]
            age = row[2]
            location = row[3]
            img_1 = row[4]
            img_2 = row[5]
            img_3 = row[6]
            img_4 = row[7]
            name = row[8]
            #Creando directorio por Animal
            
            directory_name = row[0]+'_'+'animal'
            
            s3.put_object(Bucket=bucket_name, Key=(directory_name+'/'))
           
            print(' Animal ID : ' , animal_id , ' Health Status : ' ,  health_status  , ' AGE : ' , age , ' Location : ' , location , " Link Photo : " , img_1)
           
           
            add_to_db = dynamodb.put_item(
                TableName = 'husky-app-adoption-DB2' ,
                Item = {
                    'pk' : {'S': str(animal_id)},
                    'estado_de_salud' : {'S': str(health_status)},
                    'edad' : {'N': str(age)},
                    'ubicacion' : {'S': str(location)},
                    'IMG_1' : {'S' : str(img_1)},
                    'IMG_2' : {'S' : str(img_2)},
                    'IMG_3' : {'S' : str(img_3)},
                    'IMG_4' : {'S' : str(img_4)},
                    'nombre' : {'S': str(name)}
                    
                }
                )
            print(' Successfully added the record to the dynamoDB table ')
            

    
    except Exception as e:
        print(str(e))
        
        
    return {
        'statusCode': 200,
        'body': json.dumps('csv to DynamoDB Success')
    }
