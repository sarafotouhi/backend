# fake S3 Client
import os

import boto3
from botocore.response import StreamingBody


class FakeS3Client:
    getObjSuccess = {
        'ResponseMetadata': {'RequestId': '9A9BSHW7NT', 'HostId': 'rutO4omIxEiO802SNIcLjY=', 'HTTPStatusCode': 200,
                             'HTTPHeaders': {'x-amz-id-2': 'rutO4omIxEnRN55LFLsANj4CWrOwU8SpI0EXZCb9d9Wb5BcLjY=',
                                             'x-amz-request-id': '9A9B40SHW7NT',
                                             'date': 'Sat, 12 Feb 2022 16:23:34 GMT',
                                             'last-modified': 'Tue, 01 Feb 2022 14:17:54 GMT',
                                             'etag': '"f43b53dedda12c80062bfb188"',
                                             'x-amz-server-side-encryption': 'AES256',
                                             'x-amz-version-id': 'NjemVuW2c1Zklbx2Qceio', 'accept-ranges': 'bytes',
                                             'content-type': 'application/json', 'server': 'AmazonS3',
                                             'content-length': '174'}, 'RetryAttempts': 0}, 'AcceptRanges': 'bytes',
        'LastModified': "", 'ContentLength': 174, 'ETag': '"f43b53dedda12c2bfb188"',
        'VersionId': 'NjemyTbCCaq2c1Zklbx2Qceio', 'ContentType': 'application/json', 'ServerSideEncryption': 'AES256',
        'Metadata': {}, 'Body': ""}

    deleteObjSuccess =  {'ResponseMetadata': {'RequestId': 'CWMJ', 'HostId': 'mCd3M6oLAe9DE8kG/vpLCpKBY=', 'HTTPStatusCode': 204, 'HTTPHeaders': {'x-amz-id-2': 'mCd3M6fhfkO6oLAe9DE8TWpKBY=', 'x-amz-request-id': 'CWMNQ2VYCJ', 'date': 'Sat, 12 Feb 2022 18:52:26 GMT', 'x-amz-version-id': 'kT.LqVe7jFSkUldvI7h9f9i', 'x-amz-delete-marker': 'true', 'server': 'AmazonS3'}, 'RetryAttempts': 0}, 'DeleteMarker': True, 'VersionId': 'kT.LqVe7jFSkUrnvI7h9f9i'}

    def __init__(self):
        # list of documents in the bucket stored in format as on S3 (concat the folder names onto the file name)
        self.documents = {}
        return

    def get_object(self, Bucket, Key):
        if Bucket + "/" + Key not in self.documents.keys():
            raise Exception(
                "An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist.")

        # create a stream from the document stored in the document list (should be path to an actual document)
        document = open(self.documents[Bucket + "/" + Key], "rb", buffering=0)

        # Requires a StreamingBody object created from a raw stream and the content length of the stream
        self.getObjSuccess['Body'] = StreamingBody(document, os.path.getsize(self.documents[Bucket + "/" + Key]))
        return self.getObjSuccess

    def list_objects(self, Bucket, Key):
        return self.documents[Bucket + "/" + Key]

    def delete_object(self, Bucket, Key):
        self.documents.pop(Bucket + "/" + Key)
        return self.deleteObjSuccess

    # METHOD FOR TESTING ONLY
    def exists(self, Bucket, Key):
        if Bucket + "/" + Key in self.documents.keys():
            return True
        return False
