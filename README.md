![logo](https://github.com/Shinyoro/lovelive_songs_fandom/blob/master/logo.jpg)

# Love Live! songs from Fandom Wiki
Python script that allows you to download all songs from the site fandom.com

## Requirements
  * [Python 3.X](https://python.org/)
  * [requests](https://pypi.org/project/requests/)
  * [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
  * [lxml](https://pypi.org/project/lxml/)

## Executable files
  * [Releases](https://github.com/Shinyoro/lovelive_songs_fandom/releases)

## Usage

### How to download songs
 1. Clone the repository:

    `git clone https://github.com/Shinyoro/lovelive_songs_fandom/`

 2. Install required dependencies:

    `python3 -m pip install -r requirements.txt`

 3. Run the source code file `lovelive_songs_fandom.py`:

    `python3 lovelive_songs_fandom.py`

 4. You will be prompted to update the song list.
    To run the script for the first time, be sure to agree,
    otherwise a message will appear about the absence of song lists from the JSON file:
    `Unable to start download! The list of songs needs to be updated. Please update it with the method "update_list_songs()"`.

 5. Specify the number of threads to execute. Be careful!. Default 1.

 6. Determine if you would like to download songs with art. FFmpeg utility required. Default "No".

 7. Select the groups of songs you want to download.
    If you want to download everything, leave the field empty

This will start retrieving song link lists from all groups.
Unavailable links are written to the file `error_links.txt`

After receiving the list, wait until all the songs are installed in the "Love Live!" folder next to the script.
Please note that installed songs will not be downloaded again.

### If there are new songs on Love Live Fandom Wiki
To download new songs, you also need to run the source code file from step 3 and update the song list.

## Using a script as a module

### Description
The script contains the `LL_Songs` class which has methods:

  * `get_url_fandom()` - Returns the main url address of love live fandom.

  * `get_url_groups(groups=())` - Returns additional group addresses (available: "Muse", "Aqours_SaintSnow", "Nijigasaki").

  Returns everything with no arguments.

  Takes a list of groups as strings to the argument "groups" (default "all").

  * `update_list_songs(threads_count=1)` - Creates / Updates a list of song links. The list is saved in the JSON file.
  Returns a dictionary list of songs from different groups with a link to the song and art, the title of the song and file format.
  Unavailable links are written in the file "error_links.txt".

  Takes a integer number of threads to the argument "threads_count" (default 1).

  * `download_list_songs(groups=(), art=False, threads_count=1)` - Starts downloading songs.
  The list is taken from the JSON file. Returns True if download is complete.

  Takes a list of groups as strings to the argument "groups" (default "all").

  Takes boolen value to the argument "art" for downloading songs with art (default False).
  Requires utility "ffmpeg" for download with art.

  Takes a integer number of threads to the argument "threads_count" (default 1).
