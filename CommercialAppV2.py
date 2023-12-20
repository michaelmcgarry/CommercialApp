#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 14:45:47 2023

@author: michaelmcgarry
"""

import streamlit as st
import pandas as pd
import base64
import io
from datetime import time

#Define Functions Here
weekdays = {0: 'Mon',
           1: 'Tue',
           2: 'Wed',
           3: 'Thu',
           4: 'Fri',
           5: 'Sat',
           6: 'Sun'}

def get_comp_fixtures_by_month(df,sport,country,competition):
    if sport not in df['Sport'].unique():
        print(f"Sport: {sport} not in dataset")
        return None
    
    countries = df.loc[df['Sport']==sport]['Country'].unique()
    if country not in countries:
        print(f"Country: {country} not in dataset")
        return None
    
    comps = df.loc[(df['Sport']==sport)&(df['Country']==country)]['Competition'].unique()
    
    if competition not in comps:
        print(f"Competition: {competition} not in dataset")
        return None
    else:
        print("Located Competition...")
        
    #Filter for this comp
    _ = df.loc[(df['Sport']==sport)&(df['Country']==country)&(df['Competition']==competition)].copy()
    _['Month'] = _['StartDateTime'].apply(lambda x: x.month)
    
    total_events = len(_)
    
    #Group by Months and total the number of events each month
    _ = _.groupby(['Sport','Country','Competition','Month']).agg(NumEvents=('Competition','count')).reset_index()
    
    #Calculate Percentage of Events
    _['PctEvents'] = round(_['NumEvents'] / total_events*100,2)
    
    # Create a reference DataFrame with all months
    all_months = pd.DataFrame({'Month': range(1, 13)})
    
    # Merge the reference DataFrame with the original DataFrame
    merged_df = _.merge(all_months, on='Month', how='outer')
    
    # Fill missing values with 0 and set Sport, Country, and Competition
    merged_df['NumEvents'].fillna(0, inplace=True)
    merged_df['PctEvents'].fillna(0, inplace=True)
    merged_df['Sport'].fillna(sport, inplace=True)
    merged_df['Country'].fillna(country, inplace=True)
    merged_df['Competition'].fillna(competition, inplace=True)
    
    # Sort the DataFrame by 'Month' in ascending order
    merged_df.sort_values(by='Month', inplace=True)
    
    return merged_df

def get_pct_matches_weekdays(df,weekdays,sport,country,competition):
    if sport not in df['Sport'].unique():
        print(f"Sport: {sport} not in dataset")
        return None
    
    countries = df.loc[df['Sport']==sport]['Country'].unique()
    if country not in countries:
        print(f"Country: {country} not in dataset")
        return None
    
    comps = df.loc[(df['Sport']==sport)&(df['Country']==country)]['Competition'].unique()
    
    if competition not in comps:
        print(f"Competition: {competition} not in dataset")
        return None
    else:
        print("Located Competition...")   
    
    #Filter for this comp
    _ = df.loc[(df['Sport']==sport)&(df['Country']==country)&(df['Competition']==competition)].copy()
    
    total_events = len(_)        
    
    #Group by Weekdays and get a count of fixtures each day
    _ = _.groupby(['Sport','Country','Competition','Weekday']).agg(NumEvents=('Competition','count')).reset_index()
    
    #Calc Percentage of Events on each day
    _['PctEvents'] = round(_['NumEvents'] / total_events * 100,2)
    
    # Create a reference DataFrame with all days
    all_months = pd.DataFrame({'Weekday': range(7)})
    
    # Merge the reference DataFrame with the original DataFrame
    merged_df = _.merge(all_months, on='Weekday', how='outer')
    
    # Fill missing values with 0 and set Sport, Country, and Competition
    merged_df['NumEvents'].fillna(0, inplace=True)
    merged_df['PctEvents'].fillna(0, inplace=True)
    merged_df['Sport'].fillna(sport, inplace=True)
    merged_df['Country'].fillna(country, inplace=True)
    merged_df['Competition'].fillna(competition, inplace=True)
    
    # Sort the DataFrame by 'Month' in ascending order
    merged_df.sort_values(by='Weekday', inplace=True)
    
    merged_df['Weekday'] = merged_df['Weekday'].apply(lambda x: weekdays[x])
    
    return merged_df

def get_pct_matches_start_times(df,weekdays,sport,country,competition,threshold=0.0):
    if sport not in df['Sport'].unique():
        print(f"Sport: {sport} not in dataset")
        return None
    
    countries = df.loc[df['Sport']==sport]['Country'].unique()
    if country not in countries:
        print(f"Country: {country} not in dataset")
        return None
    
    comps = df.loc[(df['Sport']==sport)&(df['Country']==country)]['Competition'].unique()
    
    if competition not in comps:
        print(f"Competition: {competition} not in dataset")
        return None
    else:
        print("Located Competition...")   
    
    #Filter for this comp
    _ = df.loc[(df['Sport']==sport)&(df['Country']==country)&(df['Competition']==competition)].copy()
    _['StartTime'] = _['StartDateTime'].apply(lambda x: x.time())
    total_events = len(_)        
    
    #Group by Weekdays and Start Times and get a count of fixtures for each start time
    #Get Avg Concurrency for each Concurrency Type also
    _ = _.groupby(['Sport','Country','Competition','Weekday','StartTime']).agg(NumEvents=('Competition','count')).reset_index()
    
 
    #Calc Percentage of Events on each day
    _['PctEvents'] = round(_['NumEvents'] / total_events * 100,2)
    
    _.sort_values(by=['Weekday','StartTime'], inplace=True)
    
    _['Weekday'] = _['Weekday'].apply(lambda x: weekdays[x])
    
    _ = _.loc[_['PctEvents']>=threshold].copy()
    
    return _

def generate_excel_download(df, filename, download_text):
    towrite = io.BytesIO()
    df.to_excel(towrite, encoding='utf-8', index=False, header=True)
    towrite.seek(0) # reset pointer
    b64 = base64.b64encode(towrite.read()).decode() # some strings
    linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download={filename}>{download_text}</a>'
    st.markdown(linko, unsafe_allow_html=True)

#Import Data Here
#Import from Boto3 AWS S3 Bucket in Final State!
df = pd.read_csv('MFL_Data_2022.csv',parse_dates=['StartDateTime','EndDateTime'])
df['Weekday'] = df['StartDateTime'].apply(lambda x: x.weekday())

#Get Unique List of Sports
sportlist = sorted(df['Sport'].unique())
sportlist.insert(0,"--Please Select--")

def display_text(text):
    st.markdown(f"- {text}")
    
def home_page():
    st.title("Commercial Tool")
    st.write("Select a report type, then apply your filters in the sidebar.")
    report_type = st.selectbox("Select a report type", ["Home", "Comp Scheduling", "Sport Concurrency", "Perform Operator Views"])
  
    if report_type == "Home":
        display_home_page()
    elif report_type == "Comp Scheduling":
        report_1_page()
    elif report_type == "Sport Concurrency":
        report_2_page()
    elif report_type == "Perform Operator Views":
        report_3_page()
        
def display_home_page():
    #Write Descriptions of each report:
    # First Report: Comp Scheduling
    st.header("Comp Scheduling Report")
    display_text("Comp Scheduling allows users to select a sport and competition, and will return the total number and % of games at each unique start time throughout the week, as well as the monthly matches and seasonality of the competition.")
    
    # Second Report: Sport Concurrency
    st.header("Sport Concurrency Report")
    display_text("Sport Concurrency allows users to select a sport, list of months, and a single day of the week and time range. This report will output a list of competitions which take place in this time window alongside the total number of games they have in the year.")
    
    # Third Report: Perform Operator Views
    st.header("Perform Operator Views Report")
    display_text("Perform Operator Views allows users to select a sport and competition, and outputs a list of operators who streamed that competition alongside their total events, total unique users, average unique users, and average unique users across all competitions in that sport.") 
    

def report_1_page():
    st.title("Competition Scheduling")
    st.sidebar.image("IGM Primary Inv logotype.png", use_column_width=True)
    
    with st.sidebar:
        selected_sport = st.selectbox("Select a sport", sportlist)
        
        countrylist = sorted(df.loc[df['Sport']==selected_sport]['Country'].unique())
        countrylist.insert(0,"--Please Select--")
        
        selected_country = st.selectbox("Select A Country:",countrylist)
        selected_comp = "--Please Select--"
        
    #If a country has been selected, prompt user to select a competition
    if selected_country != "--Please Select--":
        complist = sorted(df.loc[(df['Sport']==selected_sport)&(df['Country']==selected_country)]['Competition'].unique())
        complist.insert(0,"--Please Select--")
        selected_comp = st.selectbox("Select A Competition:",complist)
        
        if selected_comp != "--Please Select--":
            with st.container():
                if st.button(f"Click Here To Generate Reports For {selected_country} {selected_comp} {selected_sport}"):
                    total_fixtures = len(df.loc[(df['Sport']==selected_sport)&(df['Country']==selected_country)&(df['Competition']==selected_comp)])
                    st.write(f"Total Annual Fixtures: {total_fixtures}")

                    
                    #Get Monthly Fixtures Data & Download Excel Link
                    monthly_fixtures = get_comp_fixtures_by_month(df,selected_sport,selected_country,selected_comp)
                    st.dataframe(monthly_fixtures)
                    
                    #Get Seasonality
                    # Create a mapping for summer and winter months
                    summer_months = [5, 6, 7, 8]  # May, June, July, August
                    winter_months = [11, 12, 1, 2]  # November, December, January, February
                    
                    # Assuming df is your DataFrame
                    # You may need to adjust column names based on your actual DataFrame
                    summer_events = monthly_fixtures[monthly_fixtures['Month'].isin(summer_months)]['NumEvents'].sum()
                    winter_events = monthly_fixtures[monthly_fixtures['Month'].isin(winter_months)]['NumEvents'].sum()
                    
                    # Check and return the result
                    if summer_events > winter_events:
                        season = "Summer"
                    elif summer_events < winter_events:
                        season = "Winter"
                    else:
                        season = "Unknown"
                    st.write(f"Season: {season}")
                    
                    #Export the file
                    filename = f"MonthlyFixtures{selected_country}-{selected_sport}-{selected_comp}.xlsx"
                    generate_excel_download(monthly_fixtures, filename,"Click Here To Download!")
    
                    
                    #Get Daily Kick off Time Data & Download Excel Link
                    daily_fixtures = get_pct_matches_weekdays(df,weekdays,selected_sport,selected_country,selected_comp)
                    st.dataframe(daily_fixtures)
                    filename = f"DailyFixtures{selected_country}-{selected_sport}-{selected_comp}.xlsx"
                    generate_excel_download(daily_fixtures, filename, "Click Here To Download!")
                    
                    #Get Start Time Data & Download Excel Link
                    start_time_df = get_pct_matches_start_times(df, weekdays, selected_sport,selected_country,selected_comp, threshold=0)
                    st.dataframe(start_time_df)
                    filename = f"StartTimes{selected_country}-{selected_sport}-{selected_comp}.xlsx"
                    generate_excel_download(start_time_df, filename, "Click Here To Download!")
            
            

def report_2_page():
    st.title("Sport Concurrency")
    st.sidebar.image("IGM Primary Inv logotype.png", use_column_width=True)
    with st.sidebar:
        selected_sport = st.selectbox("Select a sport", sportlist)

        month_selections = st.multiselect("Select Months",[i for i in range(1,13,1)])
        
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        day_selection = st.selectbox("Select Day",days_of_week)
        
        

    with st.container():
        time_period = st.slider("Select Time Window:",value=(time(9, 30), time(14, 30)))
        start_time = time_period[0].strftime("%H:%M")
        end_time = time_period[1].strftime("%H:%M")
        
        if selected_sport != "--Please Select--":
            gen = st.button(f"Click Here To Generate Reports For {selected_sport} on a {day_selection} between {start_time} and {end_time}")
            if gen:
                st.write("GENERATING...")
                #Generate My Report 2 Report Here
                start_time_range = pd.Timestamp(start_time).time()
                end_time_range = pd.Timestamp(end_time).time()
                
                filtered_df = df[
                                (df['Sport'] == selected_sport) &
                                (df['StartDateTime'].dt.month.isin(month_selections)) &
                                (df['StartDateTime'].dt.day_name() == day_selection) &
                                (
                                    (df['StartDateTime'].dt.time >= start_time_range) & (df['StartDateTime'].dt.time <= end_time_range) |
                                    (df['EndDateTime'].dt.time >= start_time_range) & (df['EndDateTime'].dt.time <= end_time_range) |
                                    (
                                        (df['StartDateTime'].dt.time <= start_time_range) &
                                        (df['EndDateTime'].dt.time >= end_time_range)
                                    )
                                )
                            ]
                
                # Group by Sport, Country, Competition and calculate the total count of matches
                result_df = filtered_df.groupby(['Sport', 'Country', 'Competition']).size().reset_index(name='TotalMatches')
                
                # Sort the result DataFrame by total count of matches in descending order
                result_df = result_df.sort_values(by='TotalMatches', ascending=False)
                
                #Display the results
                st.dataframe(result_df)
                
                #Include Excel Download Link
                filename = f"ConcurrentCompetitions_{selected_sport}_{day_selection}_{start_time}_to_{end_time}.xlsx"
                generate_excel_download(result_df, filename, "Click Here To Download!")
                
def report_3_page():
    st.title("Perform Operator Views")
    st.sidebar.image("IGM Primary Inv logotype.png", use_column_width=True)
    selected_sport = st.sidebar.selectbox("Select a sport", sportlist)
    selected_comp = "--Please Select--"
    
    #Put logic for Stats Perform report here
    #Make sure to load the Report10 Data!
    df = pd.read_csv("CommercialAppData.csv")
    
    if selected_sport != "--Please Select--":
        complist = sorted(df.loc[df['sport']==selected_sport]['property'].unique())
        complist.insert(0,"--Please Select--")
        selected_comp = st.sidebar.selectbox("Select a Competition",complist)
        
        if selected_comp != "--Please Select--":
            with st.container():
                gen = st.button(f"Click Here to Generate Report For {selected_comp} {selected_sport}")
                
                if gen:
                    st.write("GENERATING...")
                    # Filter the DataFrame based on the specified sport and property
                    _ = df[(df['sport'] == selected_sport) & (df['property'] == selected_comp)]

                    _['average_uniques'] = _['total_uniques'] / _['num_events']
                    
                    #Get Avg Uniques by Operator for this sport:
                    filtered_df = df.loc[df['sport']==selected_sport]
                    
                    avg_by_client = filtered_df.groupby(["client"])[["num_events","total_uniques"]].sum().reset_index()
                    avg_by_client['avg_uniques'] = avg_by_client['total_uniques'] / avg_by_client['num_events']
                    avg_by_client = avg_by_client[['client','avg_uniques']].copy()
                    
                    sport_name_short = selected_sport.replace(" ", "").replace("(", "").replace(")", "")
                    comp_name_short = selected_comp.replace(" ", "").replace("(", "").replace(")", "")
                    
                    avg_by_client.columns = ['client',f"clientAvg{sport_name_short}UniqueUsersPerEvent"]
                    
                    #Merge the two dataframes into one and present
                    result_df = _.merge(avg_by_client,how="left")
                    
                    st.dataframe(result_df)
                    
                    filename = f"AvgClientViews{comp_name_short}_{sport_name_short}.xlsx"
                    generate_excel_download(result_df, filename, "Click Here To Download!")
                    #Filename generating funny - remove competition and make more general
        
        

if __name__ == "__main__":
    home_page()