import vlc
import time
import os
import xml.etree.ElementTree as ET
import random
from urllib.parse import unquote  # para decoding
import traceback
import shutil # para copiar archivos
from mutagen.mp3 import MP3
from mutagen import File
import threading

# Actuales dependencias y requisitos:
# 1) vlc, mutagen
# 2) carpeta logs creada en raiz
# 3) playlist de vlc en raiz con nombre playlist.xspf

class PokeStream:

    playlist_vlc = ""
    playlist_vlc_xml = ""
    playlist_default = [] # playlist que contendra todas las canciones
    playlist_users = []  # playlist que se llenara cuando los usuarios agreguen musica a la cola (muy a futuro)

    playlist_vlc_path = "playlist.xspf"
    playlist_vlc_len = 0

    # Play modes, por defecto random. Otros ejemplos: "diamond", "xy", "secuencial", etc
    playmode = "random"

    current_song_metadata = {
            "title": "",
            "composer": "",
            "album": "",
            "tracknumber": "",
            "artist": "",
            "albumartist": "",
            "path": ""
    }

    track_count = 0

    def __init__(self):
        # Creo instancia y asigno un media player
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        print("Cargando playlist...")
        self.load_vlc_playlist()
        if self.playlist_vlc_len <= 0:
            print("ERROR: el tamanio de la playlist es <= a cero")
            return

        # thread para comandos en la consola
        th = threading.Thread(target = self.console).start()
        print("Total Threads ", threading.active_count())

    def console(self):
        while(True):
            command = input()
            if command == "next":
                # Para hacer next reales tendria que utilizar mediaplayer list ewe
                self.player.stop()
            if command == "output":
                op = self.player.audio_output_set("Automatic")
                list = vlc.libvlc_audio_output_list_get(self.player)
                print(list)

    def load_default_playlist(self):
        # Cargo la playlist creada en vlc a la lista playlist_default
        # Por ahora no veo necesario hacer esto, la playlist de vlc trae toda
        # la info necesaria para reproducir y la metadata, pero dejo el codigo por las dudas
        root = ET.parse(playlist_vlc_path).getroot()
        self.playlist_vlc_xml = root

        # Agrego el path de cada song del playlist a playlist_default
        for track in root.findall("./tracklist/track"):
            track_path = track.findall("./location")
            if os.path.exists(track_path):
                playlist_default.append(track_path)
            else:
                log_error("[WARNING] La cancion ubicada en " + track_path + " no existe. Cancion ignorada." + "\n")
                print("[WARNING] La cancion ubicada en " + track_path + " no existe. Cancion ignorada.")

    def load_vlc_playlist(self):
        # Cargo la playlist de vlc a una variable para poder procesarla sin tener
        # que abrir el archivo a cada rato
        if(os.path.exists(self.playlist_vlc_path)):
            with open(self.playlist_vlc_path, 'r') as pl:
                self.playlist_vlc = pl.read().replace('/n', '')

            # Guardo informacion basica de la playlist
            root = ET.parse(self.playlist_vlc_path).getroot()
            self.playlist_vlc_xml = root

            try:
                # Obtengo tamanio de la playlist (hardcodeado)
                self.playlist_vlc_len = int(root[2][-1].get('tid'))
                print("Total canciones: ", self.playlist_vlc_len)
            except ValueError:
                log_error("ERROR: No se pudo convertir el tamanio de la playlist a entero" + "\n")
                print("ERROR: No se pudo convertir el tamanio de la playlist a entero")

    def start_playing(self):
        # main loop
        print("Comenzando la reproduccion en 2 segundos")
        time.sleep(2)

        while(True):
            print(self.player.is_playing())
            while (self.player.is_playing()):
                # para evitar que la song se pare apenas al comenzar
                time.sleep(1)

            if self.playmode == "random":
                random_number = random.randrange(0, self.playlist_vlc_len)
                print("Numero random: " + str(random_number) + " de un total " + str(self.playlist_vlc_len))
                selected_song = self.playlist_vlc_xml[1][random_number] # [1] es la lista de tracks (tracklist)
                selected_song_path = unquote(selected_song[0].text.replace('file:///', ''))
                if os.path.exists(selected_song_path):
                    self.current_song_metadata["path"] = selected_song_path

                    self.save_track_count()
                    self.save_song_metadata(selected_song_path)
                    self.save_metadata_to_file()
                    self.save_image_to_file()

                    self.play(selected_song_path)
                else:
                    log_error("[WARNING] no existe el path " + selected_song_path + ". Numero de song: " + str(random_number) + "\n")
                    print("WARNING: no existe el path ", selected_song_path)

    def play(self, path):
        # agrego musica al reproductor
        media = self.instance.media_new(path)
        self.player.set_media(media)

        print("Ahora reproduciendo ...", self.current_song_metadata["title"])
        self.player.play()
        time.sleep(5) # tiempo para que comience a reproducir, sino habra problemas

    def save_song_metadata(self, path):
        song_info = File(path, easy=True)
        for x in self.current_song_metadata:
            if x == "path": continue
            try:
                self.current_song_metadata[x] = song_info[x][0]
            except KeyError:
                print("No existe la key ", x)

    def save_metadata_to_file(self):
        for x in self.current_song_metadata:
            with open(x + ".txt", "w+", encoding="utf-8") as metadatainfo:
                metadatainfo.write(self.current_song_metadata[x])

    def save_image_to_file(self):
        file = File(self.current_song_metadata["path"])
        artwork = ""
        try:
            artwork = file.tags['APIC:'].data
        except KeyError:
            print("Esta imagen no tiene artwork ", self.current_song_metadata["path"])
            return
        with open('album.jpg', 'wb') as img:
            img.write(artwork)

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


ps = PokeStream()
 # Hack asquqeroso para reiniciar el stream de musica en caso de que suceda un error y muera el reproductor
while(True):
    try:
        ps.start_playing()
    except Exception as e:
        pk = PokeStream()
        log_error(traceback.format_exc())
        traceback.print_exc()

        print("Reiniciando en 10 segundos...")
        time.sleep(10)
