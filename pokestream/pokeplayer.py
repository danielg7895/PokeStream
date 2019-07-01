import vlc
import time
import os
from mutagen import File
import traceback
import threading
from PIL import Image
import io

from .playlist import PlayList

# Actuales dependencias y requisitos:
# 1) vlc, mutagen
# 2) carpeta logs creada en raiz

class PokePlayer:

    playlist = None # playlist que contendra todas las canciones
    playlist_users = []  # playlist que se llenara cuando los usuarios agreguen musica a la cola (muy a futuro)

    track_count = 0

    def __init__(self):
        # Creo instancia y asigno un media player
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()


    def console(self):
        while(True):
            command = input()
            if command == "next":
                # Para hacer next reales tendria que utilizar mediaplayer list ewe
                self.player.stop()


    def addplaylist(self, playlist):
        if isinstance(playlist, PlayList):
            self.playlist = playlist
        else:
            print("ERROR: la playlist enviada no es de tipo PlayList.")
            raise InvalidPlayListType


    def start_playing(self):
        # main loop
        while(True):
            try:
                self._start_playing()
            except Exception as e:
                log_error(traceback.format_exc())
                traceback.print_exc()
                self.playlist.next_song()
                time.sleep(1)


    def _start_playing(self):
        print("Comenzando la reproduccion en 2 segundos")
        time.sleep(2)

        while(True):
            while (self.player.is_playing()):
                # para evitar que la song se pare apenas al comenzar
                time.sleep(1)

            self.playlist.next_song()
            song_path = self.playlist.current.folder_path
            if os.path.exists(song_path):

                self.save_track_count()
                self.save_metadata_to_file()
                self.save_image_to_file()

                self.play(song_path)
            else:
                log_error("[WARNING] no existe el path " + song_path)
                print("WARNING: no existe el path ", song_path)


    def play(self, path):
        # agrego musica al reproductor
        media = self.instance.media_new(path)
        self.player.set_media(media)

        print("Ahora reproduciendo ...", self.playlist.current.title)
        self.player.play()
        time.sleep(5) # tiempo para que comience a reproducir, sino habra problemas


    def save_metadata_to_file(self):
        with open('artist.txt', "w+") as artist:
            artist.write(self.playlist.current.artist)

        with open('title.txt', "w+") as title:
            title.write(self.playlist.current.title)


    def save_image_to_file(self):
        file = File(self.playlist.current.folder_path)
        artwork = ""
        try:
            artwork = file.tags['APIC:'].data
            img = Image.open(io.BytesIO(artwork))
            new_img = img.resize((400,400))
        except KeyError:
            print("Esta imagen no tiene artwork ", self.playlist.current.folder_path)
            return
        new_img.save("album.png", "PNG")



    def save_track_count(self):
        try:
            with open('track_count.txt', 'r+') as track_counter:
                line = track_counter.read()
                self.track_count = 0 if line == "" else int(line)
        except FileNotFoundError:
            # Basicamente no tengo que hacer nada porque si no existe abajo lo crea,
            # y track_count ya es cero porque lo declare al comienzo de la clase.
            pass

        self.track_count += 1

        with open('track_count.txt', 'w+') as track_counter:
            track_counter.write(str(self.track_count))


def log_error(error):
    with open("./logs/error_log.txt", 'a+') as error_log:
        error_log.write(error + "\n")
        print("Error agregado al log_error")


class InvalidPlayListType(Exception) : pass
