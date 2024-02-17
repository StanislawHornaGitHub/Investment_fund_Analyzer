"""
.DESCRIPTION
    Module of:
        - constant values required to correctly process quotation data
        - functions related to downloading and filtering fund's quotation
        
    downloadFundQuotation <- downloads quotations of provided url from www.Analizy.pl
    getFundIDfromURL <- extracts fund ID from provided url
    getFundNameFromURL <- extracts fund name from provided url
    getFundCategoryShortcut <- extracts fund category shortcut from provided url
    getFundCategory <- extracts fund category name from provided url
    filterQuotation <- filters quotation time frame
    
.NOTES

    Version:            1.0
    Author:             Stanisław Horna
    Mail:               stanislawhorna@outlook.com
    GitHub Repository:  https://github.com/StanislawHornaGitHub/Investment_fund_Analyzer
    Creation Date:      06-Feb-2024
    ChangeLog:

    Date            Who                     What

"""
import requests
import json
import pendulum
from dateutil.parser import parse

global analizyplQuotationAPI
global analizyplAPIresponse_ID
global analizyplAPIresponse_Currency
global analizyplAPIresponse_QuotationDetails
global analizyplAPIresponse_QuotationList
global analizyplAPIresponse_QuotationDate
global analizyplAPIresponse_QuotationValue


global fundIDpositionInURL
global fundNamePositionInURL
global fundCategoryPositionInURL

analizyplQuotationAPI = "https://www.analizy.pl/api/quotation"
analizyplAPIresponse_ID = "id"
analizyplAPIresponse_Currency = "currency"
analizyplAPIresponse_QuotationDetails = "series"
analizyplAPIresponse_QuotationList = "price"
analizyplAPIresponse_QuotationDate = "date"
analizyplAPIresponse_QuotationValue = "value"

fundIDpositionInURL = 4
fundNamePositionInURL = 5
fundCategoryPositionInURL = 3


def downloadFundQuotation(fundURL: str, TimePeriodInMonths: int) -> dict:

    url = f"{analizyplQuotationAPI}/{getFundCategoryShortcut(fundURL)}/{getFundIDfromURL(fundURL)}"

    responseContent = requests.get(url).content

    decodedJSON = json.loads(responseContent)

    filteredQuotation = filterQuotation(
        decodedJSON[analizyplAPIresponse_QuotationDetails][0][analizyplAPIresponse_QuotationList],
        TimePeriodInMonths
    )

    return {
        "FundID": decodedJSON[analizyplAPIresponse_ID],
        "Currency": decodedJSON[analizyplAPIresponse_Currency],
        "Price": filteredQuotation
    }


def getFundIDfromURL(fundURL: str) -> str:
    if not isinstance(fundURL, str):
        raise TypeError("FundURL must be a string")

    return fundURL.split("/")[fundIDpositionInURL]


def getFundNameFromURL(fundURL) -> str:
    if not isinstance(fundURL, str):
        raise TypeError("FundURL must be a string")
    return fundURL.split("/")[fundNamePositionInURL].replace("-", " ").title()


def getFundCategoryShortcut(fundURL) -> str:
    if not isinstance(fundURL, str):
        raise TypeError("FundURL must be a string")

    category = getFundCategory(fundURL)
    return "".join([word[0] for word in category.split("-")])


def getFundCategory(fundURL) -> str:
    if not isinstance(fundURL, str):
        raise TypeError("FundURL must be a string")

    return fundURL.split("/")[fundCategoryPositionInURL]


def filterQuotation(quotation, TimePeriodInMonths: int) -> list:
    startDate = pendulum.now().subtract(months=TimePeriodInMonths).date()
    currentData = [
        item for item in quotation
        if pendulum.from_format(item[analizyplAPIresponse_QuotationDate], "YYYY-MM-DD").date() >= startDate
    ]

    historicalStartDate = startDate.subtract(years=1)
    historicalEndDate = historicalStartDate.add(months=TimePeriodInMonths)

    historicalData = [
        item for item in quotation
        if pendulum.from_format(item[analizyplAPIresponse_QuotationDate], "YYYY-MM-DD").date() >= historicalStartDate and
        pendulum.from_format(
            item[analizyplAPIresponse_QuotationDate], "YYYY-MM-DD").date() <= historicalEndDate
    ]

    return {
        "Current": currentData,
        "History": historicalData
    }
