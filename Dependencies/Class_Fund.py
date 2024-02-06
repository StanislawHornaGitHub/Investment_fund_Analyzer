from dataclasses import dataclass, field

import datetime
from dateutil.parser import parse
from Dependencies.Function_DownloadFundQuotation import downloadFundQuotation, getFundNameFromURL

global analizyPLwebsiteURL
global analizyplAPIresponse_QuotationDate
global analizyplAPIresponse_QuotationValue

analizyPLwebsiteURL = "https://www.analizy.pl/"
analizyplAPIresponse_QuotationDate = "date"
analizyplAPIresponse_QuotationValue = "value"


@dataclass(kw_only=True)
class Fund:
    URL: str
    StartDate: datetime
    EndDate: datetime
    Name: str = field(init=False)
    ID: str = field(init=False)
    Currency: str = field(init=False)
    Quotation: list = field(init=False, repr=False)

    def __post_init__(self):
        quotation = downloadFundQuotation(self.URL, self.StartDate, self.EndDate)

        self.ID = quotation["FundID"]
        self.Currency = quotation["Currency"]
        self.Quotation = quotation["Price"]
        self.Name = getFundNameFromURL(self.URL)

    def calculateDayToDayChange(self):
        self.calculateValueChange(1, "Day_to_day_%")

    def calculateWeekToWeekChange(self):
        self.calculateValueChange(7, "Week_to_week_%")

    def calculateMonthToMonthChange(self):
        self.calculateValueChange(30, "Month_to_month_%")

    def calculateValueChange(self, period: int, ColumnName=None):

        if ColumnName == None:
            ColumnName = f"Change_{period}_Days_%"

        i = len(self.Quotation) - 1
        while i >= 0:
            currentDate = parse(self.Quotation[i][analizyplAPIresponse_QuotationDate])
            j = i - 1
            while j >= 0:
                dateToCheck = parse(
                    self.Quotation[j][analizyplAPIresponse_QuotationDate]
                )
                if (currentDate - dateToCheck).days >= period:
                    self.Quotation[i][ColumnName] = round(
                        (
                            (
                                (
                                    float(
                                        self.Quotation[i][
                                            analizyplAPIresponse_QuotationValue
                                        ]
                                    )
                                    / float(
                                        self.Quotation[j][
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
                self.Quotation[i][ColumnName] = 0.0
            i -= 1
