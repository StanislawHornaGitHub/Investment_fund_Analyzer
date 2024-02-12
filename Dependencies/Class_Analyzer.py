from dataclasses import dataclass, field

from dateutil.parser import parse
import datetime

from tabulate import tabulate

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from Dependencies.Class_Fund import Fund
from Dependencies.Function_Conversion import convertNumericToStrPlsMnsSigns


@dataclass(kw_only=True)
class Analyzer:
    URLs: list[str]
    TimePeriodInMonths: int

    WindowPlotTitle = "Fund analysis plot"
    PlotSize = {
        "X": 20,
        "Y": 10
    }
    PlotOffsetInWindow = {
        "left": 0.050,
        "right": 0.845,
        "top": 0.9,
        "bottom": 0.1
    }
    PlotOrder = {
        0: {
            "title": "Price Volatility",
            "X_axis_label": "Time",
            "Y_axis_label": "Daily price change %",
        },
        1: {
            "title": "Investment Return Rate",
            "X_axis_label": "Time",
            "Y_axis_label": "Refund rate %",
        },
    }
    LegendLocation = "upper right"
    XaxisLabelRotation = 45
    PlotDateFormatter = mdates.DateFormatter("%Y-%m-%d")

    PlotGridStyle = {
        "which": "both",
        "color": "#666666",
        "linestyle": "--"
    }
    ReferenceLine = {
        "Visible": True,
        "Value": 0,
        "Color": "k"
    }

    FundsList: dict[str, Fund] = field(
        default_factory=dict, init=False, repr=False)

    DataToPlots: dict[str, dict[str, list[dict[str, str | float]]]] = field(
        default_factory=dict, init=False, repr=False
    )
    
    LastYearDataToPlots: dict[str, dict[str, list[dict[str, str | float]]]] = field(
        default_factory=dict, init=False, repr=False
    )

    Summary: dict[str, dict[str, float | int]] = field(
        default_factory=dict, init=False
    )
    
    LastYearSummary: dict[str, dict[str, float | int]] = field(
        default_factory=dict, init=False
    )


    def __post_init__(self):
        for item in self.URLs:
            temp = Fund(URL=item, TimePeriodInMonths=self.TimePeriodInMonths)
            temp.calculateDayToDayChange()

            self.FundsList[temp.getID()] = temp

        self.prepareDataToPlot()
        self.calculateSummaryDetails(self.DataToPlots, self.Summary)
        if self.TimePeriodInMonths <= 12:
            self.calculateSummaryDetails(self.LastYearDataToPlots, self.LastYearSummary)
        return None

    def prepareDataToPlot(self):
        self.DataToPlots["Investment Return Rate"] = {}
        self.LastYearDataToPlots["Investment Return Rate"] = {}
        self.DataToPlots["Price Volatility"] = {}
        self.LastYearDataToPlots["Price Volatility"] = {}

        for fund in self.FundsList:
            refund = self.FundsList[fund].getRefundRateToPlot()
            self.DataToPlots["Investment Return Rate"][fund] = refund["Current"]
            self.LastYearDataToPlots["Investment Return Rate"][fund] = refund["Historical"]
            
            change = self.FundsList[fund].getChangesToPlot()
            self.DataToPlots["Price Volatility"][fund] = change["Current"]
            self.LastYearDataToPlots["Price Volatility"][fund] = change["Historical"]

        return None

    def calculateSummaryDetails(self, source, destination):

        for fund in self.FundsList:
            destination[fund] = {}
            destination[fund]["Name"] = self.FundsList[fund].getName()
            destination[fund]["ID"] = self.FundsList[fund].getID()
            destination[fund]["Refund"] = source["Investment Return Rate"][fund]["value"][-1]

            decrease = []
            increase = []
            for value in source["Price Volatility"][fund]["value"]:
                if value > 0:
                    increase.append(value)
                if value < 0:
                    decrease.append(value)

            destination[fund]["Raise ratio"] = (
                round((len(increase) / (len(increase) + len(decrease)) * 100), 2)
            )
            try:
                destination[fund]["Avg Increase"] = round(
                    sum(increase) / len(increase), 2
                )
            except:
                destination[fund]["Avg Increase"] = "--"
            try:
                destination[fund]["Avg Decrease"] = round(
                    sum(decrease) / len(decrease), 2
                )
            except:
                destination[fund]["Avg Decrease"] = "--"

    def showAnalysisSummary(self, source, title: str):
        dataList = []
        for fund in source:
            dataList.append(convertNumericToStrPlsMnsSigns(
                inputData=source[fund],
                columnsExcludedFromSigns=[],
                currencyColumnNames=[],
                currency="",
                percentageColumnNames=[
                    "Refund", "Raise ratio", "Avg Increase", "Avg Decrease"
                ],
            )
            )

        dataHeaders = list(source[fund].keys())
        print("\n")
        print(" ".join(title))
        print(
            tabulate(
                tabular_data=dataList,
                tablefmt="github",
                headers=dataHeaders
            )
        )
        print("\n")

    def showAnalysisPlot(self):
        
        if self.TimePeriodInMonths <= 12:
            self.showAnalysisSummary(self.LastYearSummary, f"Same {self.TimePeriodInMonths} last year")
        self.showAnalysisSummary(self.Summary, f"Last {self.TimePeriodInMonths} months")
        numOfSubPlots = len(self.PlotOrder)

        # Calculate xticks interval
        firstPlot = self.PlotOrder[0]["title"]
        firstFund = list(self.DataToPlots[firstPlot].keys())[0]
        dataLength = len(self.DataToPlots[firstPlot][firstFund]["date"])
        xAxisInterval = 1
        tempLength = dataLength
        while tempLength > 31:
            xAxisInterval += 1
            tempLength = dataLength / xAxisInterval

        figure, axis = plt.subplots(
            numOfSubPlots,
            figsize=(self.PlotSize["X"], self.PlotSize["Y"]),
            num=self.WindowPlotTitle,
        )
        plt.xticks(rotation=self.XaxisLabelRotation)
        plt.gcf().autofmt_xdate()

        legend = []

        for i in range(0, numOfSubPlots):
            maxDatasetLength = {"length": 0, "fundID": ""}
            currentSubPlot = self.PlotOrder[i]["title"]

            for fund in self.DataToPlots[currentSubPlot]:
                fundName = self.FundsList[fund].getName()
                axis[i].plot(
                    self.DataToPlots[currentSubPlot][fund]["date"],
                    self.DataToPlots[currentSubPlot][fund]["value"],
                    label=fundName,
                )
                if fundName not in legend:
                    legend.append(fundName)

                currentDatasetLength = len(
                    self.DataToPlots[currentSubPlot][fund]["date"]
                )

                if maxDatasetLength["length"] < currentDatasetLength:
                    maxDatasetLength["length"] = currentDatasetLength
                    maxDatasetLength["fundID"] = fund

            if self.ReferenceLine["Visible"] == True:
                referenceLine = []
                for val in range(0, maxDatasetLength["length"]):
                    referenceLine.append(self.ReferenceLine["Value"])

                axis[i].plot(
                    self.DataToPlots[currentSubPlot][maxDatasetLength["fundID"]][
                        "date"
                    ],
                    referenceLine,
                    self.ReferenceLine["Color"],
                )

            axis[i].xaxis.set_major_formatter(self.PlotDateFormatter)
            axis[i].xaxis.set_major_locator(
                mdates.DayLocator(interval=xAxisInterval))
            axis[i].grid(
                which=self.PlotGridStyle["which"],
                color=self.PlotGridStyle["color"],
                linestyle=self.PlotGridStyle["linestyle"],
            )
            axis[i].set_title(currentSubPlot)
            axis[i].set_xlabel(self.PlotOrder[i]["X_axis_label"])
            axis[i].set_ylabel(self.PlotOrder[i]["Y_axis_label"])

        # Create 1 legend for each plot
        lines_labels = [ax.get_legend_handles_labels() for ax in figure.axes]
        lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
        figure.legend(
            lines,
            legend,
            loc=self.LegendLocation,
            bbox_to_anchor=(0, -0.1, 1, 1),
            bbox_transform=plt.gcf().transFigure,
        )
        plt.subplots_adjust(
            left=self.PlotOffsetInWindow["left"],
            right=self.PlotOffsetInWindow["right"],
            top=self.PlotOffsetInWindow["top"],
            bottom=self.PlotOffsetInWindow["bottom"],
        )
        plt.show()
