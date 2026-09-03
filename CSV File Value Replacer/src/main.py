## Import packages
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QGridLayout, QFileDialog, QPushButton, QMessageBox, QProgressBar
import os
import pandas
from log_handling.log_handling import *
from csv_value_replacer.csv_value_replacer import *

## Initialise logger
setup_logging('logging_config.json')
app_logger = logging.getLogger(__name__)

## Initialise global variables
global working_directory
working_directory = os.getcwd()
global file_or_folder
file_or_folder = 'File'
global input_csv_file_path
input_csv_file_path = 'Select the CSV file or folder with CSV files with values to be replaced'
global csv_map_file_path
csv_map_file_path = 'Select the CSV file with the "old"-"new" map for value replacement'


## Where to locate input file or folder
def set_input_csv_file_path():
    global file_or_folder
    global file_or_folder_combobox
    global working_directory
    global input_csv_file_path
    global input_file_path_label
    file_or_folder = file_or_folder_combobox.currentText()
    #filepath_options = QFileDialog.Option.DontUseNativeDialog
    if str(file_or_folder).lower() == 'file':
        input_csv_file_path, _ = QFileDialog.getOpenFileName(window, 'Select the CSV file with values to be replaced', working_directory, 'CSV Files (*.csv)')#, options=filepath_options)   
    else:
        input_csv_file_path = QFileDialog.getExistingDirectory(window, 'Select the folder containing the CSV files with values to be replaced', working_directory)#, options=filepath_options)
    app_logger.info(f'Input file: {input_csv_file_path}')
    layout.removeWidget(input_file_path_label)
    input_file_path_label = QLabel(input_csv_file_path)
    input_file_path_label.setToolTip(input_csv_file_path)
    input_file_path_label.setFixedWidth(500)
    layout.addWidget(input_file_path_label, 1, 1)

## Where to locate input file
def set_csv_map_file_path():
    global working_directory
    global csv_map_file_path
    global map_file_path_label
    #filepath_options = QFileDialog.Option.DontUseNativeDialog
    csv_map_file_path, _ = QFileDialog.getOpenFileName(window, 'Select the CSV file with the "old"-"new" map for value replacement', working_directory, 'CSV Files (*.csv)')#, options=filepath_options)
    app_logger.info(f'Input file: {csv_map_file_path}')
    layout.removeWidget(map_file_path_label)
    map_file_path_label = QLabel(csv_map_file_path)
    map_file_path_label.setToolTip(csv_map_file_path)
    map_file_path_label.setFixedWidth(500)
    layout.addWidget(map_file_path_label, 2, 1)

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
    # Combo box with list of choice between single file and folder
    global file_or_folder
    global file_or_folder_combobox
    file_or_folder_label = QLabel('File or Folder?')
    file_or_folder_label.setFixedSize(150, 15)
    layout.addWidget(file_or_folder_label, 0, 0)
    file_or_folder_combobox = QComboBox()
    file_or_folder_combobox.addItems(['File', 'Folder'])
    file_or_folder_combobox.setCurrentIndex(0) # select default value
    layout.addWidget(file_or_folder_combobox, 0, 1)
    
    # Input CSV file path
    global input_file_path_label
    global input_csv_file_path
    input_file_path_label = QLabel(input_csv_file_path)
    input_file_path_label.setToolTip(input_csv_file_path)
    input_file_path_label.setFixedWidth(500)
    layout.addWidget(input_file_path_label, 1, 1)
    set_input_file_path_button = QPushButton('Set input CSV file path')
    set_input_file_path_button.clicked.connect(set_input_csv_file_path)
    layout.addWidget(set_input_file_path_button, 1, 0)
    
    # Input CSV map file path
    global map_file_path_label
    global csv_map_file_path
    map_file_path_label = QLabel(csv_map_file_path)
    map_file_path_label.setToolTip(csv_map_file_path)
    map_file_path_label.setFixedWidth(500)
    layout.addWidget(map_file_path_label, 2, 1)
    set_map_file_path_button = QPushButton('Set map CSV file path')
    set_map_file_path_button.clicked.connect(set_csv_map_file_path)
    layout.addWidget(set_map_file_path_button, 2, 0)

    # App logic button(s)
    replace_csv_values_button = QPushButton('Replace values in CSV file')
    replace_csv_values_button.clicked.connect(replace_values_in_csv_file)
    layout.addWidget(replace_csv_values_button, 3, 0, 1, 2)

    # Exit button
    exit_button = QPushButton('Exit')
    exit_button.clicked.connect(exit_app)
    layout.addWidget(exit_button, 4, 0, 1, 2)

    # Progress bar
    global progress_bar
    progress_bar = QProgressBar()
    progress_bar.setValue(0)
    progress_bar.setFormat('%p%')
    layout.addWidget(progress_bar, 5, 0, 1, 2)  

    # Build window
    window.setLayout(layout)
    window.show()
    app.exec()

## Replace values in CSV file
def replace_values_in_csv_file():
    # Get values from GUI
    app_logger.info('Fetching input CSV file content...')
    progress_bar.setValue(15)
    progress_bar.setFormat('Fetching input CSV file content... %p%')
    input_csv_file_content = pandas.read_csv(input_csv_file_path)
    app_logger.info('Fetching content of replacement map CSV file...')
    progress_bar.setValue(30)
    progress_bar.setFormat('Fetching content of replacement map CSV file... %p%')
    csv_map_file_content = pandas.read_csv(csv_map_file_path)
    if not input_csv_file_content.empty and not csv_map_file_content.empty:
        # Create the map
        progress_bar.setValue(45)
        progress_bar.setFormat('Generating replacement map for CSV file... %p%')
        mapping_dictionary_array = create_replacing_map(csv_map_file_content)
        # Generate the output
        output_csv_file_content = replace_csv_values(input_csv_file_content, mapping_dictionary_array)
        # Write output file
        input_csv_file_name = os.path.basename(input_csv_file_path)
        write_csv_file(output_csv_file_content, input_csv_file_name.split('.csv')[0] + '_replaced.csv')
        app_logger.info('Done!')
        progress_bar.setValue(100)
        progress_bar.setFormat('Done! %p%')
    else:
        app_logger.error('Failure! Input CSV file or replacing map not found!')
        progress_bar.setValue(100)
        progress_bar.setFormat('Failure! Input CSV file or replacing map not found! %p%')

## RUN THE APPLICATION
if __name__ == "__main__":
    main()
