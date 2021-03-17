#!/usr/bin/env python3

# Modules.
from os import rmdir, mkdir, makedirs, remove
from requests import get
from sys import platform
from subprocess import call, DEVNULL
from bs4 import BeautifulSoup as bs
from threading import Thread
from time import sleep
from json import dumps, load, loads
from json.decoder import JSONDecodeError
from urllib.request import urlopen

# A class that will handle songs.
class LL_Songs:
    def __init__(self): # Initialization const variables.

        # Source of songs (Note: Do not edit these variables).
        self.__URL_FANDOM = 'http://love-live.fandom.com/api.php' # The URL of the main API.
        self.__URL_GROUPS = {
				# Pages of groups and its class.
                'Muse'             : ['Love_Live!',                                  'text_m'  ],
                'Aqours_SaintSnow' : ['Love_Live!_Sunshine!!',                       'text_aq' ],
                'Nijigasaki'       : ['Love_Live!_Nijigasaki_High_School_Idol_Club', 'text_ng' ],
                'Liella!'          : ['Love_Live!_Super_Star!!',                     'text_li' ]
        }


    # Returns the URL of the main API.
    def get_url_fandom(self):
        return self.__URL_FANDOM


    # Takes a list of groups as strings to the argument "groups" (default "all").
    # Returns a dictionary of pages of groups and its class.
    def get_url_groups(self, groups=()):
        if not groups:
            return self.__URL_GROUPS # Returns all pages of groups and its class with no arguments.

        list_url_groups = {}

        for group in groups: # Checking for the existence of a group.
            try:
                list_url_groups[group] = self.__URL_GROUPS[group]
            except KeyError:
                print('No', group, 'found. Available only', tuple(self.__URL_GROUPS.keys()))

        return list_url_groups


    # Creates or updates a list of song URLs.

    # Returns a dictionary list of songs from all different groups
    # with the UTL to the song and art, the title of the song and file format.

    # The list is saved in the JSON file.
    # Unavailable URLs will be written in the file "error_links.txt".

    # Takes a integer number of threads to the argument "threads_count" (default 1).
    def update_list_songs(self, threads_count=1):

        def init_bs(page, fix_page=False): # Initialization object of BeautifulSoup for search tags.
            if fix_page:
                html = get(self.__URL_FANDOM + '?page=' + page, params={'action' : 'parse', 'format' : 'json'})
            else:
				# Fixing page if it contains invalid characters.
                html = get(self.__URL_FANDOM, params={'action' : 'parse', 'page' : page, 'format' : 'json'})

            # Returns ready object.
            return bs(loads(html.text)['parse']['text']['*'], 'lxml')

        def get_info_song(song): # Takes URL to a page of song and checks for its availability.
            nonlocal list_songs, error_links # Variables for writing data.

            try:
                html = init_bs(song, fix_page=True)

                original_link = html.find('source').attrs['src'] # Searching audio.

                # Searching art of audio.
                original_link_art = html.find('img', attrs={'class' : 'pi-image-thumbnail'})

                # Writing the received data to "list_song".
                list_songs[song] = [original_link,
                                    '/'.join(original_link_art.attrs['src'].split('/')[:-4]),
                                    '.' + original_link.split('/')[-3].split('.')[-1]]

                print('Getted:', song)
            except (IndexError, AttributeError):

				# Writting unavailable song to the file "error_links.txt"
                error_links.write(song + '\n')
                error_links.flush()
                print('Error:', song)

        error_links = open('error_links.txt', 'w')
        groups_links_songs = {}

        for group in self.__URL_GROUPS:
            print('Getting URLs to a list of songs', group, end='\n\n')

			# Searching all "div" tags with class of group.
            html = init_bs(self.__URL_GROUPS[group][0]).find_all('div', attrs={'class' : self.__URL_GROUPS[group][1]})

            links_list_songs = []

			# Searching all URLs of songs in "div" tags and writing to "list_songs".
            for i in html:
                for a in i.find_all('a'):
                    try:
                        if 'wiki' in a.attrs['href']:
                            links_list_songs.append(a.attrs['href'][6:])
                    except KeyError:
                        pass

            list_songs = {}

            # Comparing the number of threads to the number of songs if they are more oh them.
            if threads_count > len(links_list_songs):
                threads_count = len(links_list_songs)

            # Creating threads for getting songs.
            if threads_count == 1:
                for song in links_list_songs:
                    get_info_song(song)
            else:
                threads = []
                for song in links_list_songs:
                    threads.append(Thread(target=get_info_song, args=(song,)))
                    threads[-1].start()

                    while True:
                        if len(threads) < threads_count:
                            break
                        else:
                            for thread in threads:
                                if not thread.is_alive():
                                    threads.remove(thread)
                                sleep(0.1)

				# Waiting for the end of all theads.
                while threads:
                    for thread in threads:
                        if not thread.is_alive():
                            threads.remove(thread)
                        sleep(0.1)

            # Writing the resulting song list to their group.
            groups_links_songs[group] = list_songs

            print()

        print('Writing the resulting database of songs to a JSON file')

        open('groups_links_songs.json', 'w').write(dumps(groups_links_songs))

        error_links.close()

		# Checking for unavailable songs.
        if open('error_links.txt').readline() != '':
            print('There are non-downloadable links. They are written to a file "error_links.txt"')

        print('Receipt completed', end='\n\n')

        return groups_links_songs

    # Downloads songs. The list is taken from the JSON file. Returns True if download is complete.

    # Takes a list of groups as strings to the argument "groups" (default "all").

    # Takes boolen value to the argument "art" for downloading songs with art (default False).
    # Requires utility "ffmpeg" for download with art.

    # Takes a integer number of threads to the argument "threads_count" (default 1).
    def download_list_songs(self, groups=(), art=False, threads_count=1):

        def get_file(url, path): # Downloading and writing a file to disk.
            handle = urlopen(url)

            with open(path, 'wb') as fetched_file:
                while True:
                    chunk = handle.read(1024)
                    if not chunk:
                        break
                    fetched_file.write(chunk)
                    fetched_file.flush()

        def download_song(song): # Downloading song
			# Vairables for counting downloaded songs and for downloading song with art.
            nonlocal downloaded_files, installed_files, art

			# Checking for existing song.
            try:
                try:
                    open(path + song + list_songs_group[song][2], 'rb')
                except FileNotFoundError:
                    open(path + song + '.mp3', 'rb')
                installed_files += 1
            except FileNotFoundError: # Downloading song if not be found.
                if art: # If art is True download song with art.
                    try:
                        name_art = list_songs_group[song][1].split('/')[-1]

                        get_file(list_songs_group[song][1], tmp_dir + name_art)
                        get_file(list_songs_group[song][0], tmp_dir + song + list_songs_group[song][2])
                        print('Downloaded:', song)

						# Starting FFmpeg utility for adding art to the song.
                        call(['ffmpeg', '-y',
                                '-i', tmp_dir + song + list_songs_group[song][2],
                                '-i', tmp_dir + name_art,
                                '-map', '0',
                                '-map', '1',
                                '-ab', '320k',
                                '-f', 'mp3',
                                path + song + '.mp3'], stderr=DEVNULL)

						# Clearing temp files.
                        for f in [name_art, song + list_songs_group[song][2]]:
                            remove(tmp_dir + f)

                        print('Written down to file:', path + song + '.mp3')
                    except KeyboardInterrupt:
                        for f in [name_art, song + list_songs_group[song][2]]:
                            remove(tmp_dir + f)
                        raise KeyboardInterrupt
                else:
                    get_file(list_songs_group[song][0], path + song + list_songs_group[song][2])
                    print('Downloaded:', song)
                    print('Written down to file:', path + song + list_songs_group[song][2])

                downloaded_files += 1
                installed_files += 1

        downloaded_files = 0
        installed_files  = 0

        try: # Loading database of songs from the JSON file.
            list_songs = load(open('groups_links_songs.json'))
        except (FileNotFoundError, JSONDecodeError):
            print('Unable to start download! The list of songs needs to be updated. Please update it with the method "update_list_songs()"')
            return False

        print('Download starts')

		# Making temp dir.
        try:
            if platform == 'win32':
                tmp_dir = 'C:\\Windows\\Temp\\lovelive_songs_fandom\\'
            else:
                tmp_dir = '/tmp/lovelive_songs_fandom/'
            mkdir(tmp_dir)
        except FileExistsError:
            rmdir(tmp_dir)
            mkdir(tmp_dir)

        if not groups:
            groups = list_songs.keys()

        for group in groups:
            try: # Checking for the existence of a group.
                list_songs_group = list_songs[group]
            except KeyError:
                print('No', group, 'found. Available only', tuple(self.__URL_GROUPS.keys()))
                continue

			# Making dir from the full path.
            if platform == 'win32':
                path = 'Love Live!' + '\\' + group + '\\'
            else:
                path = 'Love Live!' + '/' + group + '/'

            try:
                makedirs(path)
            except FileExistsError:
                pass

			# Threads.
            if threads_count > len(list(list_songs_group)):
                threads_count = len(list(list_songs_group))

            if threads_count == 1:
                for song in list_songs_group:
                    download_song(song)
            else:
                threads = []
                for song in list_songs_group:
                    threads.append(Thread(target=download_song, args=(song,)))
                    threads[-1].start()

                    while True:
                        if len(threads) < threads_count:
                            break
                        else:
                            for thread in threads:
                                if not thread.is_alive():
                                    threads.remove(thread)
                                sleep(0.1)

                while threads:
                    for thread in threads:
                        if not thread.is_alive():
                            threads.remove(thread)
                        sleep(0.1)

        print('Download completed.', downloaded_files, 'files downloaded.', installed_files, 'files written.')

		# Cleaning temp files.
        rmdir(tmp_dir)

        return True

if __name__ == '__main__':

    LL = LL_Songs()

    try:

        update = input('Update the song list? (Recommended) [Y/n] ')
        threads = input('Number of executing threads (Be careful!) (default 1) ')

        if threads == '':
            threads = 1
        else:
            try:
                threads = int(threads)
            except ValueError:
                print('Error! You must specify a numeric value.')
                exit()

        song_with_art = input('Download songs with arts? (Requires utility "ffmpeg") [y/N] ')

        if song_with_art == '' or song_with_art[0] == 'N' or song_with_art[0] == 'n':
            pass
        else:
            try: # Checking for a FFmpeg utility.
                call('ffmpeg', stderr=DEVNULL)
            except FileNotFoundError:
                print('Error! FFmpeg utility not found. Please, install it.')
                exit()

		# Output of the available groups.
        print('Select the group of songs you want to download:')

        for idx, group in enumerate(tuple(LL.get_url_groups())):
            if idx > 0:
                print(', ', end='')
            print(idx+1, '- ' + group, end='')
        print('\n')

        selected_groups = input('Numbers (default all) ')
        print()

        if update == '' or update[0] == 'Y' or update[0] == 'y':
            LL.update_list_songs(threads_count=threads)

        groups = []

		# Downloading songs of those groups that the user has chosen
		# else everything.
        if selected_groups:
            for count in range(len(tuple(LL.get_url_groups()))):
                if str(count+1) in selected_groups:
                    groups.append(tuple(LL.get_url_groups())[count])

        if song_with_art == '' or song_with_art[0] == 'N' or song_with_art[0] == 'n':
            LL.download_list_songs(groups, threads_count=threads)
        else:
            LL.download_list_songs(groups, art=True, threads_count=threads)

    except KeyboardInterrupt:
        try: # Cleaning temp files if user interrupted the program.
            rmdir(LL.tmp_dir)
        except (AttributeError, FileNotFoundError):
            pass

        print('\nInterrupted by user!')
