"""
.DESCRIPTION
    Class to calculate refund rate, rise ratio, average increase and decrease and display plot for
    Price Volatility and Investment Return Rate over time.
    
    To init the instance of the class you need to provide:
        - URLs <- list of urls to fund's sites on www.Analizy.pl
        - TimePeriodInMonths <- int number how many months you would like to analyze.
    
    All calculations are performed automatically during post initialization, so the only thing is to use
    .showAnalysisPyPlot() method to show plot and summary in console.
    
.NOTES

    Version:            1.0
    Author:             Stanisław Horna
    Mail:               stanislawhorna@outlook.com
    GitHub Repository:  https://github.com/StanislawHornaGitHub/Investment_fund_Analyzer
    Creation Date:      06-Feb-2024
    ChangeLog:

    Date            Who                     What

"""
# Official and 3-rd party imports
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tabulate import tabulate


# Custom created class modules
from Dependencies.Class_Fund import Fund

# Custom created function modules
from Dependencies.Function_Conversion import convertNumericToStrPlsMnsSigns
from Dependencies.Function_DownloadFundQuotation import getFundIDfromURL


@dataclass(kw_only=False)
class Analyzer:
    # Initialization Variables
    URLs: list[str]
    TimePeriodInMonths: int

    # Constant Variables
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
    XaxisDesiredNumOfLabels = 31
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

    # Calculated Variables
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

        # Loop through each URL, create Fund class instance and calculate Day to Day price change
        for item in self.URLs:
            ID = getFundIDfromURL(item)
            self.FundsList[ID] = Fund(
                URL=item, TimePeriodInMonths=self.TimePeriodInMonths)
            self.FundsList[ID].calculateDayToDayChange()

        # Calculate data for plot
        self.prepareDataToPlot()

        # Calculate data to display in summary table
        self.calculateSummaryDetails(self.DataToPlots, self.Summary)

        # if provided period is less than 1 year calculate data from same period of last year
        if self.TimePeriodInMonths <= 12:
            self.calculateSummaryDetails(
                self.LastYearDataToPlots, self.LastYearSummary)
        return None

    def prepareDataToPlot(self):

        # Prepare keys for plot data
        self.DataToPlots["Investment Return Rate"] = {}
        self.LastYearDataToPlots["Investment Return Rate"] = {}
        self.DataToPlots["Price Volatility"] = {}
        self.LastYearDataToPlots["Price Volatility"] = {}

        # Loop through each fund
        for fund in self.FundsList:

            # get refund rate day by day
            refund = self.FundsList[fund].getRefundRateToPlot()
            # assign data for actual time period
            self.DataToPlots["Investment Return Rate"][fund] = refund["Current"]
            # assign data for same period last year
            self.LastYearDataToPlots["Investment Return Rate"][fund] = refund["Historical"]

            # get price change day by day
            change = self.FundsList[fund].getChangesToPlot()
            # assign data for actual time period
            self.DataToPlots["Price Volatility"][fund] = change["Current"]
            # assign data for same period last year
            self.LastYearDataToPlots["Price Volatility"][fund] = change["Historical"]

        return None

    def calculateSummaryDetails(self, source, destination):

        # Loop through each fund
        for fund in self.FundsList:
            # Prepare key for current fund and provide generic data
            destination[fund] = {}
            destination[fund]["Name"] = self.FundsList[fund].getName()
            destination[fund]["ID"] = self.FundsList[fund].getID()
            destination[fund]["Refund"] = source["Investment Return Rate"][fund]["value"][-1]

            # Init lists for price increases and decreases
            decrease = []
            increase = []
            for value in source["Price Volatility"][fund]["value"]:
                if value > 0:
                    increase.append(value)
                if value < 0:
                    decrease.append(value)

            # Calculate ratio of increases to decreases
            destination[fund]["Raise ratio"] = (
                round((len(increase) / (len(increase) + len(decrease)) * 100), 2)
            )

            # Try to calculate average increase
            try:
                destination[fund]["Avg Increase"] = round(
                    sum(increase) / len(increase), 2
                )
            except:
                # in case where there can be division by 0, which means there were no increases
                destination[fund]["Avg Increase"] = "--"
            # Try to calculate average decrease
            try:
                destination[fund]["Avg Decrease"] = round(
                    sum(decrease) / len(decrease), 2
                )
            except:
                # in case where there can be division by 0, which means there were no increases
                destination[fund]["Avg Decrease"] = "--"

        return None

    def showAnalysisSummary(self, source, title: str):
        # Init list for result table
        dataList = []
        # Loop through each fund in source dict
        for fund in source:
            # Append list with values with added % signs and + or -
            dataList.append(
                convertNumericToStrPlsMnsSigns(
                    inputData=source[fund],
                    columnsExcludedFromSigns=[],
                    currencyColumnNames=[],
                    currency="",
                    percentageColumnNames=[
                        "Refund", "Raise ratio", "Avg Increase", "Avg Decrease"
                    ],
                )
            )

        # Get headers for table
        dataHeaders = list(source[fund].keys())

        # Print table with title
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
        return None

    def showAnalysisPyPlot(self):
        # First of all display summary tables in console

        # If selected period is greater than 12 month skip displaying table for last year
        if self.TimePeriodInMonths <= 12:
            self.showAnalysisSummary(
                self.LastYearSummary,
                f"Same {self.TimePeriodInMonths} months last year"
            )

        # Display summary table for current period
        self.showAnalysisSummary(
            self.Summary,
            f"Last {self.TimePeriodInMonths} months"
        )

        numOfSubPlots = len(self.PlotOrder)

        # Calculate xticks interval, to prevent overlapping labels on X axis
        firstPlot = self.PlotOrder[0]["title"]
        firstFund = list(self.DataToPlots[firstPlot].keys())[0]
        dataLength = len(self.DataToPlots[firstPlot][firstFund]["date"])
        xAxisInterval = 1
        tempLength = dataLength

        # Loop until displayed number of X labels will be less than constant desired num of labels
        while tempLength > self.XaxisDesiredNumOfLabels:
            xAxisInterval += 1
            tempLength = dataLength / xAxisInterval

        # Init sub plots with desired size and window title
        figure, axis = plt.subplots(
            numOfSubPlots,
            figsize=(self.PlotSize["X"], self.PlotSize["Y"]),
            num=f"{self.WindowPlotTitle} {self.TimePeriodInMonths} months",
        )

        # Define X labels rotation
        plt.xticks(rotation=self.XaxisLabelRotation)
        # display labels only on lower subplot
        plt.gcf().autofmt_xdate()

        legend = []

        # Loop through subplots
        for i in range(0, numOfSubPlots):
            # Init local variable to find largest data set on current subplot
            maxDatasetLength = {"length": 0, "fundID": ""}
            currentSubPlot = self.PlotOrder[i]["title"]

            # Loop through funds for current subplot
            for fund in self.DataToPlots[currentSubPlot]:
                fundName = self.FundsList[fund].getName()

                # Add fund data for current subplot
                axis[i].plot(
                    self.DataToPlots[currentSubPlot][fund]["date"],
                    self.DataToPlots[currentSubPlot][fund]["value"],
                    label=fundName,
                )

                # Check if name for current fund exists in legend, if not add it
                if fundName not in legend:
                    legend.append(fundName)

                # Get length of current data set
                currentDatasetLength = len(
                    self.DataToPlots[currentSubPlot][fund]["date"]
                )
                # Check if current data set is larger than largest one so far
                if maxDatasetLength["length"] < currentDatasetLength:
                    maxDatasetLength["length"] = currentDatasetLength
                    maxDatasetLength["fundID"] = fund

            # If reference line is set to true, create appropriate data set with desired value
            if self.ReferenceLine["Visible"] == True:
                referenceLine = []
                for val in range(0, maxDatasetLength["length"]):
                    referenceLine.append(self.ReferenceLine["Value"])
                # Add reference line to current subplot
                axis[i].plot(
                    self.DataToPlots[currentSubPlot][maxDatasetLength["fundID"]]["date"],
                    referenceLine,
                    self.ReferenceLine["Color"],
                )
            # Set formatter for X axis in current subplot
            axis[i].xaxis.set_major_formatter(self.PlotDateFormatter)
            # Set interval for X axis labels in current subplot
            axis[i].xaxis.set_major_locator(
                mdates.DayLocator(interval=xAxisInterval))
            # Add grid line for current subplot
            axis[i].grid(
                which=self.PlotGridStyle["which"],
                color=self.PlotGridStyle["color"],
                linestyle=self.PlotGridStyle["linestyle"],
            )
            # Set plot title and X, Y axis titles
            axis[i].set_title(currentSubPlot)
            axis[i].set_xlabel(self.PlotOrder[i]["X_axis_label"])
            axis[i].set_ylabel(self.PlotOrder[i]["Y_axis_label"])

        # Force 1 legend for each plot
        lines_labels = [ax.get_legend_handles_labels() for ax in figure.axes]
        lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
        figure.legend(
            lines,
            legend,
            loc=self.LegendLocation,
            bbox_to_anchor=(0, -0.1, 1, 1),
            bbox_transform=plt.gcf().transFigure,
        )
        # Define position of plots in displayed window
        plt.subplots_adjust(
            left=self.PlotOffsetInWindow["left"],
            right=self.PlotOffsetInWindow["right"],
            top=self.PlotOffsetInWindow["top"],
            bottom=self.PlotOffsetInWindow["bottom"],
        )
        # Display configured plots
        plt.show()
        return None
