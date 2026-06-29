#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np


# In[3]:


import os

print(os.getcwd())


# In[4]:


import os

os.listdir()


# In[5]:


import os

os.listdir(r"C:\Users\DOBUY GADGETS\Documents\US export Project")


# In[6]:


import os

os.listdir(r"C:\Users\DOBUY GADGETS\Documents\US export Project\Data")


# In[7]:


df = pd.read_csv(
    r"C:\Users\DOBUY GADGETS\Documents\US export Project\Data\Data.Gov-FY25Q44.csv",
    sep=";",
    encoding="utf-8-sig",
    low_memory=False
)
#so the dataset was improperly separated, therefore used the sep= function to separate it so it can load seamlessly into notebook.


# In[8]:


df.head()


# In[9]:


df.shape


# In[10]:


df.info()


# In[11]:


df.isnull().sum()


# In[12]:


df.duplicated().sum()


# In[13]:


df.columns.tolist()


# In[14]:


# Lets correct the date time columns
date_cols = [
    'Decision Date',
    'Effective Date',
    'Expiration Date'
]

for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')


# In[15]:


df[date_cols].dtypes


# In[16]:


# Lets clean the column names to avoid problems later.
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(' ', '_')
    .str.replace('/', '_')
    .str.replace('(', '', regex=False)
    .str.replace(')', '', regex=False)
)


# In[17]:


### Lets drp some columns with a lot of missing values. About 99.9% of missing values.
df.drop(
    columns=[
        'loan_interest_rate',
        'multiyear_working_capital_extension'
    ],
    inplace=True
)


# In[18]:


missing_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)

missing_pct
#lets check missing values of columns by percentage


# In[19]:


df.drop(
    columns=['working_capital_delegated_authority'],
    inplace=True
)
#dropping the one with the hightest percentage of missings values, it has only 12% remaining so it wont be useful during eda


# In[20]:


#Lets investigage primary lender with almost half of its values missing
df['primary_lender'].value_counts().head(20)


# In[21]:


# we notice a lo tof inconsistencies in the lender names so lets clean that
df['primary_lender'] = (
    df['primary_lender']
    .str.upper()
    .str.strip()
)


# In[22]:


df['primary_lender'].value_counts().head(20)


# In[23]:


# Now everything seems organized


# In[24]:


#lets check our yes and no columns and our decision too
df['brokered'].value_counts(dropna=False)


# In[25]:


df['deal_cancelled'].value_counts(dropna=False)


# In[26]:


df['decision'].value_counts(dropna=False)


# In[27]:


#Lets look at fo rthe money columns
df[
    [
        'approved_declined_amount',
        'disbursed_shipped_amount',
        'outstanding_exposure_amount'
    ]
].describe()


# In[28]:


df['program'].value_counts()


# In[29]:


# Before i decide to drop the deciion column, lets investigate the declined records
df[df['decision'] == 'Declined']


# In[30]:


# Not dropping the decision column , because even though it has very little comparitive ability, the declined records are meaningful 
# Also I dont want to create a new dataset lol. 


# In[31]:


(df == 'N/A').sum().sort_values(ascending=False).head(20)


# In[32]:


(df == 'N/A').sum()


# In[33]:


#Lets check for columns containing the most zeros
(df == 0).sum().sort_values(ascending=False)


# In[34]:


money_cols = [
    'approved_declined_amount',
    'disbursed_shipped_amount',
    'undisbursed_exposure_amount',
    'outstanding_exposure_amount',
    'small_business_authorized_amount',
    'woman_owned_authorized_amount',
    'minority_owned_authorized_amount'
]

for col in money_cols:
    print(col)
    print((df[col] == 0).mean() * 100)
    print()

    #Lets cal the % of 0's


# In[35]:


#Note the 0's are not missing values


# ### EXPLORATORY DATA ANALYSIS

# In[36]:


# Who receives U.S. export credit support?
# We have to understand who are receiving US credit support in order to reveal the types of businesses that benefit most from export financing programs.
# Primary exporter shows the companies that export primarily outside of the US and it tell you where its being exporting to.
# Note that; U.S. export credit support is financial help that allows U.S. companies to sell their products to buyers in other countries.
#so primary exporters are the ones receiving this support in order to export successfully. 

top_exporters_amount = (
    df.groupby('primary_exporter')['approved_declined_amount']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

top_exporters_amount


# In[ ]:





# In[37]:


import matplotlib.pyplot as plt
plt.figure(figsize=(10,5))

top_exporters_amount.plot(kind='bar')

plt.title('Top 10 Exporters Receiving U.S. Export Credit Support')
plt.xlabel('Exporter')
plt.ylabel('Number of Deals')

plt.xticks(rotation=45, ha='right')
plt.show()


# In[38]:


# To find the industries that performs the most shows which exporter benefits on the US credit the most
# Obviously there is no inductry column so we create an industry column from product description
# Product decription has a lot of industries in it sowe use that
df['product_description'].nunique()
df['product_description'].value_counts().head(30)


# # I grouped these product services into different industries 
# #### Industrial Manufacturing
# #### Agriculture
# #### Healthcare
# #### Technology
# #### Construction
# #### Energy
# #### Food & Consumer Goods
# #### Chemicals & Materials
# #### Transportation
# #### Automotive
# #### Aerospace & Defense
# #### Building Materials
# #### Professional Services
# #### Consumer Goods

# In[ ]:





# In[43]:


# df['industry'] = df['product_description'].map(industry_map)


# In[ ]:


df['product_description'].nunique()


# In[ ]:


products = pd.DataFrame(
    df['product_description']
    .dropna()
    .unique(),
    columns=['product_description']
)

products.head()


# In[ ]:


industry_lookup = pd.DataFrame({
    'product_description': [
        'Aircraft Manufacturing',
        'Farm Machinery and Equipment Manufacturing',
        'Construction Machinery Manufacturing'
    ],
    'industry': [
        'Aerospace & Defense',
        'Agriculture',
        'Construction'
    ]
})


# In[ ]:


df = df.merge(
    industry_lookup,
    on='product_description',
    how='left'
)


# In[ ]:


df['industry'].isna().sum()


# In[ ]:


df.shape


# In[44]:


# Lets create a new column  called industry with the respective industries
industry_map = {
    'Aircraft Manufacturing': 'Aerospace & Defense',

    'Lumber, Plywood, Millwork, and Wood Panel Merchant Wholesalers': 'Building Materials',

    'Transportation Equipment and Supplies (except Motor Vehicle) Merchant Whole': 'Transportation',

    'Industrial Machinery and Equipment Merchant Wholesalers': 'Industrial Manufacturing',

    'All Other Miscellaneous Manufacturing': 'Industrial Manufacturing',

    'All Other Plastics Product Manufacturing': 'Chemicals & Materials',

    'Farm Machinery and Equipment Manufacturing': 'Agriculture',

    'Other Chemical and Allied Products Merchant Wholesalers': 'Chemicals & Materials',

    'Medical, Dental, and Hospital Equipment and Supplies Merchant Wholesalers': 'Healthcare',

    "Drugs and Druggists' Sundries Merchant Wholesalers": 'Healthcare',

    'All Other Miscellaneous Chemical Product and Preparation Manufacturing': 'Chemicals & Materials',

    'Construction Machinery Manufacturing': 'Construction',

    'General Line Grocery Merchant Wholesalers': 'Food & Consumer Goods',

    'Toilet Preparation Manufacturing': 'Healthcare',

    'All Other Miscellaneous General Purpose Machinery Manufacturing': 'Industrial Manufacturing',

    'Other Miscellaneous Durable Goods Merchant Wholesalers': 'Consumer Goods',

    'Industrial Supplies Merchant Wholesalers': 'Industrial Manufacturing',

    'Construction and Mining (except Oil Well) Machinery and Equipment Merchant': 'Construction',

    'Other Grocery and Related Products Merchant Wholesalers': 'Food & Consumer Goods',

    'Surgical and Medical Instrument Manufacturing': 'Healthcare',

    'Meat and Meat Product Merchant Wholesalers': 'Food & Consumer Goods',

    'Farm Supplies Merchant Wholesalers': 'Agriculture',

    'Instruments and Related Products Manufacturing for Measuring, Displaying, a': 'Technology',

    'Other Measuring and Controlling Device Manufacturing': 'Technology',

    'Motor Vehicle Supplies and New Parts Merchant Wholesalers': 'Automotive',

    'Grain and Field Bean Merchant Wholesalers': 'Agriculture',

    'Engineering Services': 'Professional Services',

    'Oil and Gas Field Machinery and Equipment Manufacturing': 'Energy',

    'Other Miscellaneous Nondurable Goods Merchant Wholesalers': 'Consumer Goods',

    'Analytical Laboratory Instrument Manufacturing': 'Technology'
}


# In[45]:


df['industry'] = df['product_description'].map(industry_map)


# In[46]:


df['industry'].isna().sum()


# In[47]:


df.head()


# In[ ]:


df.drop(
    columns=['industry_x'],
    inplace=True
)


# In[ ]:


df.drop(
    columns=['industry_y'],
    inplace=True
)


# In[ ]:


df.head()


# In[ ]:


# An industry column was created from product descriptions by grouping common product categories into broader industry sectors.
# Records that could not be confidently classified were left as missing
df.groupby('industry')['approved_declined_amount'].sum().sort_values(ascending=False)


# ### Question 2. For the industries that receive the most US EXPORT CREDIT support, we will be going with Aerospace and defence.

# In[ ]:


import matplotlib.pyplot as plt

industry_support = (
    df.groupby('industry')['approved_declined_amount']
    .sum()
    .sort_values() / 1e9
)

plt.figure(figsize=(10,6))

industry_support.plot(kind='barh')

plt.title('U.S. Export Credit Support by Industry')
plt.xlabel('Approved Financing Amount (Billions USD)')
plt.ylabel('Industry')

plt.tight_layout()
plt.show()


# In[ ]:


# lets Identify the areas that receive the greatest share of export financing.
state_support = (
    df.groupby('primary_exporter_state_name')['approved_declined_amount']
    .sum()
    .sort_values(ascending=False)
)

state_support.head(10)


# ### Since washington is the region with the greatest share of financing, lets find out what exporter is increasing washingtons numbers
# 

# In[ ]:


df[df['primary_exporter_state_name'] == 'Washington'] \
    .groupby('primary_exporter')['approved_declined_amount'] \
    .sum() \
    .sort_values(ascending=False) \
    .head(10)


# In[ ]:


import matplotlib.pyplot as plt

top_states = (
    df.groupby('primary_exporter_state_name')['approved_declined_amount']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(10,6))

top_states.sort_values().plot(kind='barh')

plt.title('Top U.S. States Receiving Export Financing Support')
plt.xlabel('Approved Financing Amount ($)')
plt.ylabel('State')

plt.tight_layout()
plt.show()


# In[ ]:


#what countries receive the 
country_support = (
    df.groupby('country')['approved_declined_amount']
    .sum()
    .sort_values(ascending=False)
)

country_support.head(10)


# In[ ]:


# Are approvals concentrated among a small number of companies? Lets check the primary exporter(companies) and approvals/financinf (approved declined amt)
exporter_support = (
    df.groupby('primary_exporter')['approved_declined_amount']
    .sum()
    .sort_values(ascending=False)
)

exporter_support.head(10)


# In[ ]:


# How does export financing contribute to U.S. international trade?
# Lets find our export financing helps U.S. companies sell products to buyers in other countries
# Columns used are country to find out what countries are receiving, approved declined amt to show much much the finances was approved 
# and finally the disbursed, how much was successfully shipped.

# Before confirming, i had primary exporter in place of approved... because my thought process was based on companies exporting but thats not correct

#LEts begin checking the total approved and successfully disbursed.


# In[ ]:


df['approved_declined_amount'].sum()


# In[ ]:


df['disbursed_shipped_amount'].sum()


# In[ ]:


# % 
(
    df['disbursed_shipped_amount'].sum() /
    df['approved_declined_amount'].sum()
) * 100


# In[ ]:


df.groupby('country')['disbursed_shipped_amount'] \
  .sum() \
  .sort_values(ascending=False) \
  .head(10)


# In[ ]:


df.groupby('disbursed_shipped_amount')['approved_declined_amount] \
  .sum() \
  .sort_values(ascending=False) \
  .head(10)


# In[ ]:


# How has the total value of U.S. export credit approvals changed over time?
# For approvals, Obviosly approved declined amt and fiscal year for time change (annually)
yearly_approvals = (
    df.groupby('fiscal_year')['approved_declined_amount']
    .sum()
    .sort_values()
)

yearly_approvals


# In[ ]:


import matplotlib.pyplot as plt

yearly_approvals = (
    df.groupby('fiscal_year')['approved_declined_amount']
    .sum() / 1e9
)

plt.figure(figsize=(10,5))

yearly_approvals.plot(kind='line', marker='o')

plt.title('U.S. Export Credit Approvals Over Time')
plt.xlabel('Fiscal Year')
plt.ylabel('Approved Amount (Billions USD)')

plt.grid(True)
plt.show()


# In[ ]:


# What percentage of approved financing is actually disbursed?

disbursement_rate = (
    df['disbursed_shipped_amount'].sum() /
    df['approved_declined_amount'].sum()
) * 100

disbursement_rate
# For every $100 approved in export financing, about $84.50 was actually used for export transactions.


# In[ ]:


Lets check which groups are higher than others
df.groupby('program')[['approved_declined_amount','disbursed_shipped_amount']].sum()


# In[ ]:


# Which export credit programs convert approved financing into actual exports most successfully?
# Working Capital programs had the highest rate of converting approved funds to actual use, while Loans had the lowest.
program_disbursement = (
    df.groupby('program')[['approved_declined_amount', 'disbursed_shipped_amount']]
    .sum()
)

program_disbursement['disbursement_rate'] = (
    program_disbursement['disbursed_shipped_amount'] /
    program_disbursement['approved_declined_amount']
) * 100

program_disbursement.sort_values('disbursement_rate', ascending=False)


# In[ ]:


# What are the most common reasons for deal cancellations?

# Fist how many deals were cancelled
df['deal_cancelled'].value_counts()


# In[ ]:


# lets check patterns
# How many programs were cancelled
df[df['deal_cancelled'] == 'Yes']['program'].value_counts()


# In[ ]:


# How many countries were cancelled
df[df['deal_cancelled'] == 'Yes']['country'].value_counts().head(10)


# In[ ]:


#Which exporters have the most cancellations
df[df['deal_cancelled'] == 'Yes']['primary_exporter'].value_counts().head(10)


# In[ ]:


# From further observations, lets check why loan is the lowest and if countries and loan correlates
loan_countries = (
    df[df['program'] == 'Loan']
    .groupby('country')['approved_declined_amount']
    .sum()
    .sort_values(ascending=False)
)

loan_countries.head(10)


# In[ ]:


#Loan has nothing to do with countries
# Lets investigate and check the characteristics of canceled deals 
cancelled_deals = df[df['deal_cancelled'] == 'Yes']

cancelled_deals.shape


# In[ ]:


# Lets find out why insurance deals are the highest cancelled rate
insurance_cancelled = df[
    (df['program'] == 'Insurance') &
    (df['deal_cancelled'] == 'Yes')
]

insurance_cancelled.shape


# In[ ]:


cancelled_deals['program'].value_counts()


# In[ ]:


# countries with cancelled deals
cancelled_deals['country'].value_counts().head(10)


# In[ ]:


#were cancelled deals usually large or small
cancelled_deals['approved_declined_amount'].describe()


# In[ ]:


cancelled_deals['primary_exporter'].value_counts().head(10)


# In[ ]:


df.groupby('deal_cancelled')['approved_declined_amount'].sum()


# ### Insurance and Guarantee programs drove most cancellations, largely in multi-country deals, with Mexico leading single-country cancellations.
# ### Despite an average cancelled deal value of several million dollars, the median was zero — meaning many cancelled deals had little to no financing ### recorded.
# ### There is no exact reason for cancelled deals 

# In[ ]:


approval_rate = (
    df.groupby('brokered')['decision']
    .value_counts(normalize=True)
    .mul(100)
)

approval_rate


# ### Brokered deals had a slightly higher approval rate than direct applications, but since both groups were already approved at very high rates, brokers made little practical difference to outcomes.

# In[ ]:


df.to_csv("cleaned_us_export_data.csv", index=False)


# In[ ]:


df.to_csv(
    r"C:\Users\DOBUY GADGETS\Downloads\cleaned_us_export_data.csv",
    index=False,
    encoding="utf-8-sig"
)


# In[ ]:


import os

os.listdir()


# In[ ]:


import os

print(os.path.abspath("cleaned_us_export_data.csv"))


# In[48]:


df.head()


# In[49]:


df.to_csv("cleaned_us_export_data.csv", index=False)


# In[50]:


df.to_csv(
    r"C:\Users\DOBUY GADGETS\Downloads\cleaned_us_export_data.csv",
    index=False,
    encoding="utf-8-sig"
)


# In[51]:


import os

os.listdir()


# In[52]:


import os

print(os.path.abspath("cleaned_us_export_data.csv"))


# In[ ]:




