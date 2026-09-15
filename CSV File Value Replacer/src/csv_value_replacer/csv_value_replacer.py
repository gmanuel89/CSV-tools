## Import libraries
import logging
import pandas
import traceback
from constants.constants import *

## Initialise logger
app_logger = logging.getLogger(__name__)

# Create a dictionary of "old"-"new" value couples from a CSV file content
def create_replacing_map(input_dataframe: pandas.DataFrame) -> list[dict]:
    # Determine the names of the "new", the "old" and the "column" columns
    column_name_new_value = None
    column_name_old_value = None
    column_name_column_for_replacement = None
    for col in input_dataframe.columns:
        if REPLACEMENT_MAP_KEY_OLD in col.lower():
            column_name_old_value = col
        elif REPLACEMENT_MAP_KEY_NEW in col.lower():
            column_name_new_value = col
        elif REPLACEMENT_MAP_KEY_COLUMN in col.lower():
            column_name_column_for_replacement = col
    # Build the list of dictionaries
    mapping_dictionary_array = []
    if column_name_new_value and column_name_old_value:
        for index, row in input_dataframe.iterrows():
            mapping_dictionary = {REPLACEMENT_MAP_KEY_OLD : row[column_name_old_value], REPLACEMENT_MAP_KEY_NEW : row[column_name_new_value]}
            # If the "column" is specified
            if column_name_column_for_replacement:
                column_name = row[column_name_column_for_replacement]
                mapping_dictionary[REPLACEMENT_MAP_KEY_COLUMN] = column_name
            # Add the mapping to the array of mappings
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
        column_for_replacement = maprepl.get(REPLACEMENT_MAP_KEY_COLUMN)
        old_value = maprepl.get(REPLACEMENT_MAP_KEY_OLD)
        new_value = maprepl.get(REPLACEMENT_MAP_KEY_NEW)
        # For each row of the DataFrame...
        for index, row in input_dataframe.iterrows():
            # Store values for logging
            row_modified = False
            row_old_value = row.copy()
            row_new_value = row.copy()
            # If there is no column(s) specified, go for the all-cell replacement
            if not column_for_replacement:
                # For each column...
                for col in input_dataframe.columns:
                    # Replace the cell values
                    if row[col] == old_value or (pandas.isna(row[col]) and pandas.isna(old_value)):
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
                    if col == column_for_replacement:
                        # Replace the cell values
                        if row[col] == old_value or (pandas.isna(row[col]) and pandas.isna(old_value)):
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
