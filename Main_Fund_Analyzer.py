"""
.SYNOPSIS
    Program to analyze investment funds defined in config file.
    For each fund int selected timeframe following parameters will be calculated: 
        - Refund
        - Rise ratio
        - Avg Increase
        - Avg Decrease.
    Each described param will be calculated for current period and same time last year.

.DESCRIPTION
    CONFIG.json structure:
    {
        "URLs": [
            "<URL_To_Fund_1>",
            "<URL_To_Fund_2>",
            "<URL_To_Fund_3>",
            "<URL_To_Fund_4>"
        ],
        "TimePeriodInMonths": <int>
    }
    
    URLs <- list of URL to funds which will be checked
    TimePeriodInMonths <- time period to analyze passed as int
    
    
.INPUTS
        --Time_Period_In_Months <- replaces time period defined in config file
        --Config_File_Name <- Config file name, which must be located in the same dir as executed file

.OUTPUTS
    None

.NOTES

    Version:            1.0
    Author:             Stanislaw Horna
    Mail:               stanislawhorna@outlook.com
    GitHub Repository:  https://github.com/StanislawHornaGitHub/Investment_fund_Analyzer
    Creation Date:      06-Feb-2024
    ChangeLog:

    Date            Who                     What

"""
import argparse
from Dependencies.Class_Analyzer import Analyzer
from Dependencies.Function_config import getConfiguration, setCorrectPath

programSynopsis = """
Program to analyze investment funds defined in config file.
For each fund int selected timeframe following parameters will be calculated: Refund ; Rise ratio ; Avg Increase ; Avg Decrease.
Each described param will be calculated for current period and same time last year.
"""

parser = argparse.ArgumentParser(description=programSynopsis)
parser.add_argument(
    "-t",
    "--Time_Period_In_Months",
    action="store",
    type=int,
    help="Replaces TimePeriodInMonths to the number passed to script",
)
parser.add_argument(
    "-c",
    "--Config_File_Name",
    action="store",
    help="Config file name, which must be located in the same dir as executed file",
)

def main(options):
    setCorrectPath()

    config = getConfiguration(options)
    
    funds = Analyzer(**config)

    funds.showAnalysisPyPlot()

    exit(0)

if __name__ == "__main__":
    main(parser.parse_args())