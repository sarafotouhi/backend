# https://docs.aws.amazon.com/opensearch-service/latest/developerguide/configuration-samples.html for using client
# https://docs.aws.amazon.com/opensearch-service/latest/developerguide/indexing.html for uploading documents
# https://docs.aws.amazon.com/opensearch-service/latest/developerguide/integrations.html#integrations-s3-lambda streaming documents from S3 using Lambda
import io
import uuid

from PyPDF2 import PdfFileReader

from DocumentManagerProject.Constants import Constants


class DocumentManager:
    def __init__(self, openSearchClient, s3Client, logger):
        self.s3Client = s3Client
        self.openSearchClient = openSearchClient
        self.cloudWatchClient = logger

    # add a document to OpenSearch
    # requires that the document already exists in S3 and the given index (organization_workspace) exists in OpenSearch
    def put(self, organization, workspace, documentName, docType, s3FilePath, s3BucketName):

        if docType.lower() != "txt" and docType.lower() != "pdf":
            self.cloudWatchClient.log(Constants.FAILURE_UNSUPPORTED_FILE_TYPE.format(s3FilePath, s3BucketName, docType))
            return False

        indexName = organization + "_" + workspace
        # check to make sure that the index exists in opensearch
        if not self.openSearchClient.indices.exists(indexName):
            self.cloudWatchClient.log(Constants.FAILURE_INDEX_NOT_FOUND.format(indexName))
            return False

        # download document from S3
        try:
            s3Document = self.s3Client.get_object(Bucket=s3BucketName, Key=s3FilePath)
        except Exception as e:
            self.cloudWatchClient.log(Constants.FAILURE_FIND_S3_FILE.format(s3FilePath, s3BucketName, e))
            return False

        bulkUpload = []

        # multipage TXT file
        if docType.lower() == "txt":
            # use client to index the document in opensearch (index name is organization + "_" + workspace and document id is its name)
            try:
                # read the body of the s3Document to give to OpenSearch
                body = s3Document['Body'].read()

                lines = body.splitlines()
                pageNum = 1
                totalBody = ""

                for i in range(0, len(lines)):
                    cleanedLine = lines[i].decode("utf-8")
                    totalBody += cleanedLine.replace('"', '\'') + "\n"

                    # average page length is 46 lines, so if we have reached that threshold or if we have reached the last line of the file, append the totality as a page
                    if i % 46 == 45 or i == len(lines) - 1:
                        openSearchDoc = {"title": documentName,
                                         "page": pageNum,
                                         "body": totalBody}
                        pageNum += 1

                        # clear the totalBody for the next page
                        totalBody = ""

                        bulkUpload.append({"index": {"_index": indexName, "_id": str(uuid.uuid4())}})
                        bulkUpload.append(openSearchDoc)

            except Exception as e:
                self.cloudWatchClient.log(
                    Constants.FAILURE_PROCESSING_FILE.format(s3FilePath, s3BucketName, indexName, e))
                s3Document["Body"].close()
                return False

        # multipage pdf file
        elif docType.lower() == 'pdf':

            try:
                # read the body of the s3Document to give to OpenSearch
                body = s3Document['Body'].read()

                # buffer the pdf doc
                documentBuffer = io.BytesIO()
                documentBuffer.write(body)

                # create a file reader for the pdf doc
                pdf = PdfFileReader(documentBuffer)

                # read pdf doc by page and add each page to the index upload array
                for page in range(pdf.getNumPages()):
                    current_page = pdf.getPage(page)
                    text = current_page.extractText()
                    cleanedText = text.replace('"', '\'')

                    openSearchDoc = {"title": documentName,
                                     "page": page + 1,
                                     "body": cleanedText}

                    bulkUpload.append({"index": {"_index": indexName, "_id": str(uuid.uuid4())}})
                    bulkUpload.append(openSearchDoc)

            except Exception as e:
                self.cloudWatchClient.log(
                    Constants.FAILURE_PROCESSING_FILE.format(s3FilePath, s3BucketName, indexName, e))
                s3Document["Body"].close()
                return False

        # try to upload the new file to the openSearch index
        try:
            self.openSearchClient.bulk(bulkUpload)
        except Exception as e:
            self.cloudWatchClient.log(Constants.FAILURE_INDEX_FILE.format(s3FilePath, s3BucketName, indexName, e))
            s3Document["Body"].close()
            return False

        # ensure that document stream is closed
        s3Document["Body"].close()

        # log success
        self.cloudWatchClient.log(Constants.SUCCESS_UPLOAD_TO_OPENSEARCH.format(documentName, s3BucketName, indexName))
        return True

    # deletes a given file from OpenSearch index as well as from the S3 bucket (reduce amount of unnecessary data stored)
    def delete(self, organization, workspace, documentName, s3FilePath, s3BucketName):
        indexName = organization + "_" + workspace

        # delete the document from OpenSearch

        # Search for the document.
        query = {
          'query': {
            'multi_match': {
              'query': documentName,
              'fields': ['title']
            }
          }
        }

        bulkDelete = []
        try:
            response = self.openSearchClient.search(
                body = query,
                index = indexName
            )

            # if the first query returns no hits, the document wasn't in the index in the first place, this is an error
            if response['hits']['total']['value'] == 0:
                self.cloudWatchClient.log(Constants.FAILURE_DELETING_FILE_NOT_IN_OPENSEARCH.format(
                    documentName, indexName, str(response['hits']['total']['value']) + " documents found"))
                return False

            # otherwise, keep requesting and deleting the pages of the document in the index until there are no more left
            # each search will return info of at most 10 pages
            while response['hits']['total']['value'] > 0:

                for element in response['hits']['hits']:
                     bulkDelete.append({"delete": {"_index": element['_index'], "_id": element['_id']}})

                try:
                    # send off this batch to be deleted
                    self.openSearchClient.bulk(bulkDelete)
                except Exception as e:
                    self.cloudWatchClient.log(Constants.FAILURE_DELETING_FILE_NOT_IN_OPENSEARCH.format(
                        documentName, indexName, e))
                    return False

                # clear the array for the next set of pages to delete
                bulkDelete = []
                response = self.openSearchClient.search(
                    body = query,
                    index = indexName
                )

        except Exception as e:
            self.cloudWatchClient.log(Constants.FAILURE_DELETING_FILE_NOT_IN_OPENSEARCH.format(
                documentName, indexName, e))
            return False

        # delete the document from S3
        try:
            self.s3Client.delete_object(Bucket=s3BucketName, Key=s3FilePath)
        except Exception as e:
            self.cloudWatchClient.log(Constants.FAILURE_DELETING_FILE_NOT_IN_S3.format(s3FilePath, s3BucketName))
            return False

        # log message about successful deletion of the document
        self.cloudWatchClient.log(Constants.SUCCESS_DELETING_FILE.format(s3FilePath, s3BucketName, documentName, indexName))
        return True

    # creates an index under the organization and workspace's name so that it can be accessed in isolation from other indexes
    def createWorkspace(self, organization, workspace):
        indexName = organization + "_" + workspace

        # check to make sure this is not a duplicate of an already existing index
        indexExists = self.openSearchClient.indices.exists(indexName)
        if indexExists:
            self.cloudWatchClient.log(Constants.FAILURE_CREATING_WORKSPACE_ALREADY_EXISTS.format(indexName))
            return False

        # use client to create a new index for the workspace
        try:
            self.openSearchClient.indices.create(indexName)
            self.cloudWatchClient.log(Constants.SUCCESS_CREATING_WORKSPACE.format(indexName))

        except Exception as e:
            self.cloudWatchClient.log(Constants.FAILURE_CREATING_WORKSPACE.format(indexName, e))
            return False

        return True
