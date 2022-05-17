import json
import unittest

from DocumentManagerProject.Constants import Constants
from DocumentManagerProject.DocumentManager import DocumentManager
from DocumentManagerProject.Testing.FakeLogger import FakeLogger
from DocumentManagerProject.Testing.FakeOpenSearchClient import FakeOpenSearchClient
from DocumentManagerProject.Testing.FakeS3Client import FakeS3Client

class TestDocumentManager(unittest.TestCase):

    def setUp(self):
        # define variables used in the standard tests
        self.documentName = "testDocument"
        self.organization = "test-organization"
        self.workspace = "test-workspace"
        self.docType = "txt"
        self.s3Key = "testS3Path"
        self.s3Bucket = "www.s3Test.com"

        # make a happy path S3 client and add a reference to test file
        self.s3Client = FakeS3Client()

        # make happy path opensearch client and logger
        self.openSearchClient = FakeOpenSearchClient(None)
        self.cloudWatchClient = FakeLogger()

        # put the index for the happy path org/workspace in opensearch (index names cannot include special chars other than - and _
        self.openSearchClient.indices.create(self.organization + "_" + self.workspace)

        # use the above resources to construct a document manager
        self.documentManager = DocumentManager(self.openSearchClient, self.s3Client, self.cloudWatchClient)

    # test set for put method
    def test_put_happyPath_TXTSinglePage(self):

        # add the document to return on get_object calls to the standard bucket and key combination
        self.s3Client.documents[self.s3Bucket + "/" + self.s3Key] = "../Resources/simple-contract.txt"

        # call the method with no changes to the happy state of the system
        result = self.documentManager.put(self.organization, self.workspace, self.documentName, self.docType,
                                         self.s3Key, self.s3Bucket)

        documentFile = open("../Resources/ExpectedResults/simple-contract-result.json", "rb", buffering=0)
        expectedOpenSearchDocs = json.load(documentFile)

        fileInIndex = False
        for expectedDocument in expectedOpenSearchDocs:
            for doc in self.openSearchClient.documents[self.organization + "_" + self.workspace]:
                if doc == expectedDocument:
                    fileInIndex = True
            self.assertTrue(fileInIndex, "The document should be present in the index assigned to "
                                         "this organization and workspace. Expected document {} was not found".format(
                expectedDocument))

        # method should log success message about putting document in OpenSearch
        self.assertTrue(Constants.SUCCESS_UPLOAD_TO_OPENSEARCH.format(self.documentName, self.s3Bucket,
                                                                      self.organization + "_" + self.workspace) in self.cloudWatchClient.logs,
                        "The method should have logged a success message about uploading the file to OpenSearch")

        # method should return true
        self.assertEqual(result, True, "The method to put documents in an index should return true when successful")

    def test_put_happyPath_TXTMultiplePage(self):

        # add the document to return on get_object calls to the standard bucket and key combination
        self.s3Client.documents[self.s3Bucket + "/" + self.s3Key] = "../Resources/2-page-txt.txt"

        # set up expected documents
        documentFile = open("../Resources/ExpectedResults/2-page-txt-result.json", "rb", buffering=0)
        expectedOpenSearchDocs = json.load(documentFile)

        # call the method
        result = self.documentManager.put(self.organization, self.workspace, self.documentName, self.docType,
                                         self.s3Key, self.s3Bucket)

        # document should be in the expected location in openSearch
        fileInIndex = False
        for expectedDocument in expectedOpenSearchDocs:
            for doc in self.openSearchClient.documents[self.organization + "_" + self.workspace]:
                if doc == expectedDocument:
                    fileInIndex = True
            self.assertTrue(fileInIndex, "The document should be present in the index assigned to "
                                         "this organization and workspace. Expected document {} was not found".format(
                expectedDocument))

        # method should log success message about putting document in OpenSearch
        self.assertTrue(Constants.SUCCESS_UPLOAD_TO_OPENSEARCH.format(self.documentName, self.s3Bucket,
                                                                      self.organization + "_" + self.workspace) in self.cloudWatchClient.logs,
                        "The method should have logged a success message about uploading the file to OpenSearch")

        # method should return true
        self.assertEqual(result, True, "The method to put documents in an index should return true when successful")

    def test_put_happyPathPDF(self):

        self.docType = "pdf"

        # add the document to return on get_object calls to the standard bucket and key combination
        self.s3Client.documents[self.s3Bucket + "/" + self.s3Key] = "../Resources/part of AREMA Section 14.pdf"

        # set up expected documents
        documentFile = open("../Resources/ExpectedResults/part of AREMA Section 14-result.json", "rb", buffering=0)
        expectedOpenSearchDocs = json.load(documentFile)

        # call the method
        result = self.documentManager.put(self.organization, self.workspace, self.documentName, self.docType,
                                         self.s3Key, self.s3Bucket)

        # document should be in the expected location in openSearch
        fileInIndex = False
        for expectedDocument in expectedOpenSearchDocs:
            for doc in self.openSearchClient.documents[self.organization + "_" + self.workspace]:
                if doc == expectedDocument:
                    fileInIndex = True
            self.assertTrue(fileInIndex, "The document should be present in the index assigned to "
                                         "this organization and workspace. Expected document {} was not found".format(
                expectedDocument))

        # method should log success message about putting document in OpenSearch
        self.assertTrue(Constants.SUCCESS_UPLOAD_TO_OPENSEARCH.format(self.documentName, self.s3Bucket,
                                                                      self.organization + "_" + self.workspace) in self.cloudWatchClient.logs,
                        "The method should have logged a success message about uploading the file to OpenSearch")

        # method should return true
        self.assertEqual(result, True, "The method to put documents in an index should return true when successful")

    def test_put_DocNotInS3(self):
        # redefine variables used to create failure
        self.s3Key = "NotPresent"

        # call the method using the S3 Key that doesn't exist in the bucket
        result = self.documentManager.put(self.organization, self.workspace, self.documentName, self.docType,
                                         self.s3Key, self.s3Bucket)

        # the method should log a failure message when document isn't found in S3
        self.assertTrue(
            Constants.FAILURE_FIND_S3_FILE.format(self.s3Key, self.s3Bucket, "An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist.") in self.cloudWatchClient.logs,
            "The method should log a failure message when it can't find a file in S3")

        # method should return false on failure
        self.assertEqual(result, False,
                         "The method to put documents in an index should return false when the document wasn't found in S3")

    def test_put_DocTypeNotSupported(self):
        # redefine vars that need to change for this test
        self.docType = "notSupported"

        # call the method using the unsupported document type indicator
        result = self.documentManager.put(self.organization, self.workspace, self.documentName, self.docType,
                                         self.s3Key, self.s3Bucket)

        # the method should log a failure message when document isn't in a correct format
        self.assertTrue(Constants.FAILURE_UNSUPPORTED_FILE_TYPE.format(self.s3Key, self.s3Bucket,
                                                                       self.docType) in self.cloudWatchClient.logs,
                        "The method should log a failure message when it is given a file type that it can't support")

        # method should return false on failure
        self.assertEqual(result, False,
                         "The method to put documents in an index should return false when the document is an unsupported file type")

    def test_put_IndexNotInOpenSearch(self):
        # redefine variables for this test
        self.organization = "badOrganization"

        # call the method using an organization that will translate to an index that doesn't exist in opensearchf
        result = self.documentManager.put(self.organization, self.workspace, self.documentName, self.docType,
                                         self.s3Key, self.s3Bucket)

        # the method should log a failure message when the index isn't in opensearch
        # (indicates that the workspace wasn't created)
        self.assertTrue(Constants.FAILURE_INDEX_NOT_FOUND.format(
            self.organization + "_" + self.workspace) in self.cloudWatchClient.logs,
                        "The method should log a failure message when it can't find the given index in opensearch")

        # method should return false on failure
        self.assertEqual(result, False,
                         "The method to put documents in an index should return false when it can't find the given index in opensearch")

    def test_put_FailsPutToOpenSearch(self):

        # add the document to return on get_object calls to the standard bucket and key combination
        self.s3Client.documents[self.s3Bucket + "/" + self.s3Key] = "../Resources/simple-contract.txt"

        # construct an opensearch client that will raise an error when trying to index a document
        self.openSearchClient = FakeOpenSearchClient("INDEX_ERROR")

        # put the index for the org/workspace in the new opensearch client (index names cannot include special chars other than - and _
        self.openSearchClient.indices.create(self.organization + "_" + self.workspace)

        # construct the document manager using this new opensearch client
        self.documentManager = DocumentManager(self.openSearchClient, self.s3Client, self.cloudWatchClient)

        result = self.documentManager.put(self.organization, self.workspace, self.documentName, self.docType,
                                         self.s3Key, self.s3Bucket)

        # the method should log a failure message when the index isn't in opensearch
        # (indicates that the workspace wasn't created)
        self.assertTrue(
            Constants.FAILURE_INDEX_FILE.format(self.s3Key, self.s3Bucket, self.organization + "_" + self.workspace,
                                                "Error putting document into OpenSearch") in self.cloudWatchClient.logs,
            "The method should log a failure message when it can't upload the document to the opensearch index")

        # method should return false on failure
        self.assertEqual(result, False,
                         "The method to put documents in an index should return false when it can't upload the document to the opensearch index")

    # test set for delete method
    def test_delete_happyPath(self):

        # add the document to return on get_object calls to the standard bucket and key combination
        self.s3Client.documents[self.s3Bucket + "/" + self.s3Key] = "../Resources/simple-contract.txt"

        # add the file to the opensearch index directly (for testing purposes only)
        self.openSearchClient.documents[self.organization + "_" + self.workspace] = [self.documentName]

        # call method to delete this document from the opensearch index
        result = self.documentManager.delete(self.organization, self.workspace, self.documentName, self.s3Key, self.s3Bucket)

        # opensearch domain does not contain the document
        self.assertFalse(self.openSearchClient.exists(self.organization + "_" + self.workspace, self.documentName),
                         "The document should not be in the opensearch index after deletion")

        # s3 bucket does not contain the document
        self.assertFalse(self.s3Client.exists(self.s3Bucket, self.s3Key),
                         "The document should NOT be in S3 after deletion with the document manager")

        # a success should be logged
        self.assertTrue(Constants.SUCCESS_DELETING_FILE.format(self.s3Key, self.s3Bucket, self.documentName, self.organization + "_" + self.workspace) in self.cloudWatchClient.logs, "A success should be logged after deletion")

        # method should return true
        self.assertTrue(result, "The method should return true on successful execution")

    def test_delete_FileNotInIndex(self):

        self.openSearchClient.errorState = "SEARCH_ERROR"
        # call method to delete this document from the opensearch index
        result = self.documentManager.delete(self.organization, self.workspace, self.documentName, self.s3Key,
                                             self.s3Bucket)

        # a failure should be logged
        self.assertTrue(Constants.FAILURE_DELETING_FILE_NOT_IN_OPENSEARCH.format(self.documentName,
                                                                                 self.organization + "_" + self.workspace,
                                                                                 "0 documents found") in self.cloudWatchClient.logs,
                        "A failure should be logged when the file isn't found in the opensearch index")

        # method should return false
        self.assertFalse(result, "The method should return false on unsuccessful execution")

    def test_delete_FileNotInS3(self):
        # redefine variable used to find S3 file
        self.s3Key = "NotPresent"

        # add the file to the opensearch index directly (for testing purposes only)
        self.openSearchClient.documents[self.organization + "_" + self.workspace] = [self.documentName]

        # call method to delete this document from the opensearch index
        result = self.documentManager.delete(self.organization, self.workspace, self.documentName, self.s3Key,
                                             self.s3Bucket)

        # opensearch domain does not contain the document because it is removed before the S3 document
        self.assertFalse(self.openSearchClient.exists(self.organization + "_" + self.workspace, 1),
                         "The document should not be in the opensearch index after deletion")

        # a failure should be logged
        self.assertTrue(Constants.FAILURE_DELETING_FILE_NOT_IN_S3.format(self.s3Key, self.s3Bucket) in self.cloudWatchClient.logs,
                        "A failure should be logged when the file isn't found in the s3 bucket")

        # method should return false
        self.assertFalse(result, "The method should return false on unsuccessful execution")


    # test set for createWorkspace method
    def test_createWorkspace_happyPath(self):
        self.workspace = "workspace2"

        # call the method
        result = self.documentManager.createWorkspace(self.organization, self.workspace)

        # opensearch should contain the new domain
        self.assertTrue(self.openSearchClient.indices.exists(self.organization + "_" + self.workspace),
                        "The new index should exist in OpenSearch for this workspace")

        # a success should be logged
        self.assertTrue(Constants.SUCCESS_CREATING_WORKSPACE.format(self.organization + "_" + self.workspace) in self.cloudWatchClient.logs,
                        "A success should be logged after creating a new workspace's index")

        # method should return true
        self.assertTrue(result, "The method should return true on successful execution")

    def test_createWorkspace_alreadyExists(self):

        # call the method
        result = self.documentManager.createWorkspace(self.organization, self.workspace)

        # a failure should be logged
        self.assertTrue(Constants.FAILURE_CREATING_WORKSPACE_ALREADY_EXISTS.format(
            self.organization + "_" + self.workspace) in self.cloudWatchClient.logs,
                        "A failure should be logged when trying to create a duplicate workspace index")

        # method should return false
        self.assertFalse(result, "The method should return false on unsuccessful execution")

    def test_createWorkspace_failsToCreate(self):

        # redefine var to include an invalid character for OpenSearch indices
        self.workspace = "?"

        # call the method
        result = self.documentManager.createWorkspace(self.organization, self.workspace)

        # a failure should be logged
        self.assertTrue(Constants.FAILURE_CREATING_WORKSPACE.format(
            self.organization + "_" + self.workspace, "invalid_index_name_exception") in self.cloudWatchClient.logs,
                        "A failure should be logged when unable to create a workspace index")

        # method should return false
        self.assertFalse(result, "The method should return false on unsuccessful execution")


if __name__ == '__main__':
    unittest.main()
