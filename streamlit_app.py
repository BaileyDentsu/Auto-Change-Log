import streamlit as st
import pandas as pd

def compare_csv(df1, df2, columns_to_compare):
    # Setting 'Address' as index for comparison
    df1.set_index('Address', inplace=True)
    df2.set_index('Address', inplace=True)

    added = df2.index.difference(df1.index)
    removed = df1.index.difference(df2.index)
    common = df1.index.intersection(df2.index)

    data = []

    # Added URLs
    for Address in added:
        row = df2.loc[Address]
        # Append blank 'Old' values and current 'New' values for each column to compare
        data.append(['Added', Address] + [item for col in columns_to_compare for item in ('', row.get(col, ''))])

    # Removed URLs
    for Address in removed:
        row = df1.loc[Address]
        # Append current 'Old' values and blank 'New' values for each column to compare
        data.append(['Removed', Address] + [item for col in columns_to_compare for item in (row.get(col, ''), '')])

    # Modified URLs
    for Address in common:
        row1 = df1.loc[Address]
        row2 = df2.loc[Address]
        changes = ['Modified', Address]
        row_entries = []
        modified = False  # Reset flag for each URL

        for col in columns_to_compare:
            old_val = row1.get(col, '')
            new_val = row2.get(col, '')
            row_entries.append(old_val)
            if old_val != new_val:
                row_entries.append(new_val)
                modified = True
            else:
                row_entries.append('')  # Append blank for unchanged 'New' values

        if modified:
            changes.extend(row_entries)
            data.append(changes)

    # Constructing output DataFrame headers
    output_columns = ['Added/Removed/Modified', 'Address']
    for col in columns_to_compare:
        output_columns.extend([f'Old {col}', f'New {col}'])

    # Creating DataFrame from the collected data
    return pd.DataFrame(data, columns=output_columns)

st.title('CSV Comparison Tool')

# File uploaders
file1 = st.file_uploader("Choose the first CSV file", type=['csv'])
file2 = st.file_uploader("Choose the second CSV file", type=['csv'])

if file1 and file2:
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    columns = df1.columns.tolist()
    columns.remove('Address')  # Assuming 'Address' should not be compared
    selected_columns = st.multiselect('Select columns to compare:', options=columns)

    if st.button('Compare Files'):
        if selected_columns:
            result_df = compare_csv(df1, df2, selected_columns)
            st.dataframe(result_df)
            
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download output CSV", csv, "changeLog.csv", "text/csv", key='download-csv')
        else:
            st.error("Please select at least one column to compare.")
