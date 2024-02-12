import argparse
from Dependencies.Class_Analyzer import Analyzer



t = Analyzer(
    URLs=[
        "https://www.analizy.pl/fundusze-inwestycyjne-otwarte/UNI32/generali-oszczednosciowy",
        "https://www.analizy.pl/fundusze-inwestycyjne-otwarte/DWS05/investor-oszczednosciowy",
        "https://www.analizy.pl/fundusze-inwestycyjne-otwarte/PZU40/pzu-globalny-obligacji-korporacyjnych",
        "https://www.analizy.pl/fundusze-inwestycyjne-otwarte/IPO165/pocztowy-konserwatywny",
        "https://www.analizy.pl/fundusze-inwestycyjne-otwarte/UNI10/generali-profit-plus"
        ],
    TimePeriodInMonths=3
)
#t.showAnalysisSummary()
t.showAnalysisPlot()