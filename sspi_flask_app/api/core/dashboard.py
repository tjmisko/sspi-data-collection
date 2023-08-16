from datetime import datetime
from ..api import api_bp, parse_json, lookup_database
import json
import math
from io import BytesIO
from flask import redirect, request, url_for, current_app as app, render_template, flash, get_flashed_messages
from flask_login import current_user, fresh_login_required, login_required
from ... import sspi_main_data_v3, sspi_raw_api_data, sspi_clean_api_data, sspi_metadata
from pycountry import countries
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import pandas as pd
import re
import os

@api_bp.route("/", methods=["GET"])
@login_required
def api_home():
    return render_template("api.html")

@api_bp.route("/status/database/<database>")
@login_required
def get_database_status(database):
    ndocs = lookup_database(database).count_documents({})
    return render_template("database_status.html", database=database, ndocs=ndocs)

@api_bp.route('/api_coverage')
def api_coverage():
    """
    Return a list of all endpoints and whether they are implemented
    """
    all_indicators = indicator_codes()
    endpoints = [str(r) for r in app.url_map.iter_rules()]
    collect_implemented = [re.search(r'(?<=api/v1/collect/)(?!static)([\w]*)', r).group() for r in endpoints if re.search(r'(?<=api/v1/collect/)(?!static)[\w]*', r)]
    compute_implemented = [re.search(r'(?<=api/v1/compute/)(?!static)[\w]*', r).group() for r in endpoints if re.search(r'(?<=api/v1/compute/)(?!static)[\w]*', r)]
    coverage_data_object = []
    for indicator in all_indicators:
        coverage_data_object.append({"IndicatorCode": indicator, "collect_implemented": indicator in collect_implemented, "compute_implemented": indicator in compute_implemented})
    #{"collect_implemented": collect_implemented, "compute_implemented": compute_implemented}
    return parse_json(coverage_data_object)

@api_bp.route('/dynamic/<IndicatorCode>')
def get_dynamic_data(IndicatorCode):
    """
    Use the format argument to control whether the document is formatted for the website table
    """
    request_country_group = request.args.get("country_group", default = "sspi_67", type = str)
    country_codes = country_group(request_country_group)
    query_results = parse_json(sspi_clean_api_data.find({"IndicatorCode": IndicatorCode, "CountryCode": {"$in": country_codes}},
                                                        {"_id": 0, "Intermediates": 0, "IndicatorCode": 0}))
    print(query_results)
    long_data = pd.DataFrame(query_results).drop_duplicates()
    long_data = long_data.astype({"YEAR": int, "RAW": float})
    long_data = long_data.round(3)
    wide_dataframe = pd.pivot(long_data, index="CountryCode", columns="YEAR", values="RAW")
    nested_data = json.loads(wide_dataframe.to_json(orient="index"))
    return_data = []
    for country_code in nested_data.keys():
        country_data = nested_data[country_code]
        country_data["CountryCode"] = country_code
        country_data["CountryName"] = countries.lookup(country_code).name
        return_data.append(country_data)
    return parse_json(return_data)

@api_bp.route("/post_static_data", methods=["POST"])
@fresh_login_required
def post_static_data():
    data = json.loads(request.data)
    sspi_main_data_v3.insert_many(data)
    return redirect(url_for('datatest_bp.database'))


@api_bp.route("/metadata", methods=["GET"])
def metadata():
    # Implement request.args for filtering the metadata
    return parse_json(sspi_metadata.find())

@api_bp.route("/metadata", methods=["POST"])
def post_metadata():
    data = json.loads(request.data)
    sspi_metadata.insert_many(data)
    return redirect(url_for('datatest_bp.database'))

@api_bp.route("/metadata/indicator_codes", methods=["GET"])
def indicator_codes():
    """
    Return a list of all indicator codes in the database
    """
    query_result = parse_json(sspi_metadata.find_one({"indicator_codes": {"$exists": True}}))["indicator_codes"]
    return query_result

@api_bp.route("/metadata/country_groups", methods=["GET"])
def country_groups():
    """
    Return a list of all country groups in the database
    """
    query_result = parse_json(sspi_metadata.find_one({"country_groups": {"$exists": True}}))["country_groups"]
    return parse_json(query_result.keys())

@api_bp.route("/metadata/country_groups/<country_group>", methods=["GET"])
def country_group(country_group):
    """
    Return a list of all countries in a given country group
    """
    query_result = parse_json(sspi_metadata.find_one({"country_groups": {"$exists": True}}))["country_groups"][country_group]
    return query_result

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
    return raw_data

@api_bp.route("/local")
@login_required
def local():
    return render_template('local.html', database_names=check_for_local_data())

@api_bp.route("/local/database/list", methods=['GET'])
@login_required
def check_for_local_data():
    try:
        database_files = os.listdir(os.path.join(os.getcwd(),'local'))
    except FileNotFoundError:
        database_files = os.listdir("/var/www/sspi.world/local")
    database_names = [db_file.split(".")[0] for db_file in database_files]
    return parse_json(database_names)

@api_bp.route("/local/reload/<database_name>", methods=["POST"])
@login_required
def reload_from_local(database_name):
    if not database_name in check_for_local_data():
        return "Unable to Reload Data: Invalid database name"
    database = lookup_database(database_name)
    del_count = database.delete_many({}).deleted_count
    try: 
        filepath = os.path.join(os.getcwd(),'local', database_name + ".json")
        json_file = open(filepath)
    except FileNotFoundError:
        filepath = os.path.join("/var/www/sspi.world/local", database_name + ".json")
        json_file = open(filepath)
    local_data = json.load(json_file)
    ins_count = len(database.insert_many(local_data).inserted_ids)
    json_file.close()
    return "Reload successful: Dropped {0} observations from {1} and reloaded with {2} observations".format(del_count, database_name, ins_count)

@api_bp.route("/dashboard")
def api_internal_buttons():
    implementation_data = api_coverage()
    return render_template("api-internal-buttons.html", implementation_data=implementation_data)
