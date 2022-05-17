# fake Open Search Client
import opensearchpy


class FakeOpenSearchClient:
    indexSuccess = {'_index': '', '_type': '_doc', '_id': 'Dpqg734BZHZsFDvqRA9d', '_version': 1, 'result': 'created',
                    '_shards': {'total': 2, 'successful': 1, 'failed': 0}, '_seq_no': 0, '_primary_term': 1}

    deleteSuccess = {'_index': '', '_type': '_doc', '_id': 'true', '_version': 2, 'result': 'deleted',
                     '_shards': {'total': 2, 'successful': 1, 'failed': 0}, '_seq_no': 2, '_primary_term': 1}
    searchSuccess = {'took': 177, 'timed_out': False,
                     '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0},
                     'hits': {'total': {'value': 1, 'relation': 'eq'}, 'max_score': 0.2876821, 'hits': [
                         {'_index': 'test-organization_test-workspace', '_type': '_doc', '_id': '1',
                          '_score': 0.2876821,
                          '_source': {'title': 'Simple Test Contract',
                                      'contents': 'This is a sample test contract for a simple index configuration. '
                                                  'There are only title and contents in this document.'}}]}}
    searchFailure = {'took': 9, 'timed_out': False, '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0}, 'hits': {'total': {'value': 0, 'relation': 'eq'}, 'max_score': None, 'hits': []}}


    def __init__(self, errorState):
        # indexes that exist and their metadata
        self.indices = self.Index()
        # dict of documents in the indices, (index, [body1, body2, body3...])
        self.documents = {}
        self.errorState = errorState
        return

    # create a new document in the index given
    def index(self, index, body):
        if self.errorState == "INDEX_ERROR":
            raise Exception("Error putting document into OpenSearch")

        if (index not in self.documents.keys()):
            self.documents[index] = [body]
        else:
            self.documents[index].append(body)
        self.indexSuccess['_index'] = index
        return self.indexSuccess

    # delete a document from the index given
    def delete(self, index, id):
        try:
            self.documents[index][int(id)  - 1] = "Deleted"
            self.deleteSuccess['_index'] = index
            return self.deleteSuccess
        except Exception as e:
            raise Exception(404, '{"_index":"test-organization_test-workspace","_type":"_doc","_id":"test-document","_version":1,"result":"not_found","_shards":{"total":2,"successful":1,"failed":0},"_seq_no":1,"_primary_term":1}')

    # search for information about a document in an index
    def search(self, body, index):
        if self.errorState == 'SEARCH_ERROR':
            return self.searchFailure
        docsInIndex = self.documents[index]
        id = None
        for i in range (0, len(docsInIndex)):
            if docsInIndex[i] == body['query']['multi_match']['query']:
                id = i
        if id != None:
            self.searchSuccess['hits']['hits'][0]['_id'] = i
            return self.searchSuccess
        else:
            return self.searchFailure


    # perform bulk operations. For our test cases so far, it assumes that we are performing a bulk indexing
    def bulk(self, instructions):
        i = 0
        while i  < len(instructions):
            if "delete" in instructions[i].keys():
                self.delete(instructions[i]['delete']['_index'], instructions[i]['delete']['_id'])
                i += 1
            # if it's an even index, it'll have the operation information in one row and the index information in the next
            elif "index" in instructions[i].keys():
                self.index(instructions[i]['index']['_index'], instructions[i + 1])
                i += 2


    # TEST HELPER ONLY CHECKS FOR EXISTANCE OF DOCUMENT IN INDEX
    def exists(self, index, id):
        if id in self.documents[index]:
            if self.documents[index][id] != "Deleted":
                return True
        return False

    # a directory of indices and their metadata, accessed through OpenSearch object's .indices
    # (appears to be a direct variable access situation?)
    class Index:

        indexCreateSuccess = {'acknowledged': True, 'shards_acknowledged': True, 'index': ''}
        indexDeletedSuccess = {'acknowledged': True}

        def __init__(self):
            self.indices = {}

        # create a new index in the cluster
        def create(self, index_name, body=None):
            # implemented logic for naming restrictions to assist in testing but restriction is correct for openSearch indices
            if '?' in index_name:
                raise Exception("invalid_index_name_exception")
            self.indices[index_name] = body
            self.indexCreateSuccess['index'] = index_name
            return self.indexCreateSuccess

        # delete an index from the cluster
        # unsure of return value expectations
        def delete(self, index):
            self.indices.pop(index)
            return self.indexDeletedSuccess

        # check for existence of an index
        def exists(self, index):
            if index in self.indices.keys():
                return True
            return False

### Sample code from https://github.com/opensearch-project/opensearch-py/blob/main/README.md


# from opensearchpy import OpenSearch
#
# host = 'localhost'
# port = 9200
# auth = ('admin', 'admin') # For testing only. Don't store credentials in code.
# ca_certs_path = '/full/path/to/root-ca.pem' # Provide a CA bundle if you use intermediate CAs with your root CA.
#
# # Optional client certificates if you don't want to use HTTP basic authentication.
# # client_cert_path = '/full/path/to/client.pem'
# # client_key_path = '/full/path/to/client-key.pem'
#
# # Create the client with SSL/TLS enabled, but hostname verification disabled.
# client = OpenSearch(
#     hosts = [{'host': host, 'port': port}],
#     http_compress = True, # enables gzip compression for request bodies
#     http_auth = auth,
#     # client_cert = client_cert_path,
#     # client_key = client_key_path,
#     use_ssl = True,
#     verify_certs = True,
#     ssl_assert_hostname = False,
#     ssl_show_warn = False,
#     ca_certs = ca_certs_path
# )
#
# # Create an index with non-default settings.
# index_name = 'python-test-index3'
# index_body = {
#   'settings': {
#     'index': {
#       'number_of_shards': 4
#     }
#   }
# }
#
# response = client.indices.create(index_name, body=index_body)
# print('\nCreating index:')
# print(response)
#
# # Add a document to the index.
# document = {
#   'title': 'Moneyball',
#   'director': 'Bennett Miller',
#   'year': '2011'
# }
# id = '1'
#
# response = client.index(
#     index = index_name,
#     body = document,
#     id = id,
#     refresh = True
# )
#
# print('\nAdding document:')
# print(response)
#
# # Search for the document.
# q = 'miller'
# query = {
#   'size': 5,
#   'query': {
#     'multi_match': {
#       'query': q,
#       'fields': ['title^2', 'director']
#     }
#   }
# }
#
# response = client.search(
#     body = query,
#     index = index_name
# )
# print('\nSearch results:')
# print(response)
#
# # Delete the document.
# response = client.delete(
#     index = index_name,
#     id = id
# )
#
# print('\nDeleting document:')
# print(response)
#
# # Delete the index.
# response = client.indices.delete(
#     index = index_name
# )
#
# print('\nDeleting index:')
# print(response)
