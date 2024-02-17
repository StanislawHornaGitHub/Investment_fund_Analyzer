"""
.DESCRIPTION
    Class to represent all information related to the particular fund results.
    It calculates price changes in specified periods (default is 1 day) and prepares data,
    to be passed to the class Analyzer. 
    
    To init the instance of the class you need to provide:
        - URL <- url to fund's site on www.Analizy.pl to download the quotation from
        - TimePeriodInMonths <- int number how many quotation months are needed.
    
.NOTES

    Version:            1.0
    Author:             Stanisław Horna
    Mail:               stanislawhorna@outlook.com
    GitHub Repository:  https://github.com/StanislawHornaGitHub/Investment_fund_Analyzer
    Creation Date:      06-Feb-2024
    ChangeLog:

    Date            Who                     What

"""
from dataclasses import dataclass, field

import pendulum
from dateutil.parser import parse
from Dependencies.Function_DownloadFundQuotation import (
    downloadFundQuotation,
    getFundNameFromURL,
)

global analizyPLwebsiteURL
global analizyplAPIresponse_QuotationDate
global analizyplAPIresponse_QuotationValue

analizyPLwebsiteURL = "https://www.analizy.pl/"
analizyplAPIresponse_QuotationDate = "date"
analizyplAPIresponse_QuotationValue = "value"


@dataclass(kw_only=True)
class Fund:
    URL: str
    TimePeriodInMonths: int
    Name: str = field(init=False)
    ID: str = field(init=False)
    Currency: str = field(init=False)
    Quotation: list = field(init=False, repr=False)
    LastYearQuotation: list = field(init=False, repr=False)
    RefundRate: list[dict[str, str | float]] = field(
        init=False, default_factory=list)
    
    LastYearRefundRate: list[dict[str, str | float]] = field(
        init=False, default_factory=list)

    def __post_init__(self):
        downloadedQuotation = downloadFundQuotation(
            self.URL, self.TimePeriodInMonths
        )

        self.ID = downloadedQuotation["FundID"]
        self.Currency = downloadedQuotation["Currency"]
        self.Quotation = downloadedQuotation["Price"]["Current"]
        self.LastYearQuotation = downloadedQuotation["Price"]["History"]
        self.Name = getFundNameFromURL(self.URL)

        self.calculateRefundRate(self.Quotation, self.RefundRate)
        self.calculateRefundRate(self.LastYearQuotation, self.LastYearRefundRate)
        self.calculateDayToDayChange()

    def getID(self) -> str:
        return self.ID

    def getCurrency(self) -> str:
        return self.Currency

    def getName(self) -> str:
        return self.Name

    def getQuotation(self, rowID: int = -1) -> float:
        return float(self.Quotation[rowID][analizyplAPIresponse_QuotationValue])

    def calculateDayToDayChange(self):
        self.calculateValueChange(1, self.Quotation, "Day_to_day_%")
        self.calculateValueChange(1, self.LastYearQuotation, "Day_to_day_%")

    def calculateWeekToWeekChange(self):
        self.calculateValueChange(7, self.Quotation, "Week_to_week_%")
        self.calculateValueChange(7, self.LastYearQuotation, "Week_to_week_%")

    def calculateMonthToMonthChange(self):
        self.calculateValueChange(30, self.Quotation ,"Month_to_month_%")
        self.calculateValueChange(30, self.LastYearQuotation ,"Month_to_month_%")

    def calculateValueChange(self, period: int, source, ColumnName=None):

        if ColumnName == None:
            ColumnName = f"Change_{period}_Days_%"

        i = len(source) - 1
        while i >= 0:
            currentDate = parse(
                source[i][analizyplAPIresponse_QuotationDate]
            )
            j = i - 1
            while j >= 0:
                dateToCheck = parse(
                    source[j][analizyplAPIresponse_QuotationDate]
                )
                if (currentDate - dateToCheck).days >= period:
                    source[i][ColumnName] = round(
                        (
                            (
                                (
                                    float(
                                        source[i][
                                            analizyplAPIresponse_QuotationValue
                                        ]
                                    )
                                    / float(
                                        source[j][
                                            analizyplAPIresponse_QuotationValue
                                        ]
                                    )
                                )
                                - 1
                            )
                            * 100
                        ),
                        3,
                    )
                    break
                j -= 1
            else:
                source[i][ColumnName] = 0.0
            i -= 1

        return None

    def calculateRefundRate(self, source, destination):
        initialValue = float(source[0]["value"])
        for item in source:
            destination.append(
                {
                    "date": item["date"],
                    "RefundRate_%": round(
                        (((float(item["value"]) / initialValue) - 1) * 100), 2
                    ),
                }
            )
        return None

    def getRefundRateToPlot(self) -> dict[str, pendulum.DateTime | float]:
        return {
            "Current": {
                "date": [parse(dates["date"]) for dates in self.RefundRate][:-1],
                "value": [change["RefundRate_%"] for change in self.RefundRate][:-1],
            },
            "Historical": {
                "date": [parse(dates["date"]) for dates in self.LastYearRefundRate][:-1],
                "value": [change["RefundRate_%"] for change in self.LastYearRefundRate][:-1],
            }
        }

    def getChangesToPlot(self) -> dict[str, pendulum.DateTime | float]:
        return {
            "Current": {
                "date": [parse(dates["date"]) for dates in self.Quotation][:-1],
                "value": [change["Day_to_day_%"] for change in self.Quotation][:-1],
            },
            "Historical": {
                "date": [parse(dates["date"]) for dates in self.LastYearQuotation][:-1],
                "value": [change["Day_to_day_%"] for change in self.LastYearQuotation][:-1],
            }
        }
