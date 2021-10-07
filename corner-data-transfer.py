#!/usr/bin/env python3
'''
The Python API client for the Cornèr Bank transfer platform.
'''

from argparse import ArgumentParser
from datetime import datetime
from functools import reduce

from gnupg import GPG
from requests import Session

#: The default URL.
DEFAULT_URL = 'https://ft.corner.ch/'


class CornerDataFile:
    '''
    A single file of the Cornèr Bank data transfer platform.

    :param requests.Session session: The requests session
    :param dict file: The file JSON
    '''

    def __init__(self, session, file):
        self.session = session
        self.file    = file

    def __str__(self):
        '''
        String representation of the instance.

        :return: String version
        :rtype: str
        '''
        return self.file['filename']

    def __repr__(self):
        '''
        Official string representation of the instance.

        :return: String version
        :rtype: str
        '''
        return f'<{self.__class__.__name__} "{self.file["id"]}">'

    @property
    def filename(self):
        '''
        The filename of the file.

        :return: The filename
        :rtype: str
        '''
        return self.file['filename']

    @property
    def url(self):
        '''
        The download URL of the file.

        :return: The download URL
        :rtype: str
        '''
        return self.file['downloadUri']

    @property
    def put_date(self):
        '''
        The timestamp when the file was put on the server.

        :return: The put date
        :rtype: datetime.datetime
        '''
        return datetime.fromisoformat(
            self.file['attributes']['FSR_FILE_SYS_MD.START_PUT_DATE'].rstrip('Z')
        )

    @property
    def last_read_date(self):
        '''
        The timestamp when the file was last read.

        :return: The last read date
        :rtype: datetime.datetime
        '''
        date = self.file['attributes']['FSR_FILE_SYS_MD.LAST_READ_DATE'].rstrip('Z')

        if date:
            return datetime.fromisoformat(date)

        return None

    def download(self, destination, decrypt=True):
        '''
        Download the file.

        :param str destination: The destination path
        :param bool decrypt: Decrypt the retreived file
        '''
        response = self.session.get(url=self.url)
        response.raise_for_status()

        if decrypt:
            decrypted_data = GPG().decrypt(response.content)
            assert decrypted_data.ok, decrypted_data.status
            data = str(decrypted_data)
        else:
            data = response.text

        with open(file=destination, mode='w', encoding='utf-8') as file:
            file.write(data)


class CornerDataTransfer:
    '''
    The API class to communicate with the Cornèr Bank data transfer HTTPS
    channel / platform.

    :param str username: The username
    :param str password: The password
    :param str url: The base URL
    '''

    def __init__(self, username, password, url=DEFAULT_URL):
        self.username = username
        self.password = password
        self.url      = url
        self.session  = Session()

    def get_url(self, path):
        '''
        Get the full URL for a path.

        :param str path: The path

        :return: The absolute URL
        :rtype: str
        '''
        return f'{self.url.rstrip("/")}/{path}'

    def login(self):
        '''
        Login into the platform.
        '''
        data = {
            'username': self.username,
            'password': self.password,
        }

        self.session.get(url=self.get_url('static')).raise_for_status()
        self.session.post(url=self.get_url('auth/login'), data=data).raise_for_status()

    def get_files(self, directory='OUT'):
        '''
        Get the files of a directory.

        :param str directory: The directory name

        :return: The filelist
        :rtype: list
        '''
        response = self.session.get(self.get_url(f'files/{directory}?spcmd=splist'))
        response.raise_for_status()

        files = {}
        for file in response.json()['files']:
            data_file = CornerDataFile(session=self.session, file=file)
            files[data_file.filename] = data_file

        return files

    def get_unread_files(self, *args, **kwargs):
        '''
        Get the unread files.

        :param list args: The arguments
        :param dict kwargs: The keyword arguments

        :return: The unread files
        :rtype: list
        '''
        return {
            key: value
            for key, value in self.get_files(*args, **kwargs).items()
            if not value.last_read_date
        }

    def get_latest_file(self, *args, **kwargs):
        '''
        Get the latest file.

        :param list args: The arguments
        :param dict kwargs: The keyword arguments

        :return: The file
        :rtype: CornerDataFile
        '''
        return reduce(
            lambda x, y: y if not x or y.put_date >= x.put_date else x,
            self.get_files(*args, **kwargs).values(),
        )


if __name__ == '__main__':

    #
    # Setup argument parser.
    #

    parser     = ArgumentParser('Cornèr Bank data transfer client')
    subparsers = parser.add_subparsers(dest='command', required=True)

    parser.add_argument('-u', '--username', required=True, help='the username')
    parser.add_argument('-p', '--password', required=True, help='the password')
    parser.add_argument('--url', default=DEFAULT_URL, help='the base URL')

    subparsers.add_parser('latest')
    subparsers.add_parser('list')
    subparsers.add_parser('list-unread')

    download = subparsers.add_parser('download')
    download.add_argument('-n', '--nodecrypt', action='store_false', help='don\'t decrypt the file')
    download.add_argument('filename', help='the filename')
    download.add_argument('destination', help='the destination path')

    args    = parser.parse_args()
    command = args.command

    #
    # Create CornerDataTransfer instance and login.
    #

    transfer = CornerDataTransfer(username=args.username, password=args.password, url=args.url)
    transfer.login()

    #
    # Execute the desired command.
    #

    if command == 'download':
        try:
            transfer.get_files()[args.filename].download(
                destination=args.destination,
                decrypt=args.nodecrypt
            )
        except KeyError as ex:
            raise FileNotFoundError(f'Invalid filename "{args.filename}"') from ex

    elif command == 'latest':
        print(transfer.get_latest_file())

    elif command == 'list':
        for file in transfer.get_files().values():
            print(file.filename)

    elif command == 'list-unread':
        for file in transfer.get_unread_files().values():
            print(file.filename)
