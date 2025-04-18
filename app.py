
import streamlit as st
import pandas as pd
import re
from sqlalchemy import create_engine

# Set page config at the very top!
st.set_page_config(page_title="Upload Ad Datasets", layout="wide")

engine = create_engine("mysql+mysqlconnector://root:aMUNkthGiGHHDwRptYkiECXkZgJArEnT@yamabiko.proxy.rlwy.net:44665/railway")


st.title("Mobility Dashboard")
st.markdown("Upload your CSV or Excel datasets for each platform below. Unwanted columns will be removed automatically. Use 'Transform Columns' to clean names before saving to MySQL.")

# Store uploaded DataFrames
uploaded_dataframes = {}

# Columns to remove per platform
columns_to_remove = {
    "amazon_ads_sd": [
        'Ad Group Name', 'Bid Optimisation', 'Viewable Impressions',
        'Clicks', 'Click-Thru Rate (CTR)', '14 Day Detail Page Views (DPV)', 
        'Cost Per Click (CPC)', 'Cost per 1,000 viewable impressions (VCPM)', 
        'Total Advertising Cost of Sales (ACOS)', 'Total Return on Advertising Spend (ROAS)',
        '14 Day New-to-brand Orders (#)', '14 Day New-to-brand Sales (₹)', 
        '14 Day New-to-brand Units (#)', 'Total Advertising Cost of Sales (ACOS) – (Click)', 
        'Total Return on Advertising Spend (ROAS) – (Click)', '14 Day Total Orders (#) – (Click)',
        '14 Day Total Units (#) – (Click)', '14 Day New-to-brand Orders (#) – (Click)', 
        '14 Day New-to-brand Sales - (Click)', '14 Day New-to-brand Units (#) – (Click)', 
        '14 Day Total Sales – (Click)'
    ],
    "amazon_ads_sb": [
        'Click-Thru Rate (CTR)', 'Cost Per Click (CPC)', 'Clicks', 
        'Total Advertising Cost of Sales (ACOS)', 'Total Return on Advertising Spend (ROAS)',
        '14 Day Conversion Rate', 'Viewable Impressions', 'Cost per 1,000 viewable impressions (VCPM)',
        'View-Through Rate (VTR)', 'Click-Through Rate for Views (vCTR)', 'Video First Quartile Views',
        'Video Midpoint Views', 'Video Third Quartile Views', 'Video Complete Views', 'Video Unmutes',
        '5 Second Views', '5 Second View Rate', '14 Day Branded Searches', 
        '14 Day Detail Page Views (DPV)', '14 Day New-to-brand Orders (#)', 
        '14 Day % of Orders New-to-brand', '14 Day New-to-brand Sales (₹)', 
        '14 Day % of Sales New-to-brand', '14 Day New-to-brand Units (#)', 
        '14 Day % of Units New-to-brand', '14 Day New-to-brand Order Rate', 
        'Total Advertising Cost of Sales (ACOS) – (Click)', 
        'Total Return on Advertising Spend (ROAS) – (Click)', '14 Day Total Sales – (Click)', 
        '14 Day Total Orders (#) – (Click)', '14 Day Total Units (#) – (Click)', 
        'New-to-brand detail page views', 'New-to-brand detail page view click-through conversions',
        'New-to-brand detail page view rate', 'Effective cost per new-to-brand detail page view',
        '14 Day ATC', '14 Day ATC Clicks', '14 Day ATCR', 
        'Effective cost per Add to Cart (eCPATC)', 'Branded Searches click-through conversions',
        'Branded Searches Rate', 'Effective cost per Branded Search', 
        'Long-Term Sales', 'Long-Term ROAS'
    ],
    "amazon_ads_sp": [
        'Currency', 'Impressions', 'Clicks', 'Click-Thru Rate (CTR)', 
        'Cost Per Click (CPC)', 'Total Advertising Cost of Sales (ACOS)', 
        'Total Return on Advertising Spend (ROAS)', '14 Day Conversion Rate'
    ],
    "amazon_returns": [
        'SafeT claim reimbursement amount', 'SafeT claim state', 'SafeT claim id', 
        'SafeT Action reason', 'SafeT claim creation time', 'Resolution', 'In policy', 
        'Is prime', 'A-to-Z Claim', 'Label to be paid by', 'Return carrier', 'Currency code', 
        'Label type', 'Label cost', 'Merchant RMA ID', 'Amazon RMA ID'
    ],
    "amazon_sales": [
        'merchant-order-id', 'sales-channel', 'order-channel', 'url', 'ship-service-level', 
        'item-status', 'number-of-items', 'gift-wrap-price', 'gift-wrap-tax', 
        'item-extensions-data', 'promotion-ids', 'is-business-order', 
        'purchase-order-number', 'price-designation', 'fulfilled-by', 'buyer-company-name', 
        'buyer-cst-number', 'buyer-vat-number', 'buyer-tax-registration-id', 
        'buyer-tax-registration-country', 'buyer-tax-registration-type', 
        'customized-url', 'customized-page', 'is-heavy-or-bulky', 
        'vat-exclusive-item-price', 'vat-exclusive-shipping-price', 
        'vat-exclusive-giftwrap-price', 'is-iba', 'is-transparency', 
        'store-chain-store-id', 'serial-numbers', 'amazon-programs'
    ],
    "facebook_ads": [
        'Gender', 'Objective', 'Delivery status', 'Delivery level', 'Reach', 
        'Impressions', 'Frequency', 'Attribution setting', 'Result Type', 'Results', 'Age'
    ],
    "google_ads": [
        'Conversions', 'Conv. value', 'Currency code'
    ],
    "shopify": [
        'Email', 'Accepts Marketing', 'Currency', 'Discount Code', 'Discount Amount', 'Lineitem compare at price', 
        'Lineitem requires shipping', 'Lineitem taxable', 'Lineitem fulfillment status', 'Billing Name', 
        'Billing Street', 'Billing Address1', 'Billing Address2', 'Billing Company', 'Billing Zip', 'Billing Province', 
        'Billing Phone', 'Shipping Name', 'Shipping Street', 'Shipping Address1', 'Shipping Address2', 'Shipping Zip', 
        'Shipping Province', 'Shipping Phone', 'Notes', 'Note Attributes', 'Payment Reference', 'Payment Method', 
        'Vendor', 'Location', 'Device ID', 'Tags', 'Risk Level', 'Source', 'Lineitem discount', 'Tax 1 Name', 
        'Tax 1 Value', 'Tax 2 Name', 'Tax 2 Value', 'Tax 3 Name', 'Tax 3 Value', 'Tax 4 Name', 'Tax 4 Value', 
        'Tax 5 Name', 'Tax 5 Value', 'Phone', 'Receipt Number', 'Duties', 'Billing Province Name', 
        'Shipping Province Name', 'Payment ID', 'Id', 'Payment References', 'Next Payment Due At', 'Payment Terms Name', 
        'Employee'
    ]
}

def clean_column_name(col):
    col = col.strip().lower()
    col = re.sub(r'[^\w\s]', '', col)
    col = re.sub(r'\s+', '_', col)
    col = re.sub(r'_+', '_', col)
    col = col.strip('_')
    return col

def read_uploaded_file(uploaded_file):
    return pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

def upload_and_clean(name, label):
    with st.expander(f"📁 Upload: {label}"):
        uploaded_file = st.file_uploader(f"Upload `{label}` (.csv or .xlsx)", type=["csv", "xlsx"], key=name)
        if uploaded_file:
            df = read_uploaded_file(uploaded_file)
            to_remove = columns_to_remove.get(name.lower(), [])
            df = df.drop(columns=[col for col in to_remove if col in df.columns], errors='ignore')
            uploaded_dataframes[name.lower()] = df
            st.info(f"Removed unwanted columns from `{label}`")
            st.dataframe(df.head(10))

# Upload sections
st.header("📦 Amazon Data Uploads")
for key in ["amazon_ads_sb", "amazon_ads_sd", "amazon_ads_sp", "amazon_returns", "amazon_sales"]:
    upload_and_clean(key, key.replace("_", " ").title())

st.header("📘 Facebook Ads")
upload_and_clean("facebook_ads", "Facebook Ads")

st.header("🔍 Google Ads")
upload_and_clean("google_ads", "Google Ads")

st.header("🛍️ Shopify")
upload_and_clean("shopify", "Shopify")

# Transform all column names
if st.button("🔁 Transform All Column Names"):
    for name in uploaded_dataframes:
        df = uploaded_dataframes[name]
        df.columns = [clean_column_name(col) for col in df.columns]
        uploaded_dataframes[name] = df
    st.success("✅ Column names cleaned!")

    for name, df in uploaded_dataframes.items():
        with st.expander(f"🔍 Preview Transformed `{name}`"):
            st.dataframe(df.head(10))

# Save to MySQL
if st.button("🚀 Save to MySQL"):
    if uploaded_dataframes:
        for name, df in uploaded_dataframes.items():
            # ✅ Ensure column names are cleaned even if 'Transform' wasn't clicked
            df.columns = [clean_column_name(col) for col in df.columns]

            try:
                df.to_sql(name=name.lower(), con=engine, if_exists="replace", index=False)
                st.success(f"✅ Saved `{name}` to MySQL")
            except Exception as e:
                st.error(f"❌ Error saving `{name}`: {e}")
    else:
        st.warning("⚠️ Upload and transform datasets first.")
