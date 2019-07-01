from mutagen.mp3 import EasyMP3
from mutagen.easyid3 import EasyID3KeyError
from pathlib import Path

class Song:

    # Description
    title = ""

    # Media
    artist = ""
    album_artist = ""
    album = ""
    year = ""
    length = ""

    # Audio
    bitrate = ""

    # Content
    composers = ""

    # File
    folder_path = ""
    type = ""


    def __init__(self, path=None):
        if path:
            self.folder_path = path


    def set_metadata(self):
        if not self.folder_path:
            print("[set_metadata] ERROR, NO FOLDER PATH ")
            return

        if Path(self.folder_path).suffix == ".mp3":
            songinfo = EasyMP3(r''+self.folder_path)
            songinfo_tags = songinfo.tags
            self.title          = self.set_tag_securely(songinfo_tags, "title")
            self.artist         = self.set_tag_securely(songinfo_tags, "artist")
            self.album_artist   = self.set_tag_securely(songinfo_tags, "albumartist")
            self.album          = self.set_tag_securely(songinfo_tags, "album")
            self.year           = self.set_tag_securely(songinfo_tags, "date")
            self.composers      = self.set_tag_securely(songinfo_tags, "composer")

            self.length         = songinfo.info.length
            self.bitrate        = songinfo.info.bitrate
            self.type           = ".mp3"


    def set_tag_securely(self, tags, tagname):
        # Seteo una tag de la clase en especifico asegurandome que esa tag exista en mutagen
        value = ""
        try:
            value = tags[tagname][0]
        except EasyID3KeyError:
            pass
        except KeyError:
            print("KEY ERROR CON ", tagname)
        return value
