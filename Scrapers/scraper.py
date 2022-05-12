import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import re
import os
from PIL import Image
import glob
import sys
import shutil

def strip_tags(html):
    """Permet de supprimer tous les tags HTML d'une chaine de caractère.

    Parameters
    ----------
    html : str
        La chaine de caractère d'entrée.

    Returns
    -------
    str
        La chaine purgée des tous les tags HTML.
    """
    return re.sub("<[^<]+?>", "", html)


def clean_name(name):
    """Permet de supprimer les caractères interdits dans les chemins.

    Parameters
    ----------
    name : str
        La chaine de caractère d'entrée.

    Returns
    -------
    str
        La chaine purgée des tous les caractères non désirés.
    """
    chars = '\\/:*<>?"|'
    for c in chars:
        name = name.replace(c, "_")
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\.+$", "", name)
    name = name.strip()
    return name


def requests_retry_session(
    retries=3,
    backoff_factor=1,
    status_forcelist=(500, 502, 504),
    session=None,
):
    """Permet de gérer les cas simples de problèmes de connexions."""
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session




class Scraper:
    url: str = ""

    def __init__(self):
        pass

    def convert_images(self, folder, format, quality=100):
        """Permet de convertir les images d'un dossier en format spécifié."""
        print(f"Conversion des images au format {format.upper()} (qualité : {quality})", end=" ")
        format = format.lower()
        if format not in ("jpeg", "webp"):
            print("KO")
            return False
        all_files = []
        for ext in ("jpg", "jpeg", "png", "webp", "bmp"):
            all_files.extend(glob.glob(f"{folder}/*.{ext}", recursive=True))
        for filename in all_files:
            new_filename = os.path.splitext(filename)[0] + '.' + format
            im = Image.open(filename)
            im.save(new_filename, format, quality=quality)
            if new_filename != filename:
                os.remove(filename)
            print('.', end="")
            sys.stdout.flush()
        print("OK")
        return True


    def create_cbz(self, folder):
        print("Création du CBZ...", end=" ")
        # Dans le cas où un fichier du même nom existe déjà, on change de nom.
        filler_txt = ""
        if os.path.exists(folder + ".zip"):
            filler_txt += "_"
            max_attempts = 20
            while (
                os.path.exists(folder + filler_txt + ".zip") and max_attempts > 0
            ):
                filler_txt += "_"
                max_attempts -= 1
        shutil.make_archive(folder + filler_txt, "zip", folder)

        filler_txt2 = ""
        if os.path.exists(folder + ".cbz"):
            filler_txt2 += "_"
            max_attempts = 20
            while (
                os.path.exists(folder + filler_txt2 + ".cbz")
                and max_attempts > 0
            ):
                filler_txt2 += "_"
                max_attempts -= 1
        os.rename(folder + filler_txt + ".zip", folder + filler_txt2 + ".cbz")
        print("OK")

