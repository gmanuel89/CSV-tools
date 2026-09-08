## Import libraries
import logging
import pandas
import traceback

## Initialise logger
app_logger = logging.getLogger(__name__)

# Create a dictionary of "old"-"new" value couples from a CSV file content
def create_replacing_map(input_dataframe: pandas.DataFrame) -> list[dict]:
    # Determine the names of the "new", the "old" and the "column" columns
    column_name_new_value = None
    column_name_old_value = None
    column_name_column_for_replacement = None
    for col in input_dataframe.columns:
        if 'old' in col.lower():
            column_name_old_value = col
        elif 'new' in col.lower():
            column_name_new_value = col
        elif 'column' in col.lower():
            column_name_column_for_replacement = col
    # Build the list of dictionaries
    mapping_dictionary_array = []
    # If the "column" is not specified
    if column_name_new_value is not None and column_name_old_value is not None and column_name_column_for_replacement is None:
        for index, row in input_dataframe.iterrows():
            mapping_dictionary = {'old' : row[column_name_old_value], 'new' : row[column_name_new_value]}
            mapping_dictionary_array.append(mapping_dictionary)
    # If the "column" is specified
    elif column_name_new_value is not None and column_name_old_value is not None and column_name_column_for_replacement is not None:
        for index, row in input_dataframe.iterrows():
            # retrieve the individual column names (stripped from spaces)
            column_names = row[column_name_column_for_replacement].split(',') if (not pandas.isna(row[column_name_column_for_replacement]) and not pandas.isnull(row[column_name_column_for_replacement])) else []
            for c in range(len(column_names)):
                column_names[c] = column_names[c].strip()
            mapping_dictionary = {'old' : row[column_name_old_value], 'new' : row[column_name_new_value], 'columns' : column_names}
            mapping_dictionary_array.append(mapping_dictionary)
    # Return
    return mapping_dictionary_array

## Replace the csv values according to a list of dictionaries with 'old' and 'new' values
def replace_csv_values(input_dataframe: pandas.DataFrame, mapping_dictionary_array: list[dict], columns_to_print_in_log=[]) -> pandas.DataFrame:
    # Run if there is a map (otherwise return the input file with no modifications)
    if len(mapping_dictionary_array) == 0:
        app_logger.warning('No replacement will occur!')
        return input_dataframe
    app_logger.info('Replacing values in CSV file...')
    # Scroll the replacing map items...
    for maprepl in mapping_dictionary_array:
        # Get replacement information
        columns_for_replacements = maprepl.get('columns', [])
        old_value = maprepl.get('old')
        new_value = maprepl.get('new')
        # For each row of the DataFrame...
        for index, row in input_dataframe.iterrows():
            # Store values for logging
            row_modified = False
            row_old_value = row.copy()
            row_new_value = row.copy()
            # If there is no column(s) specified, go for the all-cell replacement
            if not columns_for_replacements:
                # For each column...
                for col in input_dataframe.columns:
                    # Replace the cell values
                    if row[col] == old_value:
                        #app_logger.debug(f"Row {row.name}, Column '{col}': '{row[col]}' → '{new_value}'")
                        # Update the original DataFrame
                        input_dataframe.at[row.name, col] = new_value
                        # Store the row change for logging
                        row_new_value[col] = new_value
                        row_modified = True
            # If there are columns specified
            else:
                # For each column...
                for col in input_dataframe.columns:
                    if col in columns_for_replacements:
                        # Replace the cell values
                        if row[col] == old_value:
                            #app_logger.debug(f"Row {row.name}, Column '{col}': '{row[col]}' → '{new_value}'")
                            # Update the original DataFrame
                            input_dataframe.at[row.name, col] = new_value
                            # Store the row change for logging
                            row_new_value[col] = new_value
                            row_modified = True
            # Log only in case of modifications
            if row_modified:
                log_row_value_replacement(row_old_value, columns_to_print_in_log, 'Row updated (old values):\n')
                log_row_value_replacement(row_new_value, columns_to_print_in_log, 'Row updated (new values):\n')
    # Return
    return input_dataframe

## Log the row value with a specific set of columns
def log_row_value_replacement(row: pandas.Series, columns_to_print_in_log: list[str], log_phrase='Updating row:\n') -> None:
    """Log the row value with a specific set of columns"""
    # Compare the columns in the DataFrame with the ones provided
    row_columns = set(row.index)
    provided_columns_to_print_in_log = set(columns_to_print_in_log)
    final_columns_to_print_in_log = row_columns.intersection(provided_columns_to_print_in_log)
    if final_columns_to_print_in_log:
        row_to_print = {col: row[col] for col in final_columns_to_print_in_log}
        app_logger.debug(f'{log_phrase}{row_to_print}')
    else:
        row_to_print = row.to_dict()
        app_logger.debug(f'{log_phrase}{row_to_print}')

## Replace the csv values according to a list of dictionaries with 'old' and 'new' values
def replace_csv_values2(input_dataframe: pandas.DataFrame, mapping_dictionary_array: list[dict]) -> pandas.DataFrame:
    ## Run if there is a map (otherwise return the input file with no modifications)
    if len(mapping_dictionary_array) == 0: return input_dataframe
    ## Scroll the replacing map items...
    for maprepl in mapping_dictionary_array:
        ## If there is no column(s) specified, go for the all-cell replacement
        if not maprepl.get('columns'):
            # For each column...
            for col in input_dataframe.columns:
                # Replace the cell values
                app_logger.debug(f'Replacement taking place:\nColumn: {col}\nOld Value: {maprepl.get('old')}\nNew Value: {maprepl.get('new')}')
                input_dataframe[col] = input_dataframe[col].replace(str(maprepl.get('old')), str(maprepl.get('new')))
        else:
            ## If there are columns specified
            # Determine the indices of the columns (compare mapping with the header)
            columns = maprepl.get('columns',[])
            # For each column...
            for col in input_dataframe.columns:
                if col in columns:
                    # Replace the cell values
                    app_logger.debug(f'Replacement taking place:\nColumn: {col}\nOld Value: {maprepl.get('old')}\nNew Value: {maprepl.get('new')}')
                    input_dataframe[col] = input_dataframe[col].replace(str(maprepl.get('old')), str(maprepl.get('new')))
    # Return
    return input_dataframe

## Write CSV content (in form of dataframe) into a file
def write_csv_file(csv_file_content: pandas.DataFrame, output_file_name: str, custom_column_ordering=[]) -> bool:
    """Write CSV content (in form of dataframe) into a file"""
    # Check output file name
    if output_file_name == '' : output_file_name = 'CSV file'
    if not output_file_name.endswith('.csv') : output_file_name = output_file_name + '.csv'
    # Custom column ordering (sort the ones specified, add back all the rest)
    csv_header = csv_file_content.columns.tolist()
    if custom_column_ordering is not None and len(custom_column_ordering) > 0:
        custom_csv_header = []
        for cust_col in custom_column_ordering:
            for col in csv_header:
                if col == cust_col:
                    custom_csv_header.append(col)
                    break
        for col in csv_header:
            if col not in custom_column_ordering:
                custom_csv_header.append(col)
    else:
        custom_csv_header = csv_header
    # Get the custom column ordering  
    csv_file_content = csv_file_content[custom_csv_header]
    # Write file content
    try:
        csv_file_content.to_csv(output_file_name, index=False, encoding='utf-8-sig')
        file_written = True
    except:
        file_written = False
        app_logger.debug(traceback.format_exc())
    # return
    return file_written
