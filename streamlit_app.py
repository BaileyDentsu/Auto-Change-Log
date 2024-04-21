import streamlit as st
import pandas as pd

def compare_csv(df1, df2, columns_to_compare):
    # Set the URL column as index for easy comparison
    df1.set_index('URL', inplace=True)
    df2.set_index('URL', inplace=True)

    # Identify added, removed, and modified URLs
    added = df2.index.difference(df1.index)
    removed = df1.index.difference(df2.index)
    common = df1.index.intersection(df2.index)

    # Prepare list for data to be collected
    data = []

    # Process added URLs
    for url in added:
        row = df2.loc[url]
        data.append(
            ['Added', url] + ['' for _ in columns_to_compare] + [row.get(col, '') for col in columns_to_compare]
        )

    # Process removed URLs
    for url in removed:
        row = df1.loc[url]
        data.append(
            ['Removed', url] + [row.get(col, '') for col in columns_to_compare] + ['' for _ in columns_to_compare]
        )

    # Process modified URLs
    for url in common:
        row1 = df1.loc[url]
        row2 = df2.loc[url]
        changes = ['Modified', url]
        modified = False  # Flag to track if any changes exist

        for col in columns_to_compare:
            old_val = row1.get(col, '')
            new_val = row2.get(col, '')
            if old_val != new_val:
                changes.extend([old_val, new_val])
                modified = True
            else:
                # Extend with old value and a blank for the new value to preserve column alignment
                changes.extend([old_val, ''])

        if modified:
            data.append(changes)

    # Define the columns for the output DataFrame
    output_columns = ['Added/Removed/Modified', 'URL']
    for col in columns_to_compare:
        output_columns.extend([f'Old {col}', f'New {col}'])

    # Create the output DataFrame from the collected data
    return pd.DataFrame(data, columns=output_columns)

# Streamlit UI setup
st.title('CSV Comparison Tool')

# File uploaders
file1 = st.file_uploader("Choose the first CSV file", type=['csv'])
file2 = st.file_uploader("Choose the second CSV file", type=['csv'])

if file1 and file2:
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    columns = df1.columns.tolist()
    columns.remove('URL')  # Assume 'URL' should not be chosen for comparison
    selected_columns = st.multiselect('Select columns to compare:', options=columns)

    if st.button('Compare Files'):
        if selected_columns:
            result_df = compare_csv(df1, df2, selected_columns)
            st.dataframe(result_df)
            
            # Create a CSV download link
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download output CSV", csv, "changeLog.csv", "text/csv", key='download-csv')
        else:
            st.error("Please select at least one column to compare.")
