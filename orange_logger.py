from datetime import datetime


def write_exception(write_file, traceback):
    timestamp = str(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
    write_file.write(f"{timestamp} - execption - \n\t{traceback}\n")


def write_event(write_file, text):
    timestamp = str(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
    write_file.write(f"{timestamp} - event - \n\t{text}\n")
