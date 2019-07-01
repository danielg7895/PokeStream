from tkinter import filedialog
import tkinter
from os import listdir, walk
from os.path import isfile, join, isdir, exists
from pathlib import Path
from shutil import copy
from random import shuffle

from .song import Song


class PlayList:

    name = ""
    allowed_extensions = (".mp3", ".wav", ".ogg")
    playlist = []
    url_playlist = [] # usada para guardar y cargar playlist de forma mas facil

    # Play modes, por defecto random. Otros ejemplos: "diamond", "xy", "secuencial", etc
    playmode = "random"

    previous = None
    current = None
    next = None


    def __init__(self, path, playlist_name):
        self.name = playlist_name
        self.load_playlist(path)
        if len(self.url_playlist) > 0:
            for path in self.url_playlist:
                self.playlist.append(Song(path))

            if len(self.playlist) <= 0: # wtf?
                print("Failed to load playlist.")
                raise PlayListNotLoaded
        else:
            print("Failed to load playlist.")
            raise PlayListNotLoaded

        self.sort_playlist(self.playmode)
        self.increase_data()


    def next_song(self):
        self.increase_data()
        if self.current != None:
            self.current.set_metadata()


    def previous_song(self):
        pass


    def sort_playlist(self, sortmode):
        if len(self.playlist) <= 0:
            raise PlayListNotLoaded

        if sortmode == "random":
            shuffle(self.playlist)


    def increase_data(self):
        # Por defecto las canciones siempre se loopean, sino habria que toquetear esto un poco
        # porque cuando se llega al final de la lista, esto comienza de nuevo
        playlist_len = len(self.playlist)
        current_index = 0

        if self.current != None: # significa que ya se inicializo previous, current y next antes
            current_index = self.playlist.index(self.current)

        self.previous = self.playlist[current_index % playlist_len]
        self.current = self.playlist[(current_index + 1) % playlist_len]
        self.next = self.playlist[(current_index + 2) % playlist_len]


    def create_playlist(self):
        # Creo la playlist pidiendo al usuario una carpeta donde estan los archivos de sonidos
        tkinter.Tk().withdraw()
        file_path = filedialog.askdirectory(initialdir = ".", title = "Select folder")
        try:
            self.url_playlist = self.search_sound_files(file_path)
        except FileNotFoundError:
            print("[PlayList][search_sound_files][ERROR] directorio: " + path + " no existe.")

        self.save_playlist()


    def save_playlist(self):
        # Guardo la lista de playlist de la clase en un archivo .pks en la carpeta especificada
        if len(self.url_playlist) > 0:
            str_list = "|".join(self.url_playlist)
            with open("playlist.pks", "w+", encoding="utf-8") as pks:
                pks.write(str_list)
        else:
            print("[ERROR] la playlist que se intenta guardar esta vacia")


    def load_playlist(self, path):
        # abro la playlist del working directory actual con nombre playlist.pks
        # Si no existe, le pido al usuario para buscarla o crearla.
        try:
            with open(path, "r", encoding="utf-8") as pks:
                self.url_playlist = pks.read().split("|")
        except FileNotFoundError:
            print("Error, playlist no encontrada, opciones:")
            print("1) Buscar archivo playlist (.pks)")
            print("2) Crear nueva playlist a partir de una carpeta")
            reply = input()
            if reply == "1":
                # obtengo direccion donde se encuentra el archivo de playlist
                tkinter.Tk().withdraw()
                file_path = filedialog.askopenfilename(initialdir = ".", title = "Select .pks", filetypes=[("Playlist files", "*.pks")])

                # Leo el archivo, lo separo por comas y la agrego a la playlist
                with open(file_path, "r", encoding="utf-8") as pl:
                    self.url_playlist = pl.read().split("|")

            elif reply == "2":
                self.create_playlist()

            else:
                print("Opcion invalida.")


    def search_sound_files(self, path):
        soundfiles = []
        for root, dirs, files in walk(path):
            for sound in files:
                sound = join(root, sound)
                if Path(sound).suffix in self.allowed_extensions:
                    soundfiles.append(sound)
        return soundfiles


class PlayListNotLoaded(Exception): pass
