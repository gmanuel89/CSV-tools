## Import libraries
import csv
import os
import sys
import math

## Get CSV header
def get_csv_content_header(csv_content: list[list] | list[dict]) -> list[str]:
    """Get CSV header"""
    # Initialise output
    csv_content_header = []
    if isinstance(csv_content, list):
        if isinstance(csv_content[0], list):
            csv_content_header = csv_content[0]
        elif isinstance(csv_content[0], dict):
            # Each item of the list is a dictionary, but there is no key if the cell value is empty
            for csv_line in csv_content:
                csv_content_header.extend(list(csv_line.keys()))
            csv_content_header = list(set(csv_content_header))
        else:
            pass
    # return
    return csv_content_header

## Read input csv file (returns a list of rows)
def read_csv_file(input_csv_file_path: str, output_format=dict) -> list[list] | list[dict]:
    """Read input csv file (returns a list of rows)"""
    # Initialise output
    input_csv_file_lines = None
    ## Open the CSV file
    if os.path.exists(input_csv_file_path):
        with open(input_csv_file_path, 'r', encoding='utf-8-sig', newline='') as input_file:
            # Prevent possible errors due to large columns (beyond 131072 characters)
            try:
                if output_format == list:
                    input_csv_file_lines = list(csv.reader(input_file))
                elif output_format == dict:
                    input_csv_file_dictionary = csv.DictReader(input_file)
                    input_csv_file_lines = []
                    for row in input_csv_file_dictionary:
                        input_csv_file_lines.append(dict(row))
                else:
                    input_csv_file_lines = csv.reader(input_file)
            except:
                print("Presence of too large cells!!!")
                field_size_limit = sys.maxsize
                while True:
                    try:
                        csv.field_size_limit(field_size_limit)
                        break
                    except:
                        field_size_limit = int(field_size_limit / 10)
                if output_format == list:
                    input_csv_file_lines = list(csv.reader(input_file))
                elif output_format == dict:
                    input_csv_file_dictionary = csv.DictReader(input_file)
                    input_csv_file_lines = []
                    for row in input_csv_file_dictionary:
                        input_csv_file_lines.append(dict(row))
                else:
                    input_csv_file_lines = csv.reader(input_file)
        ## Bring the row lengths on par
        if output_format == list:
            csv_column_header = input_csv_file_lines[0]
            csv_column_number = len(csv_column_header)
            for r in range(len(input_csv_file_lines)):
                if len(input_csv_file_lines[r]) < csv_column_number:
                    for cdiff in range(csv_column_number - len(input_csv_file_lines[r])):
                        input_csv_file_lines[r].append(None)
        else:
            pass
    # return
    return input_csv_file_lines

## Function to split the original CSV file content into chunks (input can be either the number of 'lines' per chunk or the number of 'chunks' to obtain)
def split_csv_file_content_into_chunks(csv_file_content: list[list] | list[dict], number_of_output_chunks=2, number_of_lines_per_chunk=10) -> list[list[list]] | list[list[dict]]:
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
    # If the format is a list of lists
    if csv_file_content is not None and isinstance(csv_file_content[0], list):
        # Store the header (to be placed at every csv)
        csv_header = csv_file_content[0]
        # The actual lines are beyond the header
        total_number_of_lines = len(csv_file_content) - 1
    # If the format is a list of dictionaries
    elif csv_file_content is not None and isinstance(csv_file_content[0], dict):
        # Store the header (to be placed at every csv)
        csv_header = list(csv_file_content[0].keys())
        # The actual lines are beyond the header
        total_number_of_lines = len(csv_file_content)
    else:
        csv_file_content_split.append(csv_file_content)
        return csv_file_content_split
    # Calculate the number of lines per chunks
    if number_of_output_chunks is not None and number_of_output_chunks > 0: # mode == 'chunks'
        number_of_lines_per_chunk = math.ceil(total_number_of_lines / number_of_output_chunks)
    # Use the input number of lines per chunks
    else: # mode == 'lines'
        if number_of_lines_per_chunk is None or number_of_lines_per_chunk == 0 or number_of_lines_per_chunk > total_number_of_lines:
            number_of_lines_per_chunk = total_number_of_lines
        # Calculate the number of chunks
        number_of_output_chunks = math.ceil(total_number_of_lines / number_of_lines_per_chunk)
    # Initialise index variables
    lower_index = None
    higher_index = None
    # Start cycling after the header
    for i in range(number_of_output_chunks):
        if lower_index is None:
            lower_index = 0
        else:
            lower_index = lower_index + number_of_lines_per_chunk
        if higher_index is None:
            higher_index = number_of_lines_per_chunk
        else:
            higher_index = higher_index + number_of_lines_per_chunk
        # Do not go over the length of the file lines
        if higher_index >= total_number_of_lines + 1 : higher_index = total_number_of_lines + 1
        # Retrieve the lines to be put into the output
        output_lines = csv_file_content[lower_index:higher_index]
        # Break out if there are no more lines
        if len(output_lines) == 0: break
        # Add the chunk to the final output
        if csv_file_content is not None and isinstance(csv_file_content[0], list):
            output_lines_with_header = output_lines
            output_lines_with_header.insert(0, csv_header)
        else:
            output_lines_with_header = output_lines
        csv_file_content_split.append(output_lines_with_header)
    # return
    return csv_file_content_split

## Write CSV content into a file
def write_csv_file(csv_file_content: list[list] | list[dict], output_file_name: str, custom_column_ordering=[]) -> None:
    """Write CSV content into a file"""
    # Exit if there is no content
    if len(csv_file_content) == 0: return None
    # Check output file name
    if output_file_name == '' : output_file_name = 'CSV file'
    if not output_file_name.endswith('.csv') : output_file_name = output_file_name + '.csv'
    # Get header (harmonised)
    csv_header = get_csv_content_header(csv_file_content)
    # Custom column ordering (sort the ones specified, add back all the rest)
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
    # Write file content
    with open(output_file_name, 'w+', encoding='UTF8', newline='') as output_file:
        # If it is a list of lists...
        if isinstance(csv_file_content[0], list):
            # Write content to file
            csv_writer = csv.writer(output_file)
            csv_writer.writerow(custom_csv_header)
            for r in range(1,len(csv_file_content)): # skip header
                csv_row = csv_file_content[r]
                csv_row_reordered = []
                for hd in custom_csv_header:
                    csv_row_reordered.append(csv_row[csv_file_content[0].index(hd)])
                csv_writer.writerow(csv_row_reordered)
        # If it is a list of dictionaries
        elif isinstance(csv_file_content[0], dict):
            # Write content to file
            csv_writer = csv.DictWriter(output_file, fieldnames=custom_csv_header)
            csv_writer.writeheader()
            csv_writer.writerows(csv_file_content)
        else:
            pass
        # return
        return None
