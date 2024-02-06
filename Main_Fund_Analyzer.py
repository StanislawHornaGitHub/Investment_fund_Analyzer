import argparse
from Dependencies.Class_Fund import Fund
from Dependencies.Function_config import *
from Dependencies.Function_CSV import *
from Dependencies.Function_DownloadFundQuotation import downloadFundQuotation

from dateutil.parser import parse

import matplotlib.pyplot as plt
import matplotlib.dates as mdates



startDate = "2020-01-01"
endDate = "2024-02-05"

instance = Fund(
    URL = "https://www.analizy.pl/fundusze-inwestycyjne-otwarte/UNI32/generali-oszczednosciowy",
    StartDate = parse(startDate),
    EndDate = parse(endDate),
)

# test = Fund()

instance.calculateDayToDayChange()
instance.calculateWeekToWeekChange()
instance.calculateMonthToMonthChange()
print(len(instance.Quotation))
dates = [parse(dates["date"]) for dates in instance.Quotation]
y = [change["value"] for change in instance.Quotation]

zero = []

for i in range(0, len(y)):
    zero.append(0)


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=90))
plt.xticks(rotation=45)
plt.plot(dates, y)
plt.gcf().autofmt_xdate()
print(instance)
plt.show()
