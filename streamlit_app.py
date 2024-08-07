import streamlit as st
import pandas as pd

def compare_csv(df1, df2, columns_to_compare):
    """
    Compare two CSV files and identify added, removed, and modified entries.
    
    Args:
    df1 (DataFrame): First dataframe to compare
    df2 (DataFrame): Second dataframe to compare
    columns_to_compare (list): List of column names to compare
    
    Returns:
    DataFrame: Comparison results
    """
    # Setting 'Address' as index for comparison
    df1.set_index('Address', inplace=True)
    df2.set_index('Address', inplace=True)

    # Identify added, removed, and common addresses
    added = df2.index.difference(df1.index)
    removed = df1.index.difference(df2.index)
    common = df1.index.intersection(df2.index)

    data = []

    # Process added URLs
    for address in added:
        row = df2.loc[address]
        data.append(['Added', address] + [item for col in columns_to_compare for item in ('', row.get(col, ''))])

    # Process removed URLs
    for address in removed:
        row = df1.loc[address]
        data.append(['Removed', address] + [item for col in columns_to_compare for item in (row.get(col, ''), '')])

    # Process modified URLs
    for address in common:
        row1 = df1.loc[address]
        row2 = df2.loc[address]
        changes = ['Modified', address]
        row_entries = []
        modified = False

        for col in columns_to_compare:
            old_val = row1.get(col, '')
            new_val = row2.get(col, '')

            # Convert to single values if Series
            old_val = old_val.iloc[0] if isinstance(old_val, pd.Series) and not old_val.empty else old_val
            new_val = new_val.iloc[0] if isinstance(new_val, pd.Series) and not new_val.empty else new_val

            row_entries.append(old_val)
            if old_val != new_val:
                row_entries.append(new_val)
                modified = True
            else:
                row_entries.append('')  # Append blank for unchanged 'New' values

        if modified:
            changes.extend(row_entries)
            data.append(changes)

    # Construct output DataFrame headers
    output_columns = ['Added/Removed/Modified', 'Address']
    for col in columns_to_compare:
        output_columns.extend([f'Old {col}', f'New {col}'])

    # Create DataFrame from the collected data
    return pd.DataFrame(data, columns=output_columns)

# Streamlit UI
st.title('CSV Comparison Tool')

# File uploaders
file1 = st.file_uploader("Choose the first CSV file", type=['csv'])
file2 = st.file_uploader("Choose the second CSV file", type=['csv'])

if file1 and file2:
    # Read CSV files into DataFrames
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # Get columns for comparison (excluding 'Address')
    columns = df1.columns.tolist()
    columns.remove('Address')
    
    # Allow user to select columns for comparison
    selected_columns = st.multiselect('Select columns to compare:', options=columns)

    if st.button('Compare Files'):
        if selected_columns:
            # Perform comparison
            result_df = compare_csv(df1, df2, selected_columns)
            
            # Display results
            st.dataframe(result_df)

            # Provide download option for results
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download output CSV", csv, "changeLog.csv", "text/csv", key='download-csv')
        else:
            st.error("Please select at least one column to compare.")