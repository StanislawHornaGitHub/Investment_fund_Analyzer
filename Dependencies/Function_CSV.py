import csv

def readCSVfile(fileName: str, delimiterSign: str =","):
    with open(fileName, "r") as file:
        reader = csv.DictReader(file, delimiter=delimiterSign)
        
        resultList = []
        for row in reader:
            resultList.append(row)
    
    return resultList

def writeCSVfile(ListToWrite: list, fileName: str, delimiterSign: str =","):
    
    headers = list(ListToWrite[0].keys())
    
    with open(fileName, "w") as resFile:
        writer = csv.writer(resFile, delimiter=delimiterSign)
        writer.writerow(headers)
        
        for row in ListToWrite:
            lineToWrite = []
            for column in headers:
                lineToWrite.append(row[column])
            writer.writerow(lineToWrite)