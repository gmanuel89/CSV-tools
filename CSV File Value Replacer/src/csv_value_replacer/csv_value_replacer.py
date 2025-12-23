## Import libraries
import csv
import sys
import os

# Create a dictionary of "old"-"new" value couples from a CSV file content
def create_replacing_map(input_csv_lines):
    # Get header
    csv_header = input_csv_lines[0]
    # Remove it from the list
    input_csv_lines.remove(csv_header)
    # Determine the indices of the "new" and the "old"
    new_index = None
    old_index = None
    column_index = None
    for i in range(len(csv_header)):
        if 'old' in csv_header[i].lower():
            old_index = i
    for i in range(len(csv_header)):
        if 'new' in csv_header[i].lower():
            new_index = i
    for i in range(len(csv_header)):
        if 'column' in csv_header[i].lower():
            column_index = i
    # Build the list of dictionaries
    mapping_dictionary_array = []
    # If the "column" is not specified
    if new_index is not None and old_index is not None and column_index is None:
        for i in range(len(input_csv_lines)):
            mapping_dictionary = {'old' : input_csv_lines[i][old_index], 'new' : input_csv_lines[i][new_index]}
            mapping_dictionary_array.append(mapping_dictionary)
    # If the "column" is specified
    elif new_index is not None and old_index is not None and column_index is not None:
        for i in range(len(input_csv_lines)):
            # retrieve the individual column names (stripped from spaces)
            column_indices = input_csv_lines[i][column_index].split(',')
            for c in range(len(column_indices)):
                column_indices[c] = column_indices[c].strip()
            mapping_dictionary = {'old' : input_csv_lines[i][old_index], 'new' : input_csv_lines[i][new_index], 'columns' : column_indices}
            mapping_dictionary_array.append(mapping_dictionary)
    # Return
    #print(mapping_dictionary_array)
    return mapping_dictionary_array

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

## Replace the csv values according to a list of dictionaries with 'old' and 'new' values
def replace_csv_values(input_csv_file_lines, mapping_dictionary_array, add_new_column_if_match_is_missing=True):
    ## Run if there is a map (otherwise return the input file with no modifications)
    if len(mapping_dictionary_array) == 0: return input_csv_file_lines
    ## Scroll the replacing map items...
    for maprepl in mapping_dictionary_array:
        ## If there is no column(s) specified, go for the all-cell replacement
        if maprepl.get('columns') is None:
            # For each row...
            for r in range(len(input_csv_file_lines)):
                # Skip the header
                if r == 0 : continue
                # For each column
                for c in range(len(input_csv_file_lines[r])):     
                    # Replace the cell value
                    if str(input_csv_file_lines[r][c]) == str(maprepl.get('old')):
                        input_csv_file_lines[r][c] = str(maprepl.get('new'))
        else:
            ## If there are columns specified
            # Determine the indices of the columns (compare mapping with the header)
            columns = maprepl.get('columns')
            column_indices = []
            for i in range(len(columns)):
                for c in range(len(input_csv_file_lines[0])):
                    if columns[i] == input_csv_file_lines[0][c]:
                        column_indices.append(c)
            ## Replace all the values only in selected columns
            # For each row of the CSV...
            for r in range(len(input_csv_file_lines)):
                # Skip the header (or add it)
                if r == 0:
                    if len(column_indices) == 0 and maprepl.get('columns')[0] != '':
                        if add_new_column_if_match_is_missing:
                            input_csv_file_lines[0].extend(maprepl.get('columns'))
                    continue
                # If there are no column matches...
                if len(column_indices) == 0 and maprepl.get('columns')[0] != '':
                    # Add the new value(s) to new column(s) (only if there is a match in the row)
                    if add_new_column_if_match_is_missing:
                        for i in range(len(maprepl.get('columns'))):
                            for c in range(len(input_csv_file_lines[r])):
                                if str(input_csv_file_lines[r][c]) == str(maprepl.get('old')):    
                                    input_csv_file_lines[r].append(str(maprepl.get('new')))
                                    break
                    else:
                        for c in range(len(input_csv_file_lines[r])):     
                            # Replace the cell value
                            if str(input_csv_file_lines[r][c]) == str(maprepl.get('old')):
                                input_csv_file_lines[r][c] = str(maprepl.get('new'))
                else:
                    # For each column (to replace)
                    for c in column_indices:     
                        # Replace the cell value
                        if str(input_csv_file_lines[r][c]) == str(maprepl.get('old')):
                            input_csv_file_lines[r][c] = str(maprepl.get('new'))  
    # Return
    return input_csv_file_lines

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
