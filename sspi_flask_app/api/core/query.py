import re
from flask import Blueprint, jsonify, request
from ...models.errors import InvalidQueryError
from ..resources.validators import validate_data_query
from ..resources.utilities import parse_json, lookup_database
from ... import sspi_metadata

query_bp = Blueprint("query_bp", __name__,
                     template_folder="templates", 
                     static_folder="static", 
                     url_prefix="/query")

@query_bp.route("/<database_string>")
def query_database(database_string):
    query_params = get_query_params(request)
    print(query_params)
    database = lookup_database(database_string)
    return jsonify(parse_json(database.find(query_params, options={"_id": 0})))

def get_query_params(request, requires_database=False):
    """
    Implements the logic of query parameters and raises an 
    InvalidQueryError for invalid queries.

    In Flask, request.args is a MultiDict object of query parameters, but
    I wanted the function to work for simple dictionaries as well so we can
    use it easily internally
    
    Sanitizes User Input and returns a MongoDB query dictionary.

    Should always be implemented inside of a try except block
    with an except that returns a 404 error with the error message.

    requires_database determines whether the query 
    """
    raw_query_input = {
        "IndicatorCode": request.args.getlist("IndicatorCode"),
        "IndicatorGroup": request.args.get("IndicatorGroup"),
        "CountryCode": request.args.getlist("CountryCode"),
        "CountryGroup": request.args.get("CountryGroup"),
        "Year": request.args.getlist("Year"),
        "YearRangeStart": request.args.get("YearRangeStart"),
        "YearRangeEnd": request.args.get("YearRangeEnd")
    }
    if requires_database:
        raw_query_input["Database"] = request.args.get("database"),
    validated_query_input = validate_data_query(raw_query_input)
    return build_mongo_query(validated_query_input)

def build_mongo_query(raw_query_input):
    """
    Given a safe and logically valid query input, build a mongo query
    """
    mongo_query = {}
    if raw_query_input["IndicatorCode"]: 
        mongo_query["IndicatorCode"] = {"$in": raw_query_input["IndicatorCode"]}
    if raw_query_input["IndicatorGroup"]:
        mongo_query["IndicatorGroup"] = {"$in": indicator_group(raw_query_input["IndicatorGroup"])}
    if raw_query_input["CountryCode"]:
        mongo_query["CountryCode"] = {"$in": raw_query_input["CountryCode"]}
    if raw_query_input["CountryGroup"]:
        mongo_query["CountryCode"] = {"$in": country_group(raw_query_input["CountryGroup"])}
    if raw_query_input["Year"]:
        mongo_query["YEAR"] = {"$in": raw_query_input["Year"]}
    return mongo_query

@query_bp.route("/metadata/country_groups", methods=["GET"])
def query_country_groups():
    return sspi_metadata.country_groups()

@query_bp.route("/metadata/indicator_codes", methods=["GET"])
def query_indicator_codes():
    return jsonify(sspi_metadata.indicator_codes())

@query_bp.route("/metadata/indicator_details")
def query_indicator_details():
    return jsonify(sspi_metadata.indicator_details())

@query_bp.route("/metadata/intermediate_details")
def query_intermediate_details():
    return jsonify(sspi_metadata.intermediate_details())
