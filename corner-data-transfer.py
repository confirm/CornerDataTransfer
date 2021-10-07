#!/usr/bin/env python3

from argparse import ArgumentParser

from requests import Session

DEFAULT_BASE_URL = 'https://ft.corner.ch/'


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
        return self.file['cwid']

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

    def download(self, destination):
        '''
        Download the file.

        :param str destination: The destination path
        '''
        response = self.session.get(url=self.url, stream=True)
        response.raise_for_status()

        with open(file=destination, mode='wb') as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)


class CornerDataTransfer:
    '''
    The API class to communicate with the Cornèr Bank data transfer HTTPS
    channel / platform.

    :param str username: The username
    :param str password: The password
    :param str url: The base URL
    '''

    def __init__(self, username, password, url=DEFAULT_BASE_URL):
        self.username = username
        self.password = password
        self.url      = url
        self.session  = Session()

    def get_url(self, path):
        '''
        Get the full URL for a path.
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


if __name__ == '__main__':

    parser     = ArgumentParser('Cornèr Bank data transfer client')
    subparsers = parser.add_subparsers(dest='command', required=True)

    parser.add_argument('-u', '--username', required=True, help='the username')
    parser.add_argument('-p', '--password', required=True, help='the password')
    parser.add_argument('--url', default=DEFAULT_BASE_URL, help='the base URL')

    subparsers.add_parser('list')

    download = subparsers.add_parser('download')
    download.add_argument('filename', help='the filename')
    download.add_argument('destination', help='the destination path')

    args    = parser.parse_args()
    command = args.command

    transfer = CornerDataTransfer(username=args.username, password=args.password, url=args.url)
    transfer.login()

    if command == 'download':
        transfer.get_files()[args.filename].download(args.destination)

    elif command == 'list':
        for file in transfer.get_files().values():
            print(file.filename)

