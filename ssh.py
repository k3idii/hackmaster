import paramiko
import warnings

warnings.filterwarnings(action='ignore',module='.*paramiko.*')
paramiko.util.log_to_file('./paramiko.log')
