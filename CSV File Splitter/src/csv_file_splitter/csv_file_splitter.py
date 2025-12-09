## Import libraries
import csv
import os
import pandas
import math

## Read input csv file (returns a dataframe)
def read_csv_file(input_csv_file_path: str) -> pandas.DataFrame | None:
    """Read input csv file (returns a dataframe)"""
    # Initialise output
    input_csv_dataframe = None
    if os.path.exists(input_csv_file_path):
        # Read the CSV file
        input_csv_dataframe = pandas.read_csv(input_csv_file_path)
    # return
    return input_csv_dataframe

## Function to split the original CSV file content (in form of dataframe) into chunks (input can be either the number of 'lines' per chunk or the number of 'chunks' to obtain)
def split_csv_file_content_into_chunks(csv_file_content: pandas.DataFrame, number_of_output_chunks=2, number_of_lines_per_chunk=10) -> list[pandas.DataFrame]:
    """
    Function to split the original CSV file content into chunks (input can be either the number of 'lines' per chunk or the number of 'chunks' to obtain)

    Worst case: a list of one element (i.e. one chunk) being the whole CSV content is returned, so that it is always a chunk-iterable list object
    """
    # Initialise output variable
    csv_file_content_split = []
    # If there is no CSV content or only one line
    if csv_file_content is None or len(csv_file_content) <= 1:
        csv_file_content_split.append(csv_file_content)
        return csv_file_content_split
    # Retrieve the number of lines
    total_number_of_lines = len(csv_file_content)
    # Calculate the number of lines per chunks
    if number_of_output_chunks is not None and number_of_output_chunks > 0: # mode == 'chunks'
        number_of_lines_per_chunk = math.ceil(total_number_of_lines / number_of_output_chunks)
    # Use the input number of lines per chunks
    else: # mode == 'lines'
        if number_of_lines_per_chunk is None or number_of_lines_per_chunk == 0 or number_of_lines_per_chunk > total_number_of_lines:
            number_of_lines_per_chunk = total_number_of_lines
        # Calculate the number of chunks
        number_of_output_chunks = math.ceil(total_number_of_lines / number_of_lines_per_chunk)
    # Split the input dataframe
    for i in range(number_of_output_chunks):
            start = i * number_of_lines_per_chunk
            end = min(start + number_of_lines_per_chunk, total_number_of_lines)
            chunk = csv_file_content.iloc[start:end]
            if not chunk.empty:
                csv_file_content_split.append(chunk)
    # return
    return csv_file_content_split

## Write CSV content (in form of dataframe) into a file
def write_csv_file(csv_file_content: pandas.DataFrame, output_file_name: str, custom_column_ordering=[]) -> None:
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
    csv_file_content.to_csv(output_file_name, index=False)
    # return
    return None
