import requests
import json
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

def downloadFundQuotation(fundURL, startDate, endDate) -> dict:
    url = f"{analizyplQuotationAPI}/{getFundCategoryShortcut(fundURL)}/{getFundIDfromURL(fundURL)}"
    
    responseContent = requests.get(url).content
    
    decodedJSON = json.loads(responseContent)
    
    filteredQuotation = filterQuotation(
        decodedJSON[analizyplAPIresponse_QuotationDetails][0][analizyplAPIresponse_QuotationList],
        startDate,
        endDate
    )
    
    return {
        "FundID": decodedJSON[analizyplAPIresponse_ID],
        "Currency": decodedJSON[analizyplAPIresponse_Currency],
        "Price": filteredQuotation
    }
    
def getFundIDfromURL(fundURL) -> str:
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

def filterQuotation(quotation, startDate, endDate) -> list:
    return [
        item for item in quotation 
        if parse(item[analizyplAPIresponse_QuotationDate]) >= startDate and
            parse(item[analizyplAPIresponse_QuotationDate]) <= endDate
        ]