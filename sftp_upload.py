"""
Python script to connect to a remote server via SFTP and update the source code
by uploading files from a local to a remote directory.
Make sure to install the 'paramiko' library using 'pip install paramiko' before running the script.
"""
import json
import os

import paramiko


def get_local_dir():
    root = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(root, 'src')
    return src


def update_source_code(server_address, port_number, username, password, local_path, remote_path):
    transport = paramiko.Transport((server_address, int(port_number)))
    transport.connect(username=username, password=password)

    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        sftp.put(local_path, remote_path)
        print(f"Source code updated successfully from {local_path} to {remote_path}")
    except Exception as e:
        print(f"Error updating source code: {e}")
    finally:
        sftp.close()
        transport.close()


# .sftp_config.json

if __name__ == '__main__':
    with open('.sftp_config.json') as config_file:
        config = json.load(config_file)

    update_source_code(config['SERVER_ADDRESS'],
                       config['PORT_NUMBER'],
                       config['USERNAME'],
                       config['PASSWORD'],
                       get_local_dir(),
                       config['REMOTE_DIR'])
