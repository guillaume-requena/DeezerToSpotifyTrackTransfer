import constants
import deezerScrapper
import spotifyClicker

import argparse
import time

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '--task-switch',
        type=str,
        help='Decides which task to do',
        default='Deezer'
    )
    parser.add_argument(
        '--username',
        type=str,
        help='Username for the specified login task',
    )
    parser.add_argument(
        '--password',
        type=str,
        help='Password for the specified login task',
    )
    parser.add_argument(
        '--profile-name',
        type=str,
        help='Profile to click on in order to enter in the specified profile account in the family account',
    )
    parser.add_argument(
        '--playlist-name',
        type=str,
        help='What is the name playlist when it is not the Favorites playlist but a task performed on a classic type of playlist',
        default=''
    )
    parser.add_argument(
        '--start-index',
        type=int,
        help='Profile to click on in order to enter in the specified profile account in the family account',
        default=0
    )

    return parser


def main(task_switch,
        username,
        password,
        profile_name,
        playlist_name,
        start_index):

    if task_switch == 'Deezer':
        Deezer = deezerScrapper.DeezerScrapper(profile_name=profile_name,
                                                username=username,
                                                password=password)
        
        #Wait because of the tangible apparition of a captcha
        try:
            Deezer.select_profile()
        except Exception:
            time.sleep(4*constants.REFRESH_PAUSE_TIME)
            Deezer.select_profile()

        #Wait for the loading of the landing page
        time.sleep(constants.REFRESH_PAUSE_TIME)
        Deezer.main(playlist_name=playlist_name)

    elif task_switch == 'Spotify':
        Spotify = spotifyClicker.SpotifyClicker(deezer_profile_name=profile_name,
                                                username=username,
                                                password=password)
        
        #Wait for the loading of the landing page
        time.sleep(constants.REFRESH_PAUSE_TIME)
        Spotify.main(playlist_name=playlist_name,
                    start_index=start_index)

if __name__ == "__main__":
    parser = _build_parser()
    args = parser.parse_args()

    main(task_switch=args.task_switch,
        username=args.username,
        password=args.password,
        profile_name=args.profile_name,
        playlist_name=args.playlist_name,
        start_index=args.start_index)