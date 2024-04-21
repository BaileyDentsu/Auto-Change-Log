
import streamlit as st
import pandas as pd

def compare_csv(df1, df2, selected_columns):
    # Set the URL column as index for easy comparison
    df1.set_index('URL', inplace=True)
    df2.set_index('URL', inplace=True)

    # Identify added, removed, and modified URLs
    added = df2.index.difference(df1.index)
    removed = df1.index.difference(df2.index)
    common = df1.index.intersection(df2.index)

    data = []

    # Process added URLs
    for url in added:
        row = df2.loc[url]
        data.append(['Added', url] + ['' if col not in selected_columns else row.get(col, '') for col in selected_columns])

    # Process removed URLs
    for url in removed:
        row = df1.loc[url]
        data.append(['Removed', url] + [row.get(col, '') if col in selected_columns else '' for col in selected_columns])

    # Process modified URLs
    for url in common:
        row1 = df1.loc[url]
        row2 = df2.loc[url]
        row_data = ['Modified', url]
        modified = False
        for col in selected_columns:
            old_val = row1.get(col, '')
            new_val = row2.get(col, '')
            if old_val != new_val:
                row_data.extend([old_val, new_val])
                modified = True
            else:
                row_data.extend([old_val, ''])
        if modified:
            data.append(row_data)

    # Create the output DataFrame
    headers = ['Added/Removed/Modified', 'URL'] + [f'Old {col}' for col in selected_columns] + [f'New {col}' for col in selected_columns]
    output_df = pd.DataFrame(data, columns=headers)
    return output_df

# Streamlit UI components
st.title('CSV Comparison Tool')

# File uploaders
file1 = st.file_uploader("Choose the first CSV file", type=['csv'])
file2 = st.file_uploader("Choose the second CSV file", type=['csv'])

if file1 and file2:
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # Ensure 'URL' is one of the columns
    if 'URL' not in df1.columns or 'URL' not in df2.columns:
        st.error("Both files must contain a 'URL' column.")
    else:
        # Column selector
        selected_columns = st.multiselect('Select columns to compare:', options=df1.columns[1:])  # Skip 'URL'

        if st.button('Compare Files'):
            result_df = compare_csv(df1, df2, selected_columns)
            st.dataframe(result_df)
            
            # Download link
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download output CSV", csv, "output.csv", "text/csv", key='download-csv')
