## Import packages
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QGridLayout, QFileDialog, QLineEdit, QPushButton, QMessageBox, QProgressBar
import os
import traceback
from log_handling.log_handling import *
from csv_file_splitter.csv_file_splitter import *

## Initialise logger
setup_logging('logging_config.json')
app_logger = logging.getLogger(__name__)

## Initialise global variables
global working_directory
working_directory = os.getcwd()
global input_csv_file_path
input_csv_file_path = 'Select input CSV file to split'
global number_of_output_chunks
number_of_output_chunks = 2
global number_of_lines_per_chunk
number_of_lines_per_chunk = 10
global split_modality
split_modality = 'Chunks'

## Where to locate input file
def set_file_path():
    global working_directory
    global input_csv_file_path
    global input_file_path_label
    filepath_options = QFileDialog.Option.DontUseNativeDialog
    input_csv_file_path, _ = QFileDialog.getOpenFileName(window, 'Select CSV file to split', working_directory, 'CSV Files (*.csv)', options=filepath_options)
    app_logger.info('Input file: %s' %input_csv_file_path)
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
    app_logger.info('Output directory set to: %s' %working_directory)
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
    # Combo box with list of choice between single file and folder
    global split_modality
    global split_modality_combobox
    split_modality_label = QLabel('Chunks\nor\nLines per chunk?')
    split_modality_label.setFixedSize(150, 50)
    layout.addWidget(split_modality_label, 2, 0)
    split_modality_combobox = QComboBox()
    split_modality_combobox.addItems(['Chunks', 'Lines per chunk'])
    split_modality_combobox.setCurrentIndex(0) # select default value
    layout.addWidget(split_modality_combobox, 2, 1)
    
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
    global number_input_box
    number_label = QLabel('Number of chunks\nor\nNumber of lines per chunk')
    number_label.setFixedSize(150, 50)
    layout.addWidget(number_label, 3, 0)
    number_input_box = QLineEdit()
    number_input_box.setText('2')
    number_input_box.setFixedSize(500, 30)
    layout.addWidget(number_input_box, 3, 1)

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
    global split_modality
    # Get values from GUI
    progress_bar.setValue(10)
    progress_bar.setFormat('Getting split parameters... %p%')
    split_modality = split_modality_combobox.currentText()
    if 'chunks' in split_modality.lower():
        number_of_lines_per_chunk = None
        try:
            number_of_chunks = int(number_input_box.text())
        except:
            number_of_chunks = 2
    else:
        number_of_chunks = None
        try:
            number_of_lines_per_chunk = int(number_input_box.text())
        except:
            number_of_lines_per_chunk = 10
    # Read CSV input file
    progress_bar.setValue(30)
    progress_bar.setFormat('Reading input file... %p%')
    input_csv_file_content = pandas.read_csv(input_csv_file_path, dtype=str)
    # Split CSV input file content into chunks
    if input_csv_file_content is not None:
        progress_bar.setValue(50)
        progress_bar.setFormat('Splitting input file... %p%')
        input_csv_file_content_chunks = split_csv_file_content_into_chunks(input_csv_file_content, number_of_chunks, number_of_lines_per_chunk)
        # Write all output files
        for i in range (len(input_csv_file_content_chunks)):
            progress_bar.setValue(50 + int((i+1)/len(input_csv_file_content_chunks)*50))
            progress_bar.setFormat('Splitting input file... %p%')
            output_file_name = working_directory + '/' + '(' + str(i+1) + ') ' + os.path.basename(input_csv_file_path)
            try:
                input_csv_file_content_chunks[i].to_csv(output_file_name, index=False, encoding='utf-8-sig')
                app_logger.info('Output CSV file saved successfully!')
            except:
                app_logger.error('Failed to write CSV file!')
                app_logger.debug(traceback.format_exc())
        app_logger.info('Done!')
        progress_bar.setValue(100)
        progress_bar.setFormat('Done! %p%')
    else:
        app_logger.warning('File not split!')
        progress_bar.setValue(100)
        progress_bar.setFormat('File not split! %p%')

## RUN THE APPLICATION
if __name__ == "__main__":
    main()
