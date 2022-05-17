import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from flask import Flask, request, Response
from DocumentManagerProject.DocumentManager import DocumentManager
from DocumentManagerProject.Logger import Logger
from requests_aws4auth import AWS4Auth
from flask_cors import CORS, cross_origin

# IN FUTURE, THESE CAN BE CONVERTED TO ENVIRONMENT VARIABLES ON THE INSTANCE RUNNING THE CODE
AWS_REGION = "us-east-1"
LOG_GROUP = "document-manager"
COMPONENT_NAME = "document-manager"
OPEN_SEARCH_HOST = 'search-capstone-test-domain-mp632x44bkxmrwsojcisnzxuea.us-east-1.es.amazonaws.com'

session = boto3.session.Session(region_name=AWS_REGION)

credentials = session.get_credentials()

awsauth = AWS4Auth(region=AWS_REGION, service='es',
                   refreshable_credentials=credentials)

openSearchClient = OpenSearch(hosts=[{'host': OPEN_SEARCH_HOST, 'port': 443}],
                              http_auth=awsauth,
                              use_ssl=True,
                              verify_certs=True,
                              connection_class=RequestsHttpConnection)
s3Client = session.client("s3")

logger = Logger(LOG_GROUP, COMPONENT_NAME, session, AWS_REGION)
docMan = DocumentManager(openSearchClient, s3Client, logger)

application = Flask(__name__)
CORS(application, support_credentials=True)


@application.route("/")
def root():
    return Response({"Welcome to our API! If you arent my group member get the heck out of here!!!"}, status=200)


@application.route("/document", methods=["POST", "DELETE"])
@cross_origin(supports_credentials=True)
def handleDocumentCalls():
    try:
        if request.method == "POST":
            data = json.loads(request.data)
            docType = data["documentName"].split(".")[-1]
            result = docMan.put(data["organization"], data["workspace"], data["documentName"],
                                docType, data["s3FilePath"], data["s3BucketName"])
            if result:
                return Response("{}", status=201)
            else:
                return Response("{}", status=404)

        elif request.method == "DELETE":
            data = json.loads(request.data)
            result = docMan.delete(data["organization"], data["workspace"], data["documentName"],
                                   data["s3FilePath"], data["s3BucketName"])
            if result:
                return Response("{}", status=200)
            else:
                return Response("{}", status=404)

        else:
            return Response("INVALID REQUEST TYPE", status=406)
    except Exception as e:
        return Response("{'error thrown': " + str(e) + "}", 406)

@application.route("/workspace", methods=["POST"])
@cross_origin(supports_credentials=True)
def handleWorkspaceCalls():
    try:
        if request.method == "POST":
            data = json.loads(request.data)
            result = docMan.createWorkspace(data["organization"], data["workspace"])
            if result:
                return Response("{}", 201)
            else:
                return Response("{}", 404)

        else:
            return Response("INVALID REQUEST TYPE", 406)

    except Exception as e:
        return Response("{'error thrown': " + str(e) + "}", 406)

# THIS IS STUBBING OUR MISSING SERVICES COMPONENT TO ALLOW THE FRONT END TO CONTINUE WORK
@application.route("/requirements", methods=["POST", "GET"])
@cross_origin(supports_credentials=True)
def handleRequirementsCalls():
    try:
        if request.method == "POST":
            result = {
			"targetPhraseData":
                ["Motor nameplates", "CAN/CSA C22.2 No. 100", "", "Sealing compound for use in sealing cable entrances", "AREMA Communications and Signals Manual", "Par t 15.2.15"]
}

            if result:
                return Response(json.dumps(result), 201)
            else:
                return Response("{Error occurred}", 404)
        elif request.method == "GET":
            result = {
                "Motor nameplates": {
                "nameofStandard": "CSAC22.2No.100-04",
                "req": "Motor nameplates shall conform to CAN/CSA C22.2 No . 100-04",
                "targetPosition": "",
                "score": "17.99804",
                "pageNumber": "58",
                "pageContent": "C22.2 No. 100-04© Canadian Standards Association18June 20046.2Temperature test6.2.1The temperature of machines shall meet the requirements of Table4 and Clauses6.2.4, 6.2.7, and 6.2.8 when tested as follows:(a)for motors without a marked rated output, either by loading the motor or by raising the input voltage to obtain the rated input amperes (with the motor running); or(b)for motors with a marked rated output, at the rated frequency or speed and delivering the rated output for the period of time specified on the nameplate or until constant temperatures are reached for machines having a continuous rating.6.2.26.2.2.1For the temperature test, the test voltage shall be the rated voltage except that AC motors intended for nominal ac system voltages of 120, 208, 240, 480, and 600 shall be tested at 115, 200, 230, 460, and 575V respectively.6.2.2.2DC motors in IEC frame size 80 and smaller, designed for rectifier power supply, shall be tested with anadjustable power supply that provides a rated voltage and a rated form factor at rated load (see Clause5.1(k)).6.2.3Motors marked with a service factor shall be loaded continuously at the rated voltage and frequency until the actual output is equal to the rated horsepower multiplied by the service factor.6.2.4The temperature of insulated windings shall not exceed the values specified for the particular insulation class of the machines as specified in Table4.6.2.5Except as specified in the individual clauses of this Standard, temperatures shall be measured as specified in the Notes to Table4.6.2.6Motors designed for a specific application that is covered by another standard in the C22.2 series of Standards shall be tested in accordance with the conditions of that application, including ventilation, mounting arrangements, ambient temperature, and temperature rise.6.2.7Machines having more than one electrical rating (e.g., ac and dc) shall be tested at the rating that results in the highest temperatures.6.2.86.2.8.1The temperatures on or within the terminal box and on the supply conductors shall not exceed the values in Table5, except that higher temperatures not exceeding 110 ºC shall be permitted if the machine is marked as required by Item (u) of Clause5.1.Licensed for/Autorisé à Tao Cai, Siemens Canada Limited, Sold by/vendu par CSA on/le 10/1/2009.  Single user license only.  Storage, distribution or use on network prohibited./Permis d'utilisateur simple seulement.  Le stockage, la distribution ou l'utilisation sur le réseau est interdit.",
                    "content": [
                        "shall meet the requirements of Table4 and Clauses6.2.4, 6.2.7, and 6.2.8 when tested as follows:(a)for <em>motors</em>",
                        "without a marked rated output, either by loading the <em>motor</em> or by raising the input voltage to obtain",
                        "the rated input amperes (with the <em>motor</em> running); or(b)for <em>motors</em> with a marked rated output, at the",
                        "rated frequency or speed and delivering the rated output for the period of time specified on the <em>nameplate</em>",
                        "120, 208, 240, 480, and 600 shall be tested at 115, 200, 230, 460, and 575V respectively.6.2.2.2DC <em>motors</em>"]
                }
            }

            if result:
                return Response(json.dumps(result), 201)
            else:
                return Response("{Error occurred}", 404)

        else:
            return Response("INVALID REQUEST TYPE", 406)

    except Exception as e:
        return Response("{'error thrown': " + str(e) + "}", 406)


if __name__ == '__main__':
    application.debug = True
    application.run(host="0.0.0.0")
