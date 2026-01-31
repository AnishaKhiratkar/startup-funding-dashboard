   
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Indian Startup Funding", layout="wide")


df = pd.read_csv("startup_cleaned.csv")

df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

def company_pov(startup):

    st.title(startup)

    data = df[df['startup'] == startup]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Funding", f"{data['amount'].sum()} Cr")
        st.metric("Funding Rounds", data.shape[0])
    with col2:
        st.metric("First Funding Year", int(data['year'].min()))
        st.metric("Last Funding Year", int(data['year'].max()))

    st.subheader("Company Details")
    st.dataframe(
        data[['date','investors','round','vertical','subvertical','city','amount']]
        .sort_values('date', ascending=False)
    )


def investor_pov(investor):

    st.title(investor)

    inv = df[df['investors'].str.contains(investor, na=False)]

    st.subheader("Recent Investments")
    st.dataframe(
        inv.sort_values('date', ascending=False)
        .head(5)[['date','startup','vertical','city','round','amount']]
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Biggest Investments")
        big = inv.groupby('startup')['amount'].sum().sort_values(ascending=False).head(5)
        fig, ax = plt.subplots()
        ax.bar(big.index, big.values)
        ax.set_xticklabels(big.index, rotation=45)
        st.pyplot(fig)
    with col2:
        st.subheader("Sector Preference")
        sector = inv.groupby('vertical')['amount'].sum()
        fig, ax = plt.subplots()
        ax.pie(sector, labels=sector.index, autopct='%0.1f%%')
        st.pyplot(fig)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Stage Preference")
        stage = inv.groupby('round')['amount'].sum()
        fig, ax = plt.subplots()
        ax.pie(stage, labels=stage.index, autopct='%0.1f%%')
        st.pyplot(fig)
    with col4:
        st.subheader("City Preference")
        city = inv.groupby('city')['amount'].sum()
        fig, ax = plt.subplots()
        ax.pie(city, labels=city.index, autopct='%0.1f%%')
        st.pyplot(fig)

    st.subheader("YoY Investment")
    yoy = inv.groupby('year')['amount'].sum()
    fig, ax = plt.subplots()
    ax.plot(yoy.index, yoy.values)
    st.pyplot(fig)

    st.subheader("Similar Investors")
    similar = (
        df[df['startup'].isin(inv['startup'])]
        .assign(investors=lambda x: x['investors'].str.split(','))
        .explode('investors')
        .assign(investors=lambda x: x['investors'].str.strip())
        ['investors']
        .value_counts()
        .drop(investor, errors='ignore')
        .head(5)
    )

    st.dataframe(similar.reset_index().rename(
        columns={'index':'Investor','investors':'Common Startups'}
    ))


def general_analysis():

    st.title("General Startup Analysis")

    
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Funding", f"{df['amount'].sum()} Cr")
    col2.metric("Max Funding", f"{df.groupby('startup')['amount'].max().max()} Cr")
    col3.metric("Avg Ticket Size", f"{round(df.groupby('startup')['amount'].sum().mean())} Cr")
    col4.metric("Funded Startups", df['startup'].nunique())

    
    st.subheader("MoM Analysis")
    choice = st.selectbox("Select", ["Total Funding", "Deal Count"])

    if choice == "Total Funding":
        mom = df.groupby(['year','month'])['amount'].sum().reset_index()
    else:
        mom = df.groupby(['year','month'])['amount'].count().reset_index()

    mom['timeline'] = mom['month'].astype(str) + "-" + mom['year'].astype(str)

    fig, ax = plt.subplots(figsize=(12, 5))   
    ax.plot(mom['timeline'], mom['amount'])
    ax.set_xticks(range(0, len(mom), 3))
    ax.set_xticklabels(mom['timeline'][::3], rotation=45)
    ax.set_xlabel("Month-Year")
    ax.set_ylabel(choice)
    plt.tight_layout()  
    st.pyplot(fig)

    st.subheader("Sector Analysis")
    col1, col2 = st.columns(2)

    with col1:
        sector_count = df.groupby('vertical')['amount'].count().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots()
        ax.pie(sector_count, labels=sector_count.index, autopct='%0.1f%%')
        st.pyplot(fig)

    with col2:
        sector_sum = df.groupby('vertical')['amount'].sum().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots()
        ax.pie(sector_sum, labels=sector_sum.index, autopct='%0.1f%%')
        st.pyplot(fig)

    
    st.subheader("City-wise Funding")
    city = df.groupby('city')['amount'].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots()
    ax.bar(city.index, city.values)
    ax.set_xticklabels(city.index, rotation=45)
    st.pyplot(fig)

    
    st.subheader("Top Funded Startups")
    top_startups = df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)
    st.dataframe(top_startups.reset_index())

    
    st.subheader("Top Investors")
    investors = df['investors'].dropna().str.split(',').explode().value_counts().head(10)
    st.dataframe(investors.reset_index().rename(columns={'index':'Investor','investors':'Deals'}))










st.sidebar.title("Startup Funding Dashboard")

option = st.sidebar.selectbox(
    "Select View",
    ["General Analysis", "Company POV", "Investor POV"]
)

if option == "General Analysis":
    general_analysis()

elif option == "Company POV":
    startup = st.sidebar.selectbox("Select Startup", sorted(df['startup'].unique()))
    if st.sidebar.button("Show Company"):
        company_pov(startup)

else:
    investor_list = sorted(set(df['investors'].dropna().str.split(',').sum()))
    investor = st.sidebar.selectbox("Select Investor", investor_list)
    if st.sidebar.button("Show Investor"):
        investor_pov(investor)
