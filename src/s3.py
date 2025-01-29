import asyncio
import aioboto3
from botocore.config import Config


class _S3Connector:
    def __init__(self, bucket_name, endpoint_url, region_name, aws_access_key_id, aws_secret_access_key):
        self.bucket_name = bucket_name
        self.session = aioboto3.Session()
        self.client_args = {
            'service_name': 's3',
            'endpoint_url': endpoint_url,
            'region_name': region_name,
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
            'config': Config(s3={'addressing_style': 'path'})
        }

    async def __aenter__(self):
        self.client = await self.session.client(**self.client_args).__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def create_bucket(self):
        await self.client.create_bucket(Bucket=self.bucket_name)

    async def list_buckets(self):
        return await self.client.list_buckets()

    async def upload_file(self, filename, key):
        await self.client.upload_file(filename, self.bucket_name, key)

    async def upload_fileobj(self, filename, key):
        async with open(filename, 'rb') as data:
            await self.client.upload_fileobj(data, self.bucket_name, key)

    async def list_objects(self):
        return await self.client.list_objects(Bucket=self.bucket_name)

    async def delete_object(self, key):
        await self.client.delete_object(Bucket=self.bucket_name, Key=key)

    async def delete_bucket(self):
        await self.client.delete_bucket(Bucket=self.bucket_name)


# Использую пример от хостера TimewebCloud
# https://github.com/timeweb-cloud/s3-examples/tree/master/python3

# BUCKET = {'Name': '<bucket_name>'}  # <--- заменить
# FILENAME = 'sample.txt'

# async def main():
#     async with _S3Connector(
#         bucket_name=BUCKET['Name'],
#         endpoint_url='https://s3.timeweb.com',
#         region_name='ru-1',
#         aws_access_key_id='<account_name>',  # <--- заменить
#         aws_secret_access_key='<secret_key>'  # <--- заменить
#     ) as s3:
#         print('Создание бакета')
#         await s3.create_bucket()

#         print('\nСписок бакетов')
#         response = await s3.list_buckets()
#         for bucket in response.get('Buckets', []):
#             print(bucket['Name'])

#         print('\nЗагрузка файла в бакет')
#         await s3.upload_file(FILENAME, 'sample.txt')

#         print('\nЗагрузка объекта в бакет')
#         await s3.upload_fileobj(FILENAME, 'sample-obj.txt')

#         print('\nСписок объектов в бакете')
#         objects = await s3.list_objects()
#         for obj in objects.get('Contents', []):
#             print(obj['Key'])

#         print('\nУдаление объектов')
#         for obj in ['sample.txt', 'sample-obj.txt']:
#             await s3.delete_object(obj)
#             print(f'Объект {obj} удален')

#         print('\nУдаление бакета')
#         await s3.delete_bucket()