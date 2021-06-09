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
    chart = alt.Chart(data).mark_square(size=75).properties(
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
    paycheckDates.loc[i, 'Hours Worked'] = bundle['Hours Worked:'].sum()
    paycheckDates.loc[i, 'Payout'] = bundle['CHECK'].sum()
    paycheckDates.loc[i, 'Cashout'] = (bundle['Cash Tips'].sum())
    paycheckDates.loc[i, 'Takehome Percent'] = (paycheckDates.loc[i, 'Payout'] / (bundle['Service Charge (Credit Tips)'].sum()))
    paycheckDates.loc[i, 'Avg Tip'] = bundle['Average Tip Percent'].mean()


#############
# Streamlit #
#############
st.set_page_config(page_title="Carlson Data Project", layout='wide')

##############
# Containers #
# (Structure)#
##############
header = st.beta_container()
bigGraph = st.beta_container()
paycheckApp = st.beta_container()
averagesApp = st.beta_container()

##########
# Header #
##########
header.title('Serving Job Performance Project')
header.subheader("Tracking Financial Data:");

##################
# Financial Data #
# One Big Graph! #
##################
#############
#Data Filter#
#############
#
#TODO: Move beta expander into column next to graph
#
with bigGraph.beta_expander('Choose Data to View:'):
    axisCol, dateCol = st.beta_columns(2)
    # Filter Date Range
    startDate = dateCol.date_input('Start Date', datetime.date(2021, 5, 1))
    endDate = dateCol.date_input('End Date', date.today())
    domain = [startDate.isoformat(), endDate.isoformat()]

    # Filter Type of Shift
    #allShiftTypes = raw['Shift'].unique().tolist()
    #shiftsSelected = st.multiselect('Shift Type', allShiftTypes, allShiftTypes[0])
    
    # Filter X Axis
    x = axisCol.selectbox('X-Axis: (Default to Date Worked to represent performance over time)',financialDataCols, 0)
    # Filter Y Axis
    y = axisCol.selectbox('Y-Axis: (Default to Net Sales to represent overall sales performance)', financialDataCols, 3)

# Sets data source as financialData dataframe
financialGraph = scatterPlot(financialData)
# Encodes financialData graph with user selected options.
graph = enc(financialGraph, x, y, 'Shift')
# Render Graph
bigGraph.write(graph)


################
# Paycheck App #
################
paycheckApp.header('Paycheck approximations')
paycheckAppdata, paycheckAppDesc = paycheckApp.beta_columns(2)
paycheckAppDesc.subheader("'Payout' represents the approximate Take-home income after all deductions and taxes")
paycheckAppDesc.subheader('How is the payout calculated?')
paycheckAppDesc.text("Income consists of Credit Tips, Cash tips, and an Hourly Wage.\n5% of Alcohol Sales go to Bartenders, deducted from Credit Tips.\n3% of Food Sales go to Dining Room Attendants, deducted from Credit Tips.\nFederal Tax, State Tax, Medicare, Social Security are all deducted.")

paycheckAppDesc.text("Payout isn't 100% accurate because Breakfast shifts include alcohol sales with no bartender to compensate. \nWhile also tracking Lunch alcohol sales which does require bartender compensation.")

paycheckAppdata.dataframe(paycheckDates, width = 1300)

################
# Averages App #
################
averagesApp.header("Overall Averages:")
averagesAppdata, averagesAppDesc = averagesApp.beta_columns(2)
averagesAppDesc.subheader("Averages gathered from RAW Form data")
averagesAppdata.dataframe(averagesdf, width = 1300)

with st.beta_expander('Dataframes'):
    # Raw Data from Google Form
    st.write("Raw Data from Google Form:")
    st.dataframe(raw)
    # Filtered and Calculated Data
    st.write("Filtered and Calculated Data:")
    st.dataframe(financialData)


st.write("Sam Carlson")
st.write("Computer Science, Data Science & Psychology")
st.write("Link to Github: https://github.com/samuelrcarlson/VillageSamData")