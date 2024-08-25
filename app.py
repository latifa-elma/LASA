import streamlit as st
import os
import subprocess
from datetime import datetime
import requests
import pytz
import pandas as pd

# URL of the API to get the current time
time_api_url = "http://worldtimeapi.org/api/timezone/Etc/UTC"

def get_current_time():
    try:
        response = requests.get(time_api_url)
        response.raise_for_status()  # Check if the request was successful
        current_time_data = response.json()
        return datetime.fromisoformat(current_time_data["datetime"]).replace(tzinfo=pytz.UTC)
    except requests.exceptions.RequestException as e:
        st.warning(f"Error fetching time: {e}. Using local system time.")
        return datetime.now(pytz.UTC)

# Streamlit app setup
st.title("YMM-LASA for Automated Integration")

# Fetch the current date
current_date = get_current_time()
expiration_date = datetime(2024, 9, 10, 14, 0, tzinfo=pytz.UTC)

if current_date > expiration_date:
    st.error("Thank you for your visit.")
else:
    st.success("Welcome to the application!")

    # Create the uploads directory if it doesn't exist
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    # PART 1: Separation

    st.header("Separation")

    # Section to upload the MMSTA file
    uploaded_mmsta_file = st.file_uploader("Upload your MMSTA file", type=["csv", "xlsx"])

    # Button to apply separation
    if st.button("Separate"):
        if uploaded_mmsta_file:
            mmsta_filepath = os.path.join(uploads_dir, uploaded_mmsta_file.name)
            with open(mmsta_filepath, "wb") as f:
                f.write(uploaded_mmsta_file.getbuffer())

            # Call the separation script
            result = subprocess.run(["python", "separation.py", mmsta_filepath], capture_output=True, text=True)
            if result.returncode != 0:
                st.error(f"Error during separation: {result.stderr}")
            else:
                output_filename = "MMSTA_separe.xlsx"
                if os.path.exists(output_filename):
                    with open(output_filename, 'rb') as generated_file:
                        st.download_button(
                            label="Download the separated Excel file",
                            data=generated_file,
                            file_name=output_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    st.success("Separation completed successfully!")
                else:
                    st.error("Error generating the Excel file.")
        else:
            st.error("Please upload the MMSTA file.")

    # PART 2: Integration

    st.header("Integration")

    # Section to upload the MMSTA_separe file
    uploaded_mmsta_separe_file = st.file_uploader("Upload the separated MMSTA file (MMSTA_separe.xlsx)", type=["xlsx"])

    # Section to upload the Circuit List file
    uploaded_circuit_file = st.file_uploader("Upload your Circuit List file", type=["csv", "xlsx"])

    # Button to apply integration
    if st.button("Integrate"):
        if uploaded_mmsta_separe_file and uploaded_circuit_file:
            mmsta_separe_filepath = os.path.join(uploads_dir, uploaded_mmsta_separe_file.name)
            with open(mmsta_separe_filepath, "wb") as f:
                f.write(uploaded_mmsta_separe_file.getbuffer())
            
            circuit_filepath = os.path.join(uploads_dir, uploaded_circuit_file.name)
            with open(circuit_filepath, "wb") as f:
                f.write(uploaded_circuit_file.getbuffer())

            # Call the integration script
            result = subprocess.run(["python", "integration.py", mmsta_separe_filepath, circuit_filepath], capture_output=True, text=True)
            if result.returncode != 0:
                st.error(f"Error during integration: {result.stderr}")
            else:
                output_filename = "liste_circuit_integre.xlsx"
                if os.path.exists(output_filename):
                    with open(output_filename, 'rb') as integration_file:
                        st.download_button(
                            label="Download the integrated Excel file",
                            data=integration_file,
                            file_name=output_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    st.success("Integration completed successfully!")
                else:
                    st.error("Error generating the integrated Excel file.")
        else:
            st.error("Please upload both the separated MMSTA file and the Circuit List.")

    # Add the names of the developers at the bottom-left corner
    st.markdown("""
        <div style='position: fixed; bottom: 0; left: 0; padding: 10px;'>
            <p>Developed by <strong>EL MALIANI LATIFA</strong> and <strong>EL BINANI SALMA</strong></p>
        </div>
        """, unsafe_allow_html=True)
