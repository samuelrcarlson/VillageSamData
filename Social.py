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

fedTax = .079
stateTax = .0398
medicare = .01452
socSec = .062
draCut = .03
barCut = .05

# TO DO: 
# Separate encoding()
def scatterPlot(data):
    chart = alt.Chart(data).mark_point(size=75).properties(
            width=750,
            height=750
    )
    return chart

def enc(chart, x, y, group):
    chart = chart.encode(
    x=x,
    y=y,
    color=group,
    tooltip=[x, y, group, 'Date Worked']).interactive(
    )
    return chart


##############
# RAW import #
##############
#Import Google Sheet as .xlsx through Published sheet
raw = pd.read_excel ("https://docs.google.com/spreadsheets/d/e/2PACX-1vT9s3a6JIvnQdmjhCmAXajFqFeCkntFIr9v6t8aAHjJxBZjD09PZcajqwTt1Gjk5BWGzb-B0XzflX2_/pub?output=xlsx")
#Adjust Date Time for raw data
raw['Date Worked'] = pd.to_datetime(raw['Date Worked'])

############
# Averages #
############
# Average Hours per Shift
avgHoursWorked = raw["Hours Worked:"].mean()
# All Credit Tips Recorded
totalTips = (raw["Service Charge (Credit Tips)"].sum() + raw["Cash Tips"].sum())
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
        'Avg Tip Percent': [avgTipPercent],
        'Sum of Tips': [totalTips]
       }

averagesdf = pd.DataFrame(data=averageData)

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
# Calculate how 
financialData['CHECK'] = (financialData['Hourly Pay'] + financialData['Takehome Credit Tips']) - (((financialData['Hourly Pay'] + financialData['Takehome Credit Tips']) * fedTax) - (((financialData['Hourly Pay'] + financialData['Takehome Credit Tips']) * stateTax)) + (((financialData['Hourly Pay'] + financialData['Takehome Credit Tips']) * medicare) + ((financialData['Hourly Pay'] + financialData['Takehome Credit Tips']) * socSec)))
financialData['Average Tip Percent'] = (financialData['Cash Tips'] + financialData['Service Charge (Credit Tips)'])/ financialData['Net Sales']

financialDataCols = list(financialData)
#################
# Paycheck Math #
#################
#Import .csv with Pay period groupings.
paycheckDates = pd.read_csv('Paydates.csv')

# Compare each financialData date worked and group into appropriate pay periods
# .loc[i, "#"] places column per i row
for i in range(len(paycheckDates)) :
    bundle = financialData.loc[(financialData['Date Worked'] >= paycheckDates.loc[i, "Start"] ) & (financialData['Date Worked'] <= paycheckDates.loc[i, "End"])]
    paycheckDates.loc[i, 'Payout'] = bundle['CHECK'].sum()
    paycheckDates.loc[i, 'Hours Worked'] = bundle['Hours Worked:'].sum()
    paycheckDates.loc[i, 'Cashout'] = bundle['Cash Tips'].sum()
    paycheckDates.loc[i, 'Avg Tip'] = bundle['Average Tip Percent'].mean()

#############
# Streamlit #
#############

st.title('VS@BE Personal Financial Performance Project')
st.header("Sam Carlson");
st.write("git: https://github.com/samuelrcarlson/VillageSamData")

#Encoding Charts happens AFTER user selects preferences...

#############
#Data Filter#
#############
with st.beta_expander('Filter Data Settings'):
    # Filter Date Range
    #startDate = st.date_input('Start Date', datetime.date(2021, 5, 1))
    #endDate = st.date_input('End Date', date.today())
    #domain = [startDate.isoformat(), endDate.isoformat()]

    # Filter Type of Shift
    #allShiftTypes = raw['Shift'].unique().tolist()
    #shiftsSelected = st.multiselect('Shift Type', allShiftTypes, allShiftTypes[0])

    # Filter X Axis
    x = st.selectbox('X-Axis: ',financialDataCols, 0)
    # Filter Y Axis
    y = st.selectbox('Y-Axis:', financialDataCols, 3)

##################
# Financial Data #
# One Big Graph! #
##################

financialGraph = scatterPlot(financialData)
graph = enc(financialGraph, x, y, 'Shift')
st.write(graph)


######################
# Paycheck dataframe #
######################
with st.beta_expander('Paycheck approximations'):
    st.write(paycheckDates)

###############
# Averages df #
###############
#st.write(averagesdf)

with st.beta_expander('Dataframes'):
    # Raw Data from Google Form
    st.write("Raw Data from Google Form:")
    st.write(raw)
    # Filtered and Calculated Data
    st.write("Filtered and Calculated Data:")
    st.write(financialData)
    # Averages Data
    st.write("Averages Data:")
    st.write(averagesdf)