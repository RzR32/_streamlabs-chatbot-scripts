# coding=utf-8
# ---------------------------
#   Import Libraries
# ---------------------------
import codecs
import os
import json
import threading

import clr

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# ---------------------------
#   [Required] Script Information
# ---------------------------
ScriptName = "Twitch (kraken) Clip/Video Script"
Website = "https://twitch.tv/RzR32"
Description = "If a new Clip/Video get create, send a message in the chat with the link"
Creator = "RzR32"
Version = "0.1"

# ---------------------------
#   Define Global Variables
# ---------------------------

settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
# Path for the clip file
file_latest_clip_path = "Services/Scripts/Twitch_kraken/latest_clip.txt"
file_latest_video_path = "Services/Scripts/Twitch_kraken/latest_video.txt"


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
            self.Clips_Period = "day"
            self.Clips_Limit = 10
            self.Clips_Usage = "Stream Chat"
            # Videos
            self.Videos = True
            self.Videos_Archive = True
            self.Videos_Upload = True
            self.Videos_Broadcast = True
            self.Videos_Limit = 10
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
    Token = ScriptSettings.Token

    # CLIP
    if ScriptSettings.Clips:
        period = ScriptSettings.Clips_Period
        limit = int(ScriptSettings.Clips_Limit)
        #
        curator = ""
        slug = ""
        found = 0
        #
        lines = ""

        # MAKE REQUEST FOR TWITCH CLIPS
        url_clips = "https://api.twitch.tv/kraken/clips/top?channel=" + username + "&period=" + period + \
                    "&limit=" + limit.__str__()
        r = Parent.GetRequest(url_clips, headers={"client-id": Token, "accept": "application/vnd.twitchtv.v5+json"})
        clip_in_one_string = r.split("}}")

        # get the whole file as 'lines'
        if os.path.isfile(file_latest_clip_path):
            with open(file_latest_clip_path, "r") as f:
                lines = f.read().splitlines()

        # open the file to read to it
        file_latest_clip = open(file_latest_clip_path, "ab")

        for all_clips in reversed(clip_in_one_string):
            all_clips = all_clips.replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '')\
                .replace("{", "").replace("}", "")

            if all_clips.startswith("\"status\""):
                all_clips = all_clips[35:]

            all_clips = all_clips[1:]

            if all_clips.__contains__("slug"):
                string_clip = all_clips.split(",")

                for one_clip in string_clip:

                    one_clip = one_clip.replace("\"", "").replace("\\", "")

                    if one_clip.startswith("slug:"):
                        slug = "https://clips.twitch.tv/" + one_clip[5:]

                    if one_clip.startswith("name:") and found == 0:
                        found += 1

                    elif one_clip.startswith("name:") and found == 1:
                        found -= 1
                        curator = one_clip[5:]

                        if not lines.__contains__(slug):
                            file_latest_clip.write(slug + "\n")
                            if ScriptSettings.Clips_Usage == "Stream Chat" or ScriptSettings.Clips_Usage == "Chat Both":
                                Parent.SendStreamMessage("'" + curator + "' hat ein Clip erstellt > " + slug)
                            if ScriptSettings.Clips_Usage == "Discord Chat" or ScriptSettings.Clips_Usage == "Chat Both":
                                Parent.SendDiscordMessage("'" + curator + "' hat ein Clip erstellt > " + slug)

        file_latest_clip.close()
    # CLIP
    # VIDEO
    if ScriptSettings.Videos:
        userid = ""
        #
        curator = ""
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

        # get the userid from the streamer
        url_user = "https://api.twitch.tv/kraken/users?login=" + username
        r_user = Parent.GetRequest(url_user, headers={"client-id": Token, "accept": "application/vnd.twitchtv.v5+json"})
        out_user = r_user.split(",")

        for string in out_user:
            if string.__contains__("_id"):
                string = string.replace("\"", "").replace("\\", "").replace(":", "")
                string = string[3:]
                userid = string
        # get the userid from the streamer
        if archive:
            extra = extra + "?broadcast_type=archive"
        if upload:
            extra = extra + "?broadcast_type=upload"
        if broadcast:
            extra = extra + "?broadcast_type=highlight"

        if archive or upload or broadcast:
            url_video = "https://api.twitch.tv/kraken/channels/" + userid.__str__() + "/videos" + extra + \
                        "&limit=" + limit.__str__()
        else:
            url_video = "https://api.twitch.tv/kraken/channels/" + userid.__str__() + "/videos?limit=" + limit.__str__()

        r = Parent.GetRequest(url_video, headers={"client-id": Token, "accept": "application/vnd.twitchtv.v5+json"})
        video_in_one_string = r.replace("{", "").replace("}", "").replace("[", "").replace("]", "") \
            .replace("\"", "").replace("\\", "").split("title")

        # get the whole file as 'lines'
        if os.path.isfile(file_latest_video_path):
            with open(file_latest_video_path, "r") as f:
                lines = f.read().splitlines()

        # open the file to read to it
        file_latest_video = open(file_latest_video_path, "ab")

        for all_videos in reversed(video_in_one_string):
            all_videos = "title" + all_videos

            if all_videos.startswith("title:"):
                string_clip = all_videos.split(",")

                for one_video in string_clip:

                    if one_video.startswith("url:https://www.twitch.tv/videos/"):
                        url = one_video[4:]

                    if one_video.startswith("name:"):
                        curator = one_video[5:]

                    if one_video.startswith("broadcast_type:"):
                        type = one_video[15:]

                        if not url == "":
                            if not lines.__contains__(url):
                                file_latest_video.write(url + "\n")
                                if ScriptSettings.Videos_Usage == "Stream Chat" or ScriptSettings.Videos_Usage == "Chat Both":
                                    Parent.SendStreamMessage("Neues Video bei '" + curator + "' (" + type + ") " + url)
                                if ScriptSettings.Videos_Usage == "Discord Chat" or ScriptSettings.Videos_Usage == "Chat Both":
                                    Parent.SendDiscordMessage("Neues Video bei '" + curator + "' (" + type + ") " + url)

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
