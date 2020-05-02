# coding=utf-8
# ---------------------------
#   Import Libraries
# ---------------------------
import codecs
import os
import json

import clr

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# ---------------------------
#   [Required] Script Information
# ---------------------------
ScriptName = "League Script"
Website = "https://twitch.tv/RzR32"
Description = "Send your League of Legends Elo/Mastery in your Stream Chat - Unofficial"
Creator = "RzR32"
Version = "0.1"

# ---------------------------
#   Define Global Variables
# ---------------------------

settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")


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
            # League
            self.SummonerName = "RzR32"
            self.Server = "euw1"
            # Elo
            self.Elo = "!elo"
            self.Cooldown_Elo = 10
            self.Permission_Elo = "Everyone"
            # Mastery
            self.Mastery = "!mastery"
            self.Cooldown_Mastery = 10
            self.Permission_Mastery = "Everyone"
            self.Mastery_count = 3
            # Token
            self.Token = ""

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
    #   Load settings
    global ScriptSettings
    ScriptSettings = Settings(settingsFile)
    return


# ---------------------------
#   [Required] Execute Data / Process messages
# ---------------------------
def Execute(data):
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Elo and Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.Elo, data.User):
        Parent.SendStreamMessage(
            "Time Remaining " + str(Parent.GetUserCooldownDuration(ScriptName, ScriptSettings.Elo, data.User)))

    # Check if the propper command is used, the command is not on cooldown and the user has permission to use the

    # global var
    SummonerName = ScriptSettings.SummonerName
    # Riot Server
    _Server = ScriptSettings.Server
    # Riot Games API Token
    Token = ScriptSettings.Token
    headers = {"X-Riot-Token": Token}
    headers_json = {"content-type": "application/json"}

    # Elo Command #
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Elo and not Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.Elo, data.User) and Parent.HasPermission(data.User,
                                                                                ScriptSettings.Permission_Elo,
                                                                                ScriptSettings.SummonerName):
        Parent.BroadcastWsEvent("EVENT_MINE", "{'show':false}")

        # String for the Summoner ID, needed to do the other request´s
        s_id = ""

        # String´s for the Output
        string_solo = ""
        string_flex = ""
        string_tft = ""

        # String´ to temporarily save the other string´s
        string_type = ""
        string_rank = ""
        string_tier = ""
        string_leaguePoints = ""

        # String for the output
        string_out_elo = ""

        # get SummonerID from summonerName
        url_summonerid = "https://" + _Server + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/"
        result_summonerid = Parent.GetRequest(url_summonerid + SummonerName, headers)
        out_summonerid = result_summonerid.split("\n")

        for s_summonerid in out_summonerid:
            s_summonerid = s_summonerid.replace(",", " ")
            s_summonerid = s_summonerid.replace("{", "").replace("}", "")
            s_summonerid = s_summonerid.replace("\"", "").replace("\\", "")

            if s_summonerid.__contains__("status: 4"):
                Parent.SendStreamMessage("Execution failed! (Client Side)")
                return
            elif s_summonerid.__contains__("status: 5"):
                Parent.SendStreamMessage("Execution failed! (Server Side)")
                return

            if s_summonerid.__contains__("response: id:"):
                s_id = s_summonerid[15:]
                s_id = s_id[:48]

        # get Solo/Flex elo
        url_league = "https://" + _Server + ".api.riotgames.com/lol/league/v4/entries/by-summoner/"
        result_league = Parent.GetRequest(url_league + s_id, headers)
        out_league = result_league.split(",")

        for s_league in out_league:
            s_league = s_league.replace("{", "").replace("}", "")
            s_league = s_league.replace("[", "").replace("]", "")
            s_league = s_league.replace("\"", "").replace("\\", "")

            if s_league.startswith("queueType"):
                string_type = s_league[16:].replace("_", "").replace("SR", "").replace("5x5", "")
            elif s_league.startswith("tier"):
                string_tier = s_league[5:]
            elif s_league.startswith("rank"):
                string_rank = s_league[5:]
            elif s_league.startswith("leaguePoints"):
                string_leaguePoints = s_league[13:]

                if string_type.__contains__("SOLO"):
                    string_solo = string_type + " " + string_tier + " " + string_rank + " " + string_leaguePoints
                elif string_type.__contains__("FLEX"):
                    string_flex = string_type + " " + string_tier + " " + string_rank + " " + string_leaguePoints

        # get TfT elo
        url_tft = "https://" + _Server + ".api.riotgames.com/tft/league/v1/entries/by-summoner/"
        result_tft = Parent.GetRequest(url_tft + s_id, headers)
        out_tft = result_tft.split(",")

        for s_tft in out_tft:
            s_tft = s_tft.replace("{", "").replace("}", "")
            s_tft = s_tft.replace("[", "").replace("]", "")
            s_tft = s_tft.replace("\"", "").replace("\\", "")

            if s_tft.startswith("queueType"):
                string_type = s_tft[16:].replace("_", "").replace("SR", "").replace("5x5", "")
            elif s_tft.startswith("tier"):
                string_tier = s_tft[5:]
            elif s_tft.startswith("rank"):
                string_rank = s_tft[5:]
            elif s_tft.startswith("leaguePoints"):
                string_leaguePoints = s_tft[13:]

                string_tft = string_type + " " + string_tier + " " + string_rank + " " + string_leaguePoints

        # OUTPUT
        if string_solo.__eq__(""):
            string_solo = "SOLL Unranked"
        if string_flex.__eq__(""):
            string_flex = "FLEX Unranked"
        if string_tft.__eq__(""):
            string_tft = "TFT Unranked"

        string_out_elo = " ♦ " + string_solo + " ♦ " + string_flex + " ♦ " + string_tft + " ♦ "
        Parent.SendStreamMessage(string_out_elo)

        # Put the Command - Elo on cooldown
        Parent.AddUserCooldown(ScriptName, ScriptSettings.Elo, data.User,
                               ScriptSettings.Cooldown_Elo)

    # Mastery Command #
    elif data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Mastery and not Parent.IsOnUserCooldown(
            ScriptName, ScriptSettings.Mastery, data.User) and Parent.HasPermission(data.User,
                                                                                    ScriptSettings.Permission_Mastery,
                                                                                    ScriptSettings.SummonerName):
        Parent.BroadcastWsEvent("EVENT_MINE", "{'show':false}")

        # Start int for Count
        int_to_count = 0
        # End int for Count
        int_config = ScriptSettings.Mastery_count

        # String for the Summoner ID, needed to do the other request´s
        s_id = ""

        # String´s for Champion
        string_champion_id = ""
        string_champion_level = ""
        string_champion_points = ""

        # Strings´s for ID in NAME
        string_key = ""
        string_id = ""

        # String for the output
        string_out_mastery = ""

        # Game Version
        s_game_verions = ""

        # get latest game version
        response_game_version = Parent.GetRequest("https://ddragon.leagueoflegends.com/api/versions.json",
                                                  headers_json)
        out_game_version = response_game_version.split(',')

        file_path___champ_ID = "Services/Scripts/League/Champion_ID.txt"
        file_champ_ID = open(file_path___champ_ID, "w+")

        for s_game_verions in out_game_version:
            s_game_verions = s_game_verions.replace("[", "").replace("\"", "").replace("\\", "")

            if s_game_verions.__contains__("response"):
                s_game_verions = s_game_verions[14:]
                # check if file already exist
                if os.path.isfile(file_path___champ_ID):
                    # Check Version in File
                    with open(file_path___champ_ID, "r") as file:
                        first_line = file.readline()
                        if not first_line.__contains__(s_game_verions):
                            # version is the another, remake text file
                            file_champ_ID.write("Version: " + s_game_verions + "\n\n")
                            s_game_verions = "Y " + s_game_verions
                        else:
                            s_game_verions = "N " + s_game_verions
                        break
                else:
                    # recreate file
                    file_champ_ID.write("Version: " + s_game_verions + "\n\n")
                    s_game_verions = "Y " + s_game_verions
                break

        if s_game_verions.startswith("Y "):
            # string_champion_id to string_champion_name
            response_summoner_name = Parent.GetRequest("https://ddragon.leagueoflegends.com/cdn/" + s_game_verions[2:] +
                                                       "/data/de_DE/champion.json", headers_json)
            out_summoner_name = response_summoner_name.split(',')

            for s_summoner_name in out_summoner_name:
                s_summoner_name = s_summoner_name.replace("\"", "").replace("\\", "")

                if s_summoner_name.startswith("id"):
                    string_id = s_summoner_name[3:]

                elif s_summoner_name.startswith("key"):
                    string_key = s_summoner_name[4:]

                    # Write new File with "id + key"
                    file_champ_ID.write(" " + string_key + ":" + string_id + "\n")

        file_champ_ID.close()

        # get SummonerID from summonerName
        url_summonerid = "https://" + _Server + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/"
        result_summonerid = Parent.GetRequest(url_summonerid + SummonerName, headers)
        out_summonerid = result_summonerid.split("\n")

        for s_summonerid in out_summonerid:

            s_summonerid = s_summonerid.replace(",", " ")
            s_summonerid = s_summonerid.replace("{", "").replace("}", "")
            s_summonerid = s_summonerid.replace("\"", "").replace("\\", "")

            if s_summonerid.__contains__("status: 4"):
                Parent.SendStreamMessage("Execution failed! (Client Side)")
                return
            elif s_summonerid.__contains__("status: 5"):
                Parent.SendStreamMessage("Execution failed! (Server Side)")
                return

            if s_summonerid.__contains__("response: id:"):
                s_id = s_summonerid[15:]
                s_id = s_id[:48]

                # get mastery from user
                url_champion_mastery = "https://" + _Server + ".api.riotgames.com/lol/champion-mastery/v4" \
                                                              "/champion-masteries/by-summoner/" + s_id
                response_champion_mastery = Parent.GetRequest(url_champion_mastery, headers)

                out_champion_mastery = response_champion_mastery.split(",")

                for s_champion_mastery in out_champion_mastery:
                    s_champion_mastery = s_champion_mastery.replace("{", "").replace("}", "") \
                        .replace("[", "").replace("]", "").replace("\"", "").replace("\\", "").strip()

                    if s_champion_mastery.startswith("response: championId:"):
                        string_champion_id = s_champion_mastery[21:]

                    elif s_champion_mastery.startswith("championId:"):
                        string_champion_id = s_champion_mastery[11:]

                    elif s_champion_mastery.startswith("championLevel:"):
                        string_champion_level = s_champion_mastery[14:]

                    elif s_champion_mastery.startswith("championPoints:"):
                        string_champion_points = s_champion_mastery[15:]

                    if s_champion_mastery.startswith("summonerId"):
                        if int_to_count < int_config:
                            int_to_count += 1

                            file_champ_ID = open(file_path___champ_ID, "r")

                            Lines = file_champ_ID.readlines()

                            for line in Lines:
                                line = line.strip()
                                line = " " + line
                                if line.startswith(" " + string_champion_id + ":"):
                                    string_out_mastery = string_out_mastery + " ♦ " + int_to_count.__str__() + \
                                                         ". Champion: " + line[line.find(":") + 1:] + \
                                                         ", Level: " + string_champion_level + \
                                                         ", Points: " + string_champion_points
                                    file_champ_ID.close()

                        else:
                            break
        # OUTPUT
        Parent.SendStreamMessage(string_out_mastery + " ♦ ")

        # Put the Command - Mastery on cooldown
        Parent.AddUserCooldown(ScriptName, ScriptSettings.Mastery, data.User, ScriptSettings.Cooldown_Mastery)
    return


# ---------------------------
# Open the Riot Games Developer website
# ---------------------------
def OpenReadAPI():
    os.system("start \"\" https://developer.riotgames.com/")


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
