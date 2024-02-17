import argparse
from Dependencies.Class_Analyzer import Analyzer



t = Analyzer(
    URLs=[
        "https://www.analizy.pl/fundusze-inwestycyjne-otwarte/UNI32/generali-oszczednosciowy",
        "https://www.analizy.pl/fundusze-inwestycyjne-otwarte/DWS05/investor-oszczednosciowy",
        "https://www.analizy.pl/fundusze-inwestycyjne-otwarte/PZU40/pzu-globalny-obligacji-korporacyjnych",
        "https://www.analizy.pl/fundusze-inwestycyjne-otwarte/PZU45/pzu-sejf",
        "https://www.analizy.pl/fundusze-inwestycyjne-otwarte/PZU79/pzu-obligacji-krotkoterminowych",
        "https://www.analizy.pl/fundusze-inwestycyjne-otwarte/UNI03/generali-korona-dochodowy",
        "https://www.analizy.pl/fundusze-inwestycyjne-otwarte/ING43/goldman-sachs-japonia"
        ],
    TimePeriodInMonths=1
)
#t.showAnalysisSummary()
t.showAnalysisPyPlot()