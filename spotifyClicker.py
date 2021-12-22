import constants

import time
import os
import unidecode

from selenium import webdriver
from selenium.webdriver.common.by import By

class SpotifyClicker(object):
    """
    Creates an instance of a driver that go through the task of adding tracks either to favorites playlist or to a new playlist.

    Args:
        username (:obj:`str`):
            Username to login to the Spotify account.
        password (:obj:`str`):
            Password to login to the Spotify account.
    """

    def __init__(self,
                deezer_profile_name,
                username,
                password):

        self.deezer_profile_name = deezer_profile_name
        self.username = username
        self.password = password
        
        self.login()

    def main(self, playlist_name='', start_index=0):
        
        favorite_bool = not bool(playlist_name)
        is_new_playlist = not bool(start_index)
        playlist_name = playlist_name.strip()

        if favorite_bool:
            file = "favorites.txt"
        else:
            file = unidecode.unidecode(playlist_name.replace(" ","_").lower())+".txt"

        dir_file = f"data/{self.deezer_profile_name}/{file}"

        try:
            with open(dir_file) as f:
                self.tracks = f.readlines()
        except OSError as err:
            print("OS error: {0}".format(err))
            
        if favorite_bool:
            self.add_tracks_to_favorites(start_index)
        else:
            if is_new_playlist:
                self.create_playlist(playlist_name)
            self.add_tracks_to_playlist(playlist_name, start_index)
        
        self.write_mistaken_tracks(dir_file)

    def login(self):
        options = webdriver.ChromeOptions()
        options.add_argument("no-sandbox")
        options.add_argument("--disable-web-security")

        self.driver = webdriver.Chrome(options=options, executable_path='./chromedriver')

        
        self.driver.get("https://accounts.spotify.com/fr/login/?continue=https:%2F%2Fopen.spotify.com%2F__noul__%3Fl2l%3D1%26nd%3D1&_locale=fr-FR")
        time.sleep(2)

        login_mail = self.driver.find_element(By.ID,"login-username")
        login_mail.clear()
        login_mail.send_keys(self.username)

        login_password = self.driver.find_element(By.ID,"login-password")
        login_password.clear()
        login_password.send_keys(self.password)

        login_form_submit = self.driver.find_element(By.ID,"login-button")
        login_form_submit.click()

        #Accept cookies
        time.sleep(10)

        login_form_submit = self.driver.find_element(By.ID,"onetrust-accept-btn-handler")
        login_form_submit.click()

        self.driver.get("https://open.spotify.com/search")
    
    def create_playlist(self, playlist_name):
        new_playlist = self.driver.find_element(By.XPATH,f"//button[@data-testid='create-playlist-button']")
        new_playlist.click()
        time.sleep(3)

        edit_playlist = self.driver.find_element(By.XPATH,f"//section[@data-testid='playlist-page']/div/div[5]/span/button")
        edit_playlist.click()
        time.sleep(1)
        edit_playlist_name = self.driver.find_element(By.XPATH,"//input[@data-testid='playlist-edit-details-name-input']")
        edit_playlist_name.clear()
        edit_playlist_name.send_keys(f"{playlist_name}")
        edit_playlist_name = self.driver.find_element(By.XPATH,"//button[@data-testid='playlist-edit-details-save-button']")
        edit_playlist_name.click()

    def add_tracks_to_playlist(self, playlist_name, start_index):
        self.driver.get("https://open.spotify.com/search")
        time.sleep(constants.LOADING_TRACK_SEARCH_SPOTIFY_TIME)
        self.mistaken_tracks = []
        
        for index, track in enumerate(self.tracks):
            if index >= start_index:
                search = self.driver.find_element(By.XPATH,f"//form[@role='search']/input")
                search.clear()
                search.send_keys(f"{track}")
                time.sleep(constants.LOADING_TRACK_SEARCH_SPOTIFY_TIME)

                #Try to add the track to playlist
                try:
                    add_track_to_playlist = self.driver.find_element(By.XPATH,"//div[@role='row' and @aria-rowindex='1']/div/div[2]/button[@aria-haspopup='menu']")
                    add_track_to_playlist.click()

                    time.sleep(1)
                    add_track_to_playlist = self.driver.find_element(By.XPATH,"//ul[@class='SboKmDrCTZng7t4EgNoM']/li[7]")
                    add_track_to_playlist.click()

                    add_track_to_playlist = self.driver.find_element(By.XPATH,f"//ul[@class='SboKmDrCTZng7t4EgNoM']/li[7]/div/ul/li/button/span[contains(text(), '{playlist_name}')]")
                    add_track_to_playlist.click()
                except Exception:
                    self.mistaken_tracks.append(track)
                    pass

                #In case the song is already in the playlist
                try:
                    time.sleep(constants.SPOTIFY_POPUP_TIME)
                    self.driver.find_element(By.XPATH,"//button[@class='Qt5xfSWikz6CLU8Vobxs pWY0RsrzxnQm9yHtovC8']").click()
                except Exception:
                    pass
    
    def add_tracks_to_favorites(self, start_index):
        self.mistaken_tracks = []
        for index, track in enumerate(self.tracks):
            if index >= start_index:
                search = self.driver.find_element(By.XPATH,f"//form[@role='search']/input")
                search.clear()
                search.send_keys(f"{track}")
                time.sleep(constants.LOADING_TRACK_SEARCH_SPOTIFY_TIME)
                try:
                    add_track_to_favorite = self.driver.find_element(By.XPATH,f"//div[@role='row' and @aria-rowindex='1']/div/div[2]/button[@role='switch']")
                    if add_track_to_favorite.get_attribute("aria-checked") == "false":
                        add_track_to_favorite.click()
                except Exception:
                    self.mistaken_tracks.append(track)
                    pass

    def write_mistaken_tracks(self, file):
        dot_index = file.find(".")
        mistaken_file = file[:dot_index] + "_mistakes" + file[dot_index:]

        with open(mistaken_file, "w") as textfile:
            for mistaken_track in self.mistaken_tracks:
                textfile.write(mistaken_track)