## Import packages
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QRadioButton, QListWidget, QGridLayout, QFileDialog, QLineEdit, QPushButton, QMessageBox, QProgressBar
import os
import traceback
from csv_file_splitter.csv_file_splitter import *

## Initialise global variables
global working_directory
working_directory = os.getcwd()
global input_csv_file_path
input_csv_file_path = 'Select input CSV file to split'
global number_of_output_chunks
number_of_output_chunks = 2
global number_of_lines_per_chunk
number_of_lines_per_chunk = 10

## Where to locate input file
def set_file_path():
    global working_directory
    global input_csv_file_path
    global input_file_path_label
    filepath_options = QFileDialog.Option.DontUseNativeDialog
    input_csv_file_path, _ = QFileDialog.getOpenFileName(window, 'Select CSV file to split', working_directory, 'CSV Files (*.csv)', options=filepath_options)
    print('Input file: %s' %input_csv_file_path)
    layout.removeWidget(input_file_path_label)
    input_file_path_label = QLabel(input_csv_file_path)
    input_file_path_label.setToolTip(input_csv_file_path)
    input_file_path_label.setFixedWidth(500)
    layout.addWidget(input_file_path_label, 0, 1)

## Where to save files
def set_working_directory():
    global working_directory
    global working_directory_label
    filepath_options = QFileDialog.Option.DontUseNativeDialog.ShowDirsOnly
    working_directory = QFileDialog.getExistingDirectory(window, 'Select Working Directory', working_directory, options=filepath_options)
    print('Output directory set to: %s' %working_directory)
    layout.removeWidget(working_directory_label)
    working_directory_label = QLabel(working_directory)
    working_directory_label.setToolTip(working_directory)
    working_directory_label.setFixedWidth(500)
    layout.addWidget(working_directory_label, 1, 1)

## Exit app
def exit_app():
    exit_confirmation = QMessageBox.question(window, 'Exit Confirmation', 'Are you sure you want to exit?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
    if exit_confirmation == QMessageBox.StandardButton.Yes:
        app.quit()

## Application
def main():
    
    # Qt application
    global app
    app = QApplication([])
    
    ## Main window frame
    global window
    window = QWidget()
    window.setWindowTitle('CSV splitter')
    window.setGeometry(100, 100, 640, 240)

    ## Layout
    global layout
    #layout = QVBoxLayout()
    layout = QGridLayout()
    layout.setHorizontalSpacing(10)
    layout.setVerticalSpacing(20)

    ## Widgets tied to global variables
    # File path
    global input_file_path_label
    global input_csv_file_path
    input_file_path_label = QLabel(input_csv_file_path)
    input_file_path_label.setToolTip(input_csv_file_path)
    input_file_path_label.setFixedWidth(500)
    layout.addWidget(input_file_path_label, 0, 1)
    set_input_file_path_button = QPushButton('Set input CSV file path')
    set_input_file_path_button.clicked.connect(set_file_path)
    layout.addWidget(set_input_file_path_button, 0, 0)
    
    # Working Directory
    global working_directory_label
    working_directory_label = QLabel(working_directory)
    working_directory_label.setToolTip(working_directory)
    working_directory_label.setFixedWidth(500)
    layout.addWidget(working_directory_label, 1, 1)
    set_working_directory_button = QPushButton('Set where to save the CSV chunk files')
    set_working_directory_button.clicked.connect(set_working_directory)
    layout.addWidget(set_working_directory_button, 1, 0)

    # Number of chunks
    global number_of_chunks_input_box
    number_of_chunks_label = QLabel('Number of chunks')
    number_of_chunks_label.setFixedSize(100, 30)
    layout.addWidget(number_of_chunks_label, 2, 0)
    number_of_chunks_input_box = QLineEdit()
    number_of_chunks_input_box.setText('2')
    number_of_chunks_input_box.setFixedSize(500, 30)
    layout.addWidget(number_of_chunks_input_box, 2, 1)

    # Or
    number_of_chunks_or_lines_per_chunk_label = QLabel('Or')
    number_of_chunks_or_lines_per_chunk_label.setFixedSize(100, 30)
    layout.addWidget(number_of_chunks_or_lines_per_chunk_label, 3, 0, 1, 2)

    # Number of lines per chunk
    global number_of_lines_per_chunk_input_box
    number_of_lines_per_chunk_label = QLabel('Number of lines per chunk')
    number_of_lines_per_chunk_label.setFixedSize(100, 30)
    layout.addWidget(number_of_lines_per_chunk_label, 4, 0)
    number_of_lines_per_chunk_input_box = QLineEdit()
    number_of_lines_per_chunk_input_box.setText('10')
    number_of_lines_per_chunk_input_box.setFixedSize(500, 30)
    layout.addWidget(number_of_lines_per_chunk_input_box, 4, 1)

    # App logic button(s)
    generate_report_button = QPushButton('Split CSV file into chunks')
    generate_report_button.clicked.connect(split_csv_file_into_chunks)
    layout.addWidget(generate_report_button, 5, 0, 1, 2)

    # Exit button
    exit_button = QPushButton('Exit')
    exit_button.clicked.connect(exit_app)
    layout.addWidget(exit_button, 6, 0, 1, 2)

    # Progress bar
    global progress_bar
    progress_bar = QProgressBar()
    progress_bar.setValue(0)
    progress_bar.setFormat('%p%')
    layout.addWidget(progress_bar, 7, 0, 1, 2)  

    # Build window
    window.setLayout(layout)
    window.show()
    app.exec()

##
def split_csv_file_into_chunks():
    # Get values from GUI
    progress_bar.setValue(10)
    progress_bar.setFormat('Getting split parameters... %p%')
    number_of_lines_per_chunk = number_of_lines_per_chunk_input_box.text()
    number_of_chunks = number_of_chunks_input_box.text()
    try:
        number_of_chunks = int(number_of_chunks)
    except:
        number_of_chunks = 2
    try:
        number_of_lines_per_chunk = int(number_of_lines_per_chunk)
    except:
        number_of_lines_per_chunk = 10
    # Read CSV input file
    progress_bar.setValue(30)
    progress_bar.setFormat('Reading input file... %p%')
    input_csv_file_content = read_csv_file(input_csv_file_path, output_format=dict)
    # Split CSV input file content into chunks
    progress_bar.setValue(50)
    progress_bar.setFormat('Splitting input file... %p%')
    input_csv_file_content_chunks = split_csv_file_content_into_chunks(input_csv_file_content, number_of_chunks, number_of_lines_per_chunk)
    # Write all output files
    for i in range (len(input_csv_file_content_chunks)):
        progress_bar.setValue(50 + int((i+1)/len(input_csv_file_content_chunks)*50))
        progress_bar.setFormat('Splitting input file... %p%')
        output_file_name = working_directory + '/' + '(' + str(i+1) + ') ' + os.path.basename(input_csv_file_path)
        write_csv_file(input_csv_file_content_chunks[i], output_file_name)
    print('Done!')
    progress_bar.setValue(100)
    progress_bar.setFormat('Done! %p%')

## RUN THE APPLICATION
if __name__ == "__main__":
    main()
