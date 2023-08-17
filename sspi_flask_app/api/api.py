from flask import Blueprint
from flask_login import current_user
from .. import sspi_raw_api_data, sspi_clean_api_data, sspi_main_data_v3, sspi_metadata
from bson import json_util
import json
import math

api_bp = Blueprint(
    'api_bp', __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/api/v1'
)

# some common utility functions used across the api core functionality

def raw_data_available(IndicatorCode):
    """
    Check if indicator is in database
    """
    return bool(sspi_raw_api_data.find_one({"collection-info.RawDataDestination": IndicatorCode}))

def parse_json(data):
    return json.loads(json_util.dumps(data))

def print_json(data):
    print(json.dumps(data, indent=4, sort_keys=True))

def string_to_float(string):
    """
    Passes back string 'NaN' instead of float NaN
    """
    if math.isnan(float(string)):
        return "NaN"
    return float(string)

def lookup_database(database_name):
    """
    Utility function used for safe database lookup
    Returns nothing if the database name is incorrect
    """
    if database_name == "sspi_main_data_v3":
        return sspi_main_data_v3
    elif database_name == "sspi_raw_api_data":
        return sspi_raw_api_data
    elif database_name == "sspi_clean_api_data":
        return sspi_clean_api_data
    elif database_name == "sspi_metadata":
        return sspi_metadata
    
def store_raw_observation(observation, collection_time, RawDataDestination):
    """
    Utility Function the response from an API call in the database
    - Observation to be passed as a well-formed dictionary for entry into pymongo
    - RawDataDestination is the indicator code for the indicator that the observation is for
    """
    sspi_raw_api_data.insert_one(
    {"collection-info": {"CollectedBy": current_user.username,
                        "RawDataDestination": RawDataDestination,
                        "CollectedAt": collection_time}, 
    "observation": observation})

# utility functions
def format_m49_as_string(input):
    """
    Utility function ensuring that all M49 data is correctly formatted as a
    string of length 3 for use with the pycountry library
    """
    input = int(input)
    if input >= 100:
        return str(input) 
    elif input >= 10:
        return '0' + str(input)
    else: 
        return '00' + str(input)
    
def fetch_raw_data(RawDataDestination):
    """
    Utility function that handles querying the database
    """
    mongoQuery = {"collection-info.RawDataDestination": RawDataDestination}
    raw_data = parse_json(sspi_raw_api_data.find(mongoQuery))
    return raw_data@api_bp.route("/metadata/indicator_codes", methods=["GET"])

def indicator_codes():
    """
    Return a list of all indicator codes in the database
    """
    query_result = parse_json(sspi_metadata.find_one({"indicator_codes": {"$exists": True}}))["indicator_codes"]
    return query_result