## Import libraries
import csv
import os
import pandas
import math
import logging

## Initialise logger
app_logger = logging.getLogger(__name__)

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
        app_logger.info('Mode: chunks')
        app_logger.info(f'Number of chunks: {number_of_output_chunks}')
        number_of_lines_per_chunk = math.ceil(total_number_of_lines / number_of_output_chunks)
    # Use the input number of lines per chunks
    else: # mode == 'lines'
        app_logger.info('Mode: lines')
        if number_of_lines_per_chunk is None or number_of_lines_per_chunk == 0 or number_of_lines_per_chunk > total_number_of_lines:
            number_of_lines_per_chunk = total_number_of_lines
        app_logger.info(f'Number of lines per chunk: {number_of_lines_per_chunk}')
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
