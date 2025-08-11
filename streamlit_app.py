import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def process_scan_data(df, start_time_str):
    """Process the scan data and return the pivot table."""
    df['Last Updated Time'] = pd.to_datetime(df['Last Updated Time'])
    scan_date = df['Last Updated Time'].dt.date.min()
    start_datetime = datetime.combine(scan_date, datetime.strptime(start_time_str, "%H:%M").time())
    end_datetime = df['Last Updated Time'].max()
    time_bins = []
    labels = []
    current_time = start_datetime
    
    while current_time < end_datetime + timedelta(minutes=30):
        next_time = current_time + timedelta(minutes=30)
        time_bins.append((current_time, next_time))
        labels.append(f"{current_time.strftime('%H:%M')}-{next_time.strftime('%H:%M')}")
        current_time = next_time
        
    def assign_slot(ts):
        for label, (start, end) in zip(labels, time_bins):
            if start <= ts < end:
                return label
        return None

    df['Time Slot'] = df['Last Updated Time'].apply(assign_slot)
    pivot_df = df.groupby(['Last Scan By', 'Time Slot']).size().unstack(fill_value=0)
    actual_time_slots = sorted([col for col in pivot_df.columns if col in labels])
    pivot_df = pivot_df[actual_time_slots]
    pivot_df.insert(len(actual_time_slots), 'Grand Total', pivot_df.sum(axis=1))
    
    return pivot_df  # Added this return statement

st.set_page_config(page_title="Scan Data Analysis", layout="wide")
st.title("Scan Rate Analysis")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
start_time = st.time_input("Select Start Time", value=datetime.strptime("16:30", "%H:%M").time())

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if 'Last Updated Time' not in df.columns or 'Last Scan By' not in df.columns:
        st.error("CSV must contain 'Last Updated Time' and 'Last Scan By' columns.")
    else:
        pivot_df = process_scan_data(df, start_time.strftime("%H:%M"))

        st.subheader("Processed Data")
        st.dataframe(pivot_df, use_container_width=True)
        csv_data = pivot_df.to_csv().encode("utf-8")
        st.download_button(" Download CSV", data=csv_data, file_name="scan_results.csv", mime="text/csv")
else:
    st.info("Please upload a CSV file to begin.")
