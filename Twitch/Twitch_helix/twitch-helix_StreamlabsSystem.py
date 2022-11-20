# coding=utf-8
# ---------------------------
#   Import Libraries
# ---------------------------
import codecs
import os
import json
import threading
from datetime import datetime

import clr

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# ---------------------------
#   [Required] Script Information
# ---------------------------
ScriptName = "Twitch (helix) Clip/Video Script"
Website = "https://twitch.tv/RzR32"
Description = "If a new Clip/Video get create, send a message in the chat with the link"
Creator = "RzR32"
Version = "0.1"

# ---------------------------
#   Define Global Variables
# ---------------------------

settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
# Path for the clip file
file_latest_clip_path = "Services/Scripts/Twitch_helix/latest_clip.txt"
file_latest_video_path = "Services/Scripts/Twitch_helix/latest_video.txt"


# ---------------------------------------
# Classes
# ---------------------------------------
class Settings:
    """" Loads settings from file if file is found if not uses default values"""

    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsFile=None):
        if settingsFile and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')

        else:  # set variables if no settings file is found
            # Twitch
            self.Twitchname = "RzR32"
            # Clips
            self.Clips = True
            self.Clips_Limit = 10
            self.Clips_StartDate = "2019-01.25"
            self.Clips_Usage = "Stream Chat"
            # Videos
            self.Videos = True
            self.Videos_Limit = 10
            self.Videos_Archive = True
            self.Videos_Upload = True
            self.Videos_Broadcast = True
            self.Videos_Usage = "Stream Chat"
            # Token
            self.Token = ""
            # Query
            self.Query = 5

    # Reload settings on save through UI
    def Reload(self, data):
        """Reload settings on save through UI"""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')

    def Save(self, settingsfile):
        """ Save settings contained within the .json and .js settings files. """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8", ensure_ascii=False)
            with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8', ensure_ascii=False)))
        except ValueError:
            Parent.Log(ScriptName, "Failed to save settings to file.")


# ---------------------------
#   [Required] Initialize Data (Only called on load)
# ---------------------------
def Init():
    # Load settings
    global ScriptSettings
    ScriptSettings = Settings(settingsFile)
    return


# ---------------------------
#   make the request
# ---------------------------
def twitch_request():
    username = ScriptSettings.Twitchname
    user_id = ""
    Token = ScriptSettings.Token

    # Get user_id from username
    URL_user = "https://api.twitch.tv/helix/users?login=" + username
    r_user = Parent.GetRequest(URL_user, headers={"client-id": Token})
    out = r_user.split(",")
    for string in out:
        if string.__contains__("id"):
            string = string.replace("\\", "").replace("\"", "")
            user_id = string[25:]
    # Get user_id from username

    # CLIP
    if ScriptSettings.Clips:
        creator_name = ""
        id = ""
        # up to 100
        limit = int(ScriptSettings.Clips_Limit)
        #
        lines = ""

        started_at = ScriptSettings.Clips_StartDate + "T00:00:00Z"

        year = datetime.today().strftime('%Y')
        month = datetime.today().strftime('%m')
        day = int(datetime.today().strftime('%d')) + 1
        ended_at = year + "-" + month + "-" + day.__str__() + "T00:00:00Z"

        # MAKE REQUEST FOR TWITCH CLIPS
        url_clips = "https://api.twitch.tv/helix/clips?broadcaster_id=" + user_id + "&started_at=" + started_at + "&ended_at=" + ended_at + "&first=" + limit.__str__()
        r_clip = Parent.GetRequest(url_clips, headers={"client-id": Token})

        clip_in_one_string = r_clip.split("{")

        # get the whole file as 'lines'
        if os.path.isfile(file_latest_clip_path):
            with open(file_latest_clip_path, "r") as f:
                lines = f.read().splitlines()

        # open the file to read to it
        file_latest_clip = open(file_latest_clip_path, "ab")

        for all_clips in reversed(clip_in_one_string):
            all_clips = all_clips.replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '') \
                .replace("{", "").replace("}", "").replace("\\", "").replace("\"", "")

            if all_clips.__contains__("id"):
                string_clip = all_clips.split(",")

                for one_clip in string_clip:

                    if one_clip.startswith("id:"):
                        id = "https://clips.twitch.tv/" + one_clip[3:]

                    if one_clip.startswith("creator_name:"):
                        creator_name = one_clip[13:]

                        if not lines.__contains__(id):
                            file_latest_clip.write(id + "\n")
                            if ScriptSettings.Clips_Usage == "Stream Chat" or ScriptSettings.Clips_Usage == "Chat Both":
                                Parent.SendStreamMessage("'" + creator_name + "' has created a Clip > " + id)
                            if ScriptSettings.Clips_Usage == "Discord Chat" or ScriptSettings.Clips_Usage == "Chat Both":
                                Parent.SendDiscordMessage("'" + creator_name + "' has created a Clip > " + id)

        file_latest_clip.close()
    # CLIP
    # VIDEO
    if ScriptSettings.Videos:
        creator_name = ""
        type = ""
        url = ""
        #
        archive = ScriptSettings.Videos_Archive  # <- recent streams
        upload = ScriptSettings.Videos_Upload  # <- video uploaded
        broadcast = ScriptSettings.Videos_Broadcast  # <- highlight
        #
        extra = ""
        # up to 100
        limit = int(ScriptSettings.Videos_Limit)

        if archive:
            extra = extra + "&type=archive"
        if upload:
            extra = extra + "&type=upload"
        if broadcast:
            extra = extra + "&type=highlight"

        url_video = "https://api.twitch.tv/helix/videos?user_id=" + user_id + extra + "&first=" + limit.__str__()

        r = Parent.GetRequest(url_video, headers={"client-id": Token})

        video_in_one_string = r.split("{")

        # get the whole file as 'lines'
        if os.path.isfile(file_latest_video_path):
            with open(file_latest_video_path, "r") as f:
                lines = f.read().splitlines()

        # open the file to read to it
        file_latest_video = open(file_latest_video_path, "ab")

        for all_videos in reversed(video_in_one_string):
            all_videos = all_videos.replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '') \
                .replace("{", "").replace("}", "").replace("\\", "").replace("\"", "")

            if not all_videos.startswith("id"):
                if all_videos.__contains__("type"):
                    for get_type in all_videos.split(","):
                        if get_type.startswith("type:"):
                            type = get_type[5:]

            if all_videos.startswith("id:"):
                string_clip = all_videos.split(",")

                for one_video in string_clip:

                    if one_video.startswith("user_name:"):
                        creator_name = one_video[10:]

                    if one_video.startswith("url:https://www.twitch.tv/videos/"):
                        url = one_video[4:]

                        if not url == "":
                            if not lines.__contains__(url):
                                file_latest_video.write(url + "\n")
                                if ScriptSettings.Videos_Usage == "Stream Chat" or ScriptSettings.Videos_Usage == "Chat Both":
                                    Parent.SendStreamMessage("Neues Video bei '" + creator_name + "' (" + type + ") " + url)
                                if ScriptSettings.Videos_Usage == "Discord Chat" or ScriptSettings.Videos_Usage == "Chat Both":
                                    Parent.SendDiscordMessage("New Video by '" + creator_name + "' (" + type + ") " + url)

        file_latest_video.close()
        # VIDEO


# ---------------------------
#   [Required] Execute Data / Process messages
# ---------------------------
def Execute(data):
    return


# ---------------------------
# Open the Riot Games Developer website
# ---------------------------
def OpenReadAPI():
    os.system("start \"\" https://dev.twitch.tv/console")


# ---------------------------
# Open the Riot Games Developer website
# ---------------------------
def del_latest_clip():
    os.remove(file_latest_clip_path)


# ---------------------------
# Open the Riot Games Developer website
# ---------------------------
def del_latest_videos():
    os.remove(file_latest_video_path)


# ---------------------------
# Make the Request one time - manuel
# ---------------------------
def start():
    twitch_request()


# ---------------------------
# Make the Request one time and start the timer - manuel
# ---------------------------
def start_Timer():
    twitch_request()
    threading.Timer(ScriptSettings.Query * 60, start_Timer).start()


# ---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
# ---------------------------
def Tick():
    return


# ---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
# ---------------------------
def ReloadSettings(jsonData):
    """Reload settings on Save"""
    global ScriptSettings
    ScriptSettings.Reload(jsonData)


# ---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
# ---------------------------
def Unload():
    return


# ---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
# ---------------------------
def ScriptToggled(state):
    return
