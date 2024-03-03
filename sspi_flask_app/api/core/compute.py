import json
import bs4 as bs
from bs4 import BeautifulSoup
from flask import Blueprint, redirect, url_for, jsonify
from flask_login import login_required
from ..resources.utilities import parse_json, goalpost, jsonify_df, zip_intermediates, format_m49_as_string, filter_incomplete_data, score_single_indicator
from ... import sspi_clean_api_data, sspi_raw_api_data, sspi_analysis
from ..datasource.sdg import flatten_nested_dictionary_biodiv, extract_sdg_pivot_data_to_nested_dictionary, flatten_nested_dictionary_redlst, flatten_nested_dictionary_intrnt, flatten_nested_dictionary_watman
from ..datasource.worldbank import cleanedWorldBankData, cleaned_wb_intrnt
from ..datasource.oecdstat import organizeOECDdata, OECD_country_list, extractAllSeries, filterSeriesList, filterSeriesListSeniors
import pandas as pd
from pycountry import countries

compute_bp = Blueprint("compute_bp", __name__,
                       template_folder="templates", 
                       static_folder="static", 
                       url_prefix="/compute")

@compute_bp.route("/BIODIV", methods=['GET'])
@login_required
def compute_biodiv():
    """
    If indicator is not in database, return a page with a button to collect the data
    - If no collection route is implemented, return a page with a message
    - If collection route is implemented, return a page with a button to collect the data
    If indicator is in database, compute the indicator from the raw data
    - Indicator computation: average of the three scores for percentage of biodiversity in
    marine, freshwater, and terrestrial ecosystems
    """
    if not sspi_raw_api_data.raw_data_available("BIODIV"):
        return redirect(url_for("api_bp.collect_bp.BIODIV"))
    raw_data = sspi_raw_api_data.fetch_raw_data("BIODIV")
    intermediate_obs_dict = extract_sdg_pivot_data_to_nested_dictionary(raw_data)
    # implement a computation function as an argument which can be adapted to different contexts
    final_data_list = flatten_nested_dictionary_biodiv(intermediate_obs_dict)
    # store the cleaned data in the database
    zipped_document_list = zip_intermediates(final_data_list, "BIODIV",
                           ScoreFunction= lambda MARINE, TERRST, FRSHWT: 0.33 * MARINE + 0.33 * TERRST + 0.33 * FRSHWT,
                           ScoreBy= "Score")
    clean_document_list = filter_incomplete_data(zipped_document_list)
    # sspi_clean_api_data.insert_many(clean_document_list)
    return parse_json(clean_document_list)

@compute_bp.route("/REDLST", methods = ['GET'])
@login_required
def compute_rdlst():
    if not sspi_raw_api_data.raw_data_available("REDLST"):
        return redirect(url_for("api_bp.collect_bp.REDLST"))
    raw_data = sspi_raw_api_data.fetch_raw_data("REDLST")
    intermediate_obs_dict = extract_sdg_pivot_data_to_nested_dictionary(raw_data)
    final_list = flatten_nested_dictionary_redlst(intermediate_obs_dict)
    meta_data_added = score_single_indicator(final_list, "REDLST")
    
    # zip_intermediates(final_list, "REDLST",
    #                        ScoreFunction= lambda REDLST: REDLST,
    #                        ScoreBy= "Values")
    # clean_document_list = filter_incomplete_data(final_list)
    # sspi_clean_api_data.insert_many(clean_document_list)
    return meta_data_added

@compute_bp.route("/WATMAN", methods=['GET'])
@login_required
def compute_watman():
    """
    metadata_map = {
        "ER_H2O_WUEYST": "CWUEFF",
        "ER_H2O_STRESS": "WTSTRS"
    }
    """
    if not sspi_raw_api_data.raw_data_available("WATMAN"):
        return redirect(url_for("collect_bp.WATMAN"))
    raw_data = sspi_raw_api_data.fetch_raw_data("WATMAN")
    total_list = [obs for obs in raw_data if obs["Raw"]["activity"] == "TOTAL"]
    intermediate_list = extract_sdg_pivot_data_to_nested_dictionary(total_list)
    final_list = flatten_nested_dictionary_watman(intermediate_list)
    zipped_document_list = zip_intermediates(final_list, "WATMAN",
                           ScoreFunction= lambda CWUEFF, WTSTRS: 0.50 * CWUEFF + 0.50 * WTSTRS,
                           ScoreBy= "Score")
    clean_document_list = filter_incomplete_data(zipped_document_list)
    sspi_clean_api_data.insert_many(clean_document_list)
    return parse_json(clean_document_list)

@compute_bp.route("/COALPW")
@login_required
def compute_coalpw():
    if not sspi_raw_api_data.raw_data_available("COALPW"):
        return redirect(url_for("api_bp.collect_bp.COALPW"))
    raw_data = sspi_raw_api_data.fetch_raw_data("COALPW")
    observations = [entry["observation"] for entry in raw_data]
    observations = [entry["observation"] for entry in raw_data]
    df = pd.DataFrame(observations)
    return parse_json(df.head().to_json())

@compute_bp.route("/ALTNRG", methods=['GET'])
@login_required
def compute_altnrg():
    if not sspi_raw_api_data.raw_data_available("ALTNRG"):
        return redirect(url_for("collect_bp.ALTNRG"))
    raw_data = sspi_raw_api_data.fetch_raw_data("ALTNRG")
    observations = [entry["observation"] for entry in raw_data]
    df = pd.DataFrame(observations)
    print(df.head())
    df = df.pivot(columns="product", values="value", index=["year", "country", "short", "flow", "units"])
    print(df)
    return parse_json(df.head().to_json())
    # for row in raw_data:
        #lst.append(row["observation"])
    #return parse_json(lst)

@compute_bp.route("/GTRANS", methods = ['GET'])
@login_required
def compute_gtrans():
    if not sspi_raw_api_data.raw_data_available("GTRANS"):
        return redirect(url_for("collect_bp.GTRANS"))
    
    #######    WORLDBANK compute    #########
    worldbank_raw = sspi_raw_api_data.fetch_raw_data("GTRANS", IntermediateCode="TCO2EQ", Source="WorldBank")
    worldbank_clean_list = cleanedWorldBankData(worldbank_raw, "GTRANS")

    #######  IEA compute ######
    iea_raw_data = sspi_raw_api_data.fetch_raw_data("GTRANS", IntermediateCode="TCO2EQ", Source="IEA")
    iea_clean_list = [entry["observation"] for entry in iea_raw_data]
   
    ### combining in pandas ####
    wb_df = pd.DataFrame(worldbank_clean_list)
    wb_df = wb_df[wb_df["RAW"].notna()].astype(str)
    iea_df = pd.DataFrame(iea_clean_list)
    iea_df = iea_df[iea_df['seriesLabel'] == "Transport"][['year', 'value', 'country']].rename(columns={'year':'YEAR', 'value':'RAW', 'country':'CountryCode'})
    # iea_df = iea_df[iea_df["RAW"].notna()].astype(str)
    
    merged = wb_df.drop(columns=["Source", "CountryName"]).merge(iea_df, how="outer", on=["CountryCode", "YEAR"]) 
    merged['RAW'] = (merged['RAW_x'].astype(float) + merged['RAW_y'].astype(float))/2
    df = merged.dropna()[['IndicatorCode', 'CountryCode', 'YEAR', 'RAW']]
    document_list = json.loads(str(df.to_json('records')))
    count = sspi_clean_api_data.insert_many(document_list)
    return f"Inserted {count} documents into SSPI Clean Database from OECD"
    
@compute_bp.route("/SENIOR", methods=['GET'])
@login_required
def compute_senior():
    if not sspi_raw_api_data.raw_data_available("SENIOR"):
        return redirect(url_for("collect_bp.SENIOR"))
    raw_data = sspi_raw_api_data.fetch_raw_data("SENIOR")
    # metadata = raw_data[0]["Metadata"]
    # metadata_soup = bs.BeautifulSoup(metadata, "lxml")
    # to see the codes and their descriptions, uncomment and return the following line
    # jsonify([[tag.get("value"), tag.get_text()] for tag in metadata_soup.find_all("code")])
    metadata_codes = {
        "PEN20A": "Expected years in retirement, men",
        "PEN20B": "Expected years in retirement, women",
        "PEN24A": "Old age income poverty, 66+",
    }
    metadata_code_map = {
        "PEN20A": "YRSRTM",
        "PEN20B": "YRSRTW",
        "PEN24A": "POVNRT",
    }
    series = extractAllSeries(raw_data[0]["Raw"])
    document_list = []
    for code in metadata_codes.keys():
        document_list.extend(filterSeriesListSeniors(series, code, "PAG", "SENIOR"))
    long_senior_data = pd.DataFrame(document_list)
    long_senior_data.drop(long_senior_data[long_senior_data["CountryCode"].map(lambda s: len(s) != 3)].index, inplace=True)
    long_senior_data["IntermediateCode"] = long_senior_data["VariableCodeOECD"].map(lambda x: metadata_code_map[x])
    long_senior_data.astype({"Year": "int", "Value": "float"})
    zipped_document_list = zip_intermediates(
        json.loads(str(long_senior_data.to_json(orient="records")), parse_int=int, parse_float=float),
        "SENIOR",
        ScoreFunction=lambda YRSRTM, YRSRTW, POVNRT: 0.25*YRSRTM + 0.25*YRSRTW + 0.50*POVNRT,
        ScoreBy="Score"
    )
    clean_document_list = filter_incomplete_data(zipped_document_list)
    sspi_clean_api_data.insert_many(clean_document_list)
    return parse_json(clean_document_list)


@compute_bp.route("/PRISON", methods=['GET'])
@login_required
def compute_prison():
    raw_data_observation_list = parse_json(sspi_raw_api_data.find({"collection-info.IndicatorCode": "PRISON"}))
    for obs in raw_data_observation_list:
        table = BeautifulSoup(obs["observation"], 'html.parser').find("table", attrs={"id": "views-aggregator-datatable",
                                                                                               "summary": "Prison population rate"})
    print(table)
    return "string"

@compute_bp.route("/INTRNT", methods=['GET'])
# @login_required
def compute_intrnt():
    if not sspi_raw_api_data.raw_data_available("INTRNT"):
        return redirect(url_for("collect_bp.INTRNT"))
    # worldbank #
    wb_raw = sspi_raw_api_data.fetch_raw_data("INTRNT", IntermediateCode = "AVINTR")
    wb_clean = cleaned_wb_intrnt(wb_raw, "INTRNT")
    # sdg #
    sdg_raw = sspi_raw_api_data.fetch_raw_data("INTRNT", IntermediateCode = "QLMBPS")
    sdg_clean = extract_sdg_pivot_data_to_nested_dictionary(sdg_raw)
    sdg_clean = flatten_nested_dictionary_intrnt(sdg_clean)
    combined_list = wb_clean + sdg_clean
    cleaned_list = zip_intermediates(combined_list, "INTRNT",
                                     ScoreFunction= lambda AVINTR, QUINTR: 0.5 * AVINTR + 0.5 * QUINTR,
                                     ScoreBy= "Score")
    filtered_list = filter_incomplete_data(cleaned_list)
    # sspi_clean_api_data.insert_many(filtered_list)
    return parse_json(filtered_list)

