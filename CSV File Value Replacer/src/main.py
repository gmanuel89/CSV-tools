## Import packages
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QRadioButton, QListWidget, QGridLayout, QFileDialog, QLineEdit, QPushButton, QMessageBox, QProgressBar
import os
import traceback
from csv_value_replacer.csv_value_replacer import *

## Initialise global variables
global working_directory
working_directory = os.getcwd()
global input_csv_file_path
input_csv_file_path = 'Select the CSV file with values to be replaced'
global csv_map_file_path
csv_map_file_path = 'Select the CSV file with the "old"-"new" map for value replacement'


## Where to locate input file
def set_input_csv_file_path():
    global working_directory
    global input_csv_file_path
    global input_file_path_label
    global input_csv_file_name
    filepath_options = QFileDialog.Option.DontUseNativeDialog
    input_csv_file_path, _ = QFileDialog.getOpenFileName(window, 'Select the CSV file with values to be replaced', working_directory, 'CSV Files (*.csv)', options=filepath_options)
    input_csv_file_name = os.path.basename(input_csv_file_path)
    print('Input file: %s' %input_csv_file_path)
    print('Input file name: %s' %input_csv_file_name)
    layout.removeWidget(input_file_path_label)
    input_file_path_label = QLabel(input_csv_file_path)
    input_file_path_label.setToolTip(input_csv_file_path)
    input_file_path_label.setFixedWidth(500)
    layout.addWidget(input_file_path_label, 0, 1)

## Where to locate input file
def set_csv_map_file_path():
    global working_directory
    global csv_map_file_path
    global map_file_path_label
    filepath_options = QFileDialog.Option.DontUseNativeDialog
    csv_map_file_path, _ = QFileDialog.getOpenFileName(window, 'Select the CSV file with the "old"-"new" map for value replacement', working_directory, 'CSV Files (*.csv)', options=filepath_options)
    print('Input file: %s' %csv_map_file_path)
    layout.removeWidget(map_file_path_label)
    map_file_path_label = QLabel(csv_map_file_path)
    map_file_path_label.setToolTip(csv_map_file_path)
    map_file_path_label.setFixedWidth(500)
    layout.addWidget(map_file_path_label, 1, 1)

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
    window.setWindowTitle('CSV value replacer')
    window.setGeometry(100, 100, 640, 240)

    ## Layout
    global layout
    #layout = QVBoxLayout()
    layout = QGridLayout()
    layout.setHorizontalSpacing(10)
    layout.setVerticalSpacing(20)

    ## Widgets tied to global variables
    # Input CSV file path
    global input_file_path_label
    global input_csv_file_path
    input_file_path_label = QLabel(input_csv_file_path)
    input_file_path_label.setToolTip(input_csv_file_path)
    input_file_path_label.setFixedWidth(500)
    layout.addWidget(input_file_path_label, 0, 1)
    set_input_file_path_button = QPushButton('Set input CSV file path')
    set_input_file_path_button.clicked.connect(set_input_csv_file_path)
    layout.addWidget(set_input_file_path_button, 0, 0)
    
    # Input CSV map file path
    global map_file_path_label
    global csv_map_file_path
    map_file_path_label = QLabel(csv_map_file_path)
    map_file_path_label.setToolTip(csv_map_file_path)
    map_file_path_label.setFixedWidth(500)
    layout.addWidget(map_file_path_label, 1, 1)
    set_map_file_path_button = QPushButton('Set map CSV file path')
    set_map_file_path_button.clicked.connect(set_csv_map_file_path)
    layout.addWidget(set_map_file_path_button, 1, 0)

    # App logic button(s)
    replace_csv_values_button = QPushButton('Replace values in CSV file')
    replace_csv_values_button.clicked.connect(replace_values_in_csv_file)
    layout.addWidget(replace_csv_values_button, 2, 0, 1, 2)

    # Exit button
    exit_button = QPushButton('Exit')
    exit_button.clicked.connect(exit_app)
    layout.addWidget(exit_button, 3, 0, 1, 2)

    # Progress bar
    global progress_bar
    progress_bar = QProgressBar()
    progress_bar.setValue(0)
    progress_bar.setFormat('%p%')
    layout.addWidget(progress_bar, 4, 0, 1, 2)  

    # Build window
    window.setLayout(layout)
    window.show()
    app.exec()

## Replace values in CSV file
def replace_values_in_csv_file():
    # Get values from GUI
    progress_bar.setValue(15)
    progress_bar.setFormat('Fetching input CSV file content... %p%')
    input_csv_file_content = read_csv_file(input_csv_file_path, list)
    progress_bar.setValue(30)
    progress_bar.setFormat('Fetching content of replacement map CSV file... %p%')
    csv_map_file_content = read_csv_file(csv_map_file_path, list)
    if input_csv_file_content and csv_map_file_content:
        # Create the map
        progress_bar.setValue(45)
        progress_bar.setFormat('Generating replacement map for CSV file... %p%')
        mapping_dictionary_array = create_replacing_map(csv_map_file_content)
        # Generate the output
        output_csv_file_content = replace_csv_values(input_csv_file_content, mapping_dictionary_array, add_new_column_if_match_is_missing=True)
        # Write output file
        write_csv_file(output_csv_file_content, input_csv_file_name.split('.csv')[0] + '_replaced.csv')
        print('Done!')
        progress_bar.setValue(100)
        progress_bar.setFormat('Done! %p%')
    else:
        print('Failure!')
        progress_bar.setValue(100)
        progress_bar.setFormat('Failure! Input CSV file or replacing map not found! %p%')

## RUN THE APPLICATION
if __name__ == "__main__":
    main()
