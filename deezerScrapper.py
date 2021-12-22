import constants

import time
import os
import unidecode

from selenium import webdriver
from selenium.webdriver.common.by import By

class DeezerScrapper(object):
    """
    Creates an instance of a driver that has methods to read the tracks of a specified playlist and write them in a file.
    Args:
        username (:obj:`str`):
            Username to login to the Deezer account.
        password (:obj:`str`):
            Password to login to the Deezer account.
    """

    def __init__(self,
                profile_name,
                username,
                password):

        self.profile_name = profile_name
        self.username = username
        self.password = password
        self.login()
    
    def login(self):
        self.driver = webdriver.Chrome(executable_path='./chromedriver')
        
        self.driver.get("https://www.deezer.com/fr/login")

        time.sleep(constants.COOKIES_PAUSE_TIME)
        #Cookies
        cookies = self.driver.find_element(By.ID,"gdpr-btn-accept-all")
        cookies.click()

        login_mail = self.driver.find_element(By.ID,"login_mail")
        login_mail.clear()
        login_mail.send_keys(self.username)

        login_password = self.driver.find_element(By.ID,"login_password")
        login_password.clear()
        login_password.send_keys(self.password)

        login_form_submit = self.driver.find_element(By.ID,"login_form_submit")
        login_form_submit.click()
    
    def main(self, playlist_name=''):
        favorite_bool = not bool(playlist_name)
        if favorite_bool:
            #Go to favorites
            favorites = self.driver.find_element(By.XPATH,"//span[contains(text(), 'Coups de cœur')]")
            favorites.click()
            time.sleep(2)
            file = "favorites.txt"
        else:
            playlists = self.driver.find_element(By.XPATH,"//span[contains(text(), 'Playlists')]")
            playlists.click()
            time.sleep(1)
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight);")
            playlists = self.driver.find_element(By.XPATH,f"//a[@title='{playlist_name}']")
            self.driver.execute_script("arguments[0].click();", playlists)
            time.sleep(2)
            file = unidecode.unidecode(playlist_name.strip().replace(" ","_").lower())+".txt"

        self.read_tracks(file)

    def select_profile(self):
        #Select the correct profile
        profile = self.driver.find_element(By.XPATH,f"//p[contains(text(), '{self.profile_name}')]")
        profile.click()

    def read_tracks(self, file):
        #Init
        self.tracks = []

        row_count = self.driver.find_element(By.XPATH,"//div[@class='xdRiL']")
        rows = int(row_count.get_attribute("aria-rowcount"))

        self.driver.refresh()
        time.sleep(constants.REFRESH_PAUSE_TIME)
        for row_index in range(1, rows+1):
            self.driver.execute_script(f"window.scrollTo(0, 300+{row_index}*56);")
            # Wait to load page
            time.sleep(constants.SCROLL_PAUSE_TIME)

            try:
                song = self.driver.find_element(By.XPATH,f"//div[@class='YrLz6']/div/div/div[@aria-rowindex='{row_index}']/div/div/div[3]/span")
                song_title = song.text
                artist = self.driver.find_element(By.XPATH,f"//div[@class='YrLz6']/div/div/div[@aria-rowindex='{row_index}']/div/div[2]/div/a")
                artist_name = artist.text

                self.tracks.append((artist_name, song_title))
            except Exception:
                pass
        self.write_tracks(file)
    
    def write_tracks(self, file):
        if not os.path.exists("data/"+self.profile_name+"/"):
            os.makedirs("data/"+self.profile_name)

        dir_file = f"data/{self.profile_name}/{file}"
        with open(dir_file, "w") as textfile:
            for track in self.tracks:
                textfile.write(track[0] + ' ' + track[1] + "\n")