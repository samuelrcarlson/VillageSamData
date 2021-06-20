# Sam Carlson
# VS@BE Personal financial performance project
# 2021

#######################
# Imports and Methods #
#######################
import pandas as pd
import altair as alt
import streamlit as st
import datetime
from datetime import date


deduction = 0.05
fedTax = .079
stateTax = .0398
medicare = .01452
socSec = .062
draCut = .03
barCut = .05

today = date.today().isoformat()

def scatterPlot(data):
    chart = alt.Chart(data).mark_circle(size=125).properties(
            width=1100,
            height=700
    )
    return chart

def barChart(data):
    chart = alt.Chart(data).mark_bar().properties(
        width=1100,
        height=700
    )
    return chart

def enc(chart, x, y, group):
    chart = chart.encode(
    x=x,
    y=y,
    color=group,
    tooltip=[x, y, group, 'Date Worked'])
    return chart

def barChartConv(chart):
    chart = chart.mark_bar(size=15)
    return chart

##############
# RAW import #
##############
#Import Google Sheet as .xlsx through Published sheet
raw = pd.read_excel ("https://docs.google.com/spreadsheets/d/e/2PACX-1vT9s3a6JIvnQdmjhCmAXajFqFeCkntFIr9v6t8aAHjJxBZjD09PZcajqwTt1Gjk5BWGzb-B0XzflX2_/pub?output=xlsx")
#Adjust Date Time for raw data
raw['Date Worked'] = pd.to_datetime(raw['Date Worked'])

#######################
# Actual Paystub Data #
#######################
#Import Actual Paystub Data
rawstub = pd.read_excel ("https://docs.google.com/spreadsheets/d/e/2PACX-1vTIT-QimZzDIgIWILbYzEvIslI7XhvNKOGiQy5Ndx_ARExGHHJAfKTkC-G33n-WoG0ozvirbccqwleb/pub?output=xlsx")
#Adjust Pay Date for processing
rawstub['Pay Date'] = pd.to_datetime(rawstub['Pay Date'])

#paystubdf = rawstub[["", ""]].copy

############
# Averages #
############
# Average Hours per Shift
avgHoursWorked = raw["Hours Worked:"].mean()
# Average Net Sales
avgNetSales = raw["Net Sales"].mean()
# Average Credit Tips per Shift
avgCrdtTips = raw["Service Charge (Credit Tips)"].mean()
# Average Cash Tip per Shift
avgCashTips = raw["Cash Tips"].mean()
# Average Hourly Rate (Tips only)
avgTipPerHour = ((avgCrdtTips + avgCashTips)/avgHoursWorked)
# Average Tip Percentage
avgTipPercent = (((avgCrdtTips + avgCashTips) / avgNetSales) * 100)

averageData = {'Avg Hours per Shift': [avgHoursWorked],
        'Avg Net Sales': [avgNetSales],
        'Avg Credit Tips': [avgCrdtTips],
        'Avg Cash Tips': [avgCashTips],
        'Avg Tips per Hour': [avgTipPerHour],
        'Avg Tip Percent': [avgTipPercent]
       }
averagesdf = pd.DataFrame(data=averageData)

############
# Sum Data #
############
# Total Shifts Worked
sumShiftsWorked = len(raw)
# Total Hours Worked
sumHoursWorked = raw["Hours Worked:"].sum()
# All Tips Recorded
totalTips = ((raw["Service Charge (Credit Tips)"].sum()) + (raw["Cash Tips"].sum()))
# All Credit Tips
sumCredtTips = raw["Service Charge (Credit Tips)"].sum()
# All Cash Tipe
sumCashTips = raw["Cash Tips"].sum()
# All Food Sales
sumFoodSales = raw['Food Sales'].sum()
# All Beer
sumBeerSales = raw['Beer Sales'].sum()
# All Wine
sumWineSales = raw['Wine Sales'].sum()
# All Liquor
sumLiquorSales = raw['Liquor Sales'].sum()

sumData = {'Total Hours': [sumHoursWorked],
        'Total Tips': [totalTips],
        'Credit Tips': [sumCredtTips],
        'Cash Tips': [sumCashTips],
        'Total Food Sales': [sumFoodSales],
        'Total Beer Sales': [sumBeerSales],
        'Total Wine Sales': [sumWineSales],
        'Total Liquor Sales': [sumLiquorSales]
       }
sumdf = pd.DataFrame(data=sumData)

##################
# Main Dataframe #
# Financial Data #
##################

financialData = raw[["Date Worked", "Shift", "Hours Worked:", "Net Sales", "Food Sales", "Liquor Sales", "Beer Sales", "Wine Sales", "Cash Tips", "Service Charge (Credit Tips)"]].copy()

# Calculate DRA Cut for every Shift (3% Food Sales)
financialData['DRA Cut'] = financialData['Food Sales'] * draCut
# Calculate Alcohol (Bar) Cut for every shift (5% Alcohol Sales)
financialData['Alcohol Cut'] = ((financialData['Liquor Sales'] + financialData['Beer Sales'] + financialData['Wine Sales']) * barCut)
# Deduct DRA And Alcohol Cut from Credit Tips
financialData['Takehome Credit Tips'] = financialData['Service Charge (Credit Tips)'] - (financialData['DRA Cut'] + financialData['Alcohol Cut'])
# Calculate Hourly Rate pay ($3.13)
financialData['Hourly Pay'] = ((financialData['Hours Worked:'] * 3.13))
#Calculate Deductions
financialData['401k'] = (financialData['Hourly Pay'] + financialData['Takehome Credit Tips']) * deduction
# Calculate Taxes and Deductions
financialData['Taxes'] = (((financialData['Hourly Pay'] + financialData['Takehome Credit Tips']) * fedTax) + ((financialData['Hourly Pay'] + financialData['Takehome Credit Tips']) * stateTax)+ ((financialData['Hourly Pay'] + financialData['Takehome Credit Tips']) * medicare) + ((financialData['Hourly Pay'] + financialData['Takehome Credit Tips']) * socSec))
# Calculate Check payout after Tax/Deductions
financialData['CHECK'] = (financialData['Hourly Pay'] + financialData['Takehome Credit Tips']) - (financialData['401k'] + financialData['Taxes'])

financialData['Average Tip Percent'] = (financialData['Cash Tips'] + financialData['Service Charge (Credit Tips)']) / financialData['Net Sales']

financialDataCols = list(financialData)

#
#
#

######################
# Net sale Breakdown #
######################
netSaleBreakdown = raw[["Date Worked", "Shift", "Net Sales", "Food Sales", "Liquor Sales", "Beer Sales", "Wine Sales"]].copy()

stackedChart = alt.Chart(netSaleBreakdown).transform_fold(
  ['Food Sales', 'Liquor Sales', "Beer Sales", "Wine Sales"],
  as_=['Sales', 'Net Sales']
).mark_bar(size = 9).encode(
  x='Net Sales:Q',
  y='Date Worked:T',
  color='Sales:N',
  tooltip=['Date Worked', 'Food Sales', 'Liquor Sales', "Beer Sales", "Wine Sales"]).properties(
    width=1100,
    height=400
    
)

shiftBreakdownChart = stackedChart.mark_bar(size = 75).encode(
    y='Shift',
)

#################
# Tip Breakdown #
#################
tipBreakdown = raw[["Date Worked", "Net Sales", "Service Charge (Credit Tips)", "Cash Tips"]].copy()
tipBreakdown['Average Tip Percentage'] = (tipBreakdown['Service Charge (Credit Tips)'] + tipBreakdown['Cash Tips']) / tipBreakdown['Net Sales']

stackedTipChart = alt.Chart(tipBreakdown).transform_fold(
  ["Service Charge (Credit Tips)", "Cash Tips"],
  as_=['Tip', 'Tips']
).mark_bar(size = 9).encode(
  x='Date Worked:T',
  y='Tips:Q',
  color='Tip:N',
  tooltip=["Date Worked", "Average Tip Percentage", "Service Charge (Credit Tips)", "Cash Tips"]).properties(
    width=1100,
    height=400
)

#################
# Paycheck Math #
#################
#Import .csv with Pay period groupings.
paycheckDates = pd.read_csv('Paydates.csv')
paycheckDates = paycheckDates[paycheckDates['Start'] <= today]

# Compare each financialData date worked and group into appropriate pay periods
# .loc[i, "#"] places column per i row
for i in range(len(paycheckDates)) :
    bundle = financialData.loc[(financialData['Date Worked'] >= paycheckDates.loc[i, "Start"] ) & (financialData['Date Worked'] <= paycheckDates.loc[i, "End"])]
    paycheckDates.loc[i, 'Hours Worked'] = bundle['Hours Worked:'].sum()
    paycheckDates.loc[i, 'Payout'] = bundle['CHECK'].sum()
    paycheckDates.loc[i, 'Cashout'] = (bundle['Cash Tips'].sum())
    paycheckDates.loc[i, 'Takehome Percent'] = (paycheckDates.loc[i, 'Payout'] / (bundle['Service Charge (Credit Tips)'].sum()))
    paycheckDates.loc[i, 'Avg Tip'] = bundle['Average Tip Percent'].mean()
    #temp
    paycheckDates.loc[i, 'Takehome Credit Tips'] = bundle['Takehome Credit Tips'].sum()
    paycheckDates.loc[i, 'Taxes'] = bundle['Taxes'].sum()
    paycheckDates.loc[i, '401k'] = bundle['401k'].sum()
paycheckDates['Old Job Pay'] = ((paycheckDates['Hours Worked'] * 14.50) * .92)


########################################################################
# Streamlit #
########################################################################
st.set_page_config(page_title="Carlson Data Project", layout='wide')

##############
# Containers #
# (Structure)#
##############
header = st.beta_container()
bigGraph = st.beta_container()
averagesApp = st.beta_container()
sumApp = st.beta_container()
salesBreakdownApp = st.beta_container()
tipBreakdownApp = st.beta_container()
paycheckApp = st.beta_container()
footer = st.beta_container()

testBed = st.beta_container()

##########
# Header #
##########
header.title('Serving Job Performance Project')

##################
# Financial Data #
# Highlights!    #
##################
bigGraph.header("Tracking Financial Data:");
bigGraphCol, emptyCol = bigGraph.beta_columns(2)
#############
#Data Filter#
#############
settings =  bigGraphCol.beta_expander('Graph Settings', expanded=True)
# Filter Date Range
#startDate = settings.date_input('Start Date', datetime.date(2021, 5, 1))
#endDate = settings.date_input('End Date', date.today())
#domain = [startDate.isoformat(), endDate.isoformat()]

# Filter Type of Shift
#allShiftTypes = raw['Shift'].unique().tolist()
#shiftsSelected = st.multiselect('Shift Type', allShiftTypes, allShiftTypes[0])

# Filter X Axis
x = settings.selectbox('X-Axis: (Default to Date Worked to represent performance over time)',financialDataCols, 0)
# Filter Y Axis
y = settings.selectbox('Y-Axis: (Default to Net Sales to represent overall sales performance)', financialDataCols, 3)

# Sets data source as financialData dataframe
financialGraph = scatterPlot(financialData)
# Encodes financialData graph with user selected options.
graph = enc(financialGraph, x, y, 'Shift')
# Render Graph
bigGraphCol.write(graph)

################
# Averages App #
################
averagesApp.header("Overall Averages:")
averagesApp.dataframe(averagesdf, width = 1100)

#######################
# Total Sales App #
#######################
salesBreakdownApp.header("Sales Breakdown Over Time:")

salesBreakdownApp.subheader("Per Day:")
salesBreakdownApp.write(stackedChart)
salesBreakdownApp.subheader("Per Shift Type:")
salesBreakdownApp.write(shiftBreakdownChart)
#salesBreakdownApp.write(netSaleBreakdown)

################
# Paycheck App #
################
paycheckApp.header('Paycheck Approximations:')
paycheckApp.dataframe(paycheckDates, width = 1300)
explanation = paycheckApp.beta_expander('Explanation:')
explanation.subheader("'Payout' represents the approximate Take-home income after all deductions and taxes")
explanation.subheader("How is the 'Payout' calculated?")
explanation.text("Income consists of Credit Tips, Cash tips, and an Hourly Wage.\n5% of Alcohol Sales go to Bartenders, deducted from Credit Tips.\n3% of Food Sales go to Dining Room Attendants, deducted from Credit Tips.\nFederal Tax, State Tax, Medicare, Social Security are all deducted.")
explanation.text("Payout isn't 100% accurate because Breakfast shifts include alcohol sales with no bartender to compensate. \nWhile also tracking Lunch alcohol sales which does require bartender compensation.")
explanation.subheader("Takehome Percentage:")
explanation.text("Takehome percentage represents how much of my earned Credit Tips aren't being deducted to compensate DRAs/Bartenders")
explanation.text("Weeks where my Alcohol sand Food Sales are low; but my Tip Percentages are high raise this percentage")
explanation.subheader("Old Job Pay")
explanation.text("$14.50/Hour * .92 , to represent why I left my old job.")
#####################
# Total Sales App #
#####################
sumApp.header("Total Sales:")
sumApp.dataframe(sumdf, width = 1100)


#####################
# Personal Tip Data #
#####################
tipBreakdownApp.header('Tip Breakdown')
#tipBreakdownApp.write(tipBreakdown)
tipBreakdownApp.write(stackedTipChart)

##################
# Raw Dataframes #
##################
with footer.beta_expander('Dataframes'):
    # Raw Data from Google Form
    st.write("Raw Data from Google Form:")
    st.dataframe(raw)
    st.write("Raw Paystub Data:")
    st.dataframe(rawstub)
    # Filtered and Calculated Data
    st.write("Filtered and Calculated Data:")
    st.dataframe(financialData)
footer.write("Sam Carlson")
footer.write("Computer Science, Data Science, and Psychology")
footer.write("Link to Github: https://github.com/samuelrcarlson/VillageSamData")

#with testBed.beta_expander('Test Space:'):
#    st.write(paycheckDates['Payout'].head(6).mean())

#    financialBar = barChartConv(financialGraph)
#    financialBar = enc(financialBar, 'Date Worked', 'Takehome Credit Tips', 'Shift')
#    st.write(financialBar)