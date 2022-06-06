import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import re
import os
from PIL import Image
import glob
import sys
import shutil
import cv2
import numpy as np
import math

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

    @staticmethod
    def convert_images(folder, format, quality=100, crop=False):
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
            if not crop:
                im = Image.open(filename)
                if format in ("jpeg") and im.mode in ("RGBA", "P"):
                    im = im.convert("RGB")
                im.save(new_filename, format, quality=quality)
            else:
                img = Scraper.auto_crop(filename)
                Scraper.save_img(img, new_filename, format, quality)
            
            if new_filename != filename:
                os.remove(filename)
            print('.', end="")
            sys.stdout.flush()
        print("OK")
        return True


    @staticmethod
    def create_cbz(folder):
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


    @staticmethod
    def auto_crop(
        img,
        blur=5,
        min_rect_pct=0.05,
        threshold=0,
        threshold_type=cv2.THRESH_BINARY_INV,
        debug=0,
    ):
        """
        Removes useless borders in a cv2 image.

        Parameters
        ----------
        img : str / numpy.ndarray
            Path of image to process.
            or
            cv2 image object to process.
        blur : int (default 5)
            Blur factor in pixels to apply on the grayed picture.
        min_rect_pct : float (default 0.05)
            All shapes smaller than min_rect_pct percent of the original image will be ignored.
        threshold : float (default 0)
            Threshold to apply.
            If 0: average of grayed image.
            If <= 1: average of grayed image * (1 + threshold). Eg. "0.5" means "150% of average".
            Else: specific value. Eg. "127".
        threshold_type : int (default cv2.THRESH_BINARY_INV)
            Threshold type to use.
        debug : int (default 0)
            Display infos about intermediate steps. Higher displays more infos.

        Returns
        -------
        numpy.ndarray
            The cropped image.
        """
        img = cv2.imdecode(
            np.fromfile(img, dtype=np.uint8), cv2.IMREAD_UNCHANGED
        )

        best_box = Scraper.find_crop(
            img,
            blur=blur,
            min_rect_pct=min_rect_pct,
            threshold=threshold,
            threshold_type=threshold_type,
            debug=debug,
        )

        # Crop image.
        crop_img = img[best_box[1] : best_box[3], best_box[0] : best_box[2]]
        return crop_img

    
    @staticmethod
    def find_crop(
        img,
        blur=5,
        min_rect_pct=0.05,
        threshold=0,
        threshold_type=cv2.THRESH_BINARY_INV,
        debug=0,
    ):
        """
        Find useless borders in a cv2 image.

        Parameters
        ----------
        img : str / numpy.ndarray
            Path of image to process.
            or
            cv2 image object to process.
        blur : int (default 5)
            Blur factor in pixels to apply on the grayed picture.
        min_rect_pct : float (default 0.05)
            All shapes smaller than min_rect_pct percent of the original image will be ignored.
        threshold : float (default 0)
            Threshold to apply.
            If 0: average of grayed image.
            If <= 1: average of grayed image * (1 + threshold). Eg. "0.5" means "150% of average".
            Else: specific value. Eg. "127".
        threshold_type : int (default cv2.THRESH_BINARY_INV)
            Threshold type to use.
        debug : int (default 0)
            Display infos about intermediate steps. Higher displays more infos.

        Returns
        -------
        [int, int, int, int]
            Bounds of the cropped image.
        """

        if isinstance(img, str):
            if os.path.isfile(img):
                img = cv2.imdecode(
                    np.fromfile(img, dtype=np.uint8), cv2.IMREAD_UNCHANGED
                )
            else:
                print(f"Impossible de trouver l'image \"{img}\".")

        src_height, src_width = img.shape[:2]

        # Preprocess image.
        thresh = Scraper.preprocess_image(img, blur, threshold, threshold_type)

        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        best_box = [0, 0, src_width, src_height]
        # Determine best box for contours.
        x1s, y1s, x2s, y2s = [], [], [], []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w >= min_rect_pct * src_width and h >= min_rect_pct * src_height:
                x1s.append(x)
                y1s.append(y)
                x2s.append(x + w)
                y2s.append(y + h)
        # Format: [x_top_left, y_top_left, x_bottom_right, y_bottom_right]
        if x1s:
            best_box = [min(x1s), min(y1s), max(x2s), max(y2s)]

        if (
            best_box == [0, 0, src_width, src_height]
            and threshold_type == cv2.THRESH_BINARY_INV
        ):
            if debug >= 1:
                print(f"[INFO] Retry assuming black borders.")
            if threshold <= 1:
                new_threshold = min(1, 0 - threshold)
            else:
                new_threshold = max(1.1, 255 - threshold)
            return Scraper.find_crop(
                img, blur, min_rect_pct, new_threshold, cv2.THRESH_BINARY, debug
            )
        return best_box


    @staticmethod
    def preprocess_image(
        img, blur=5, threshold=0, threshold_type=cv2.THRESH_BINARY_INV
    ):
        """
        Find useless borders in a cv2 image.

        Parameters
        ----------
        img : numpy.ndarray
            cv2 image object to process.
        blur : int (default 5)
            Blur factor in pixels to apply on the grayed picture.
        threshold : float (default 0)
            Threshold to apply.
            If 0: average of grayed image.
            If <= 1: average of grayed image * (1 + threshold). Eg. "0.5" means "150% of average".
            Else: specific value. Eg. "127".
        threshold_type : int (default cv2.THRESH_BINARY_INV)
            Threshold type to use.

        Returns
        -------
        numpy.ndarray
            Preprocessed image.
        """
        if len(img.shape) > 2:
            imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            # Image is already in gray scale.
            imgray = img
        if blur > 0:
            imgray = cv2.blur(imgray, (blur, blur))
        if threshold <= 1:
            _, thresh = cv2.threshold(
                imgray,
                math.floor(np.average(imgray)) * (1 + threshold),
                255,
                threshold_type,
            )
        else:
            _, thresh = cv2.threshold(imgray, threshold, 255, threshold_type)

        return thresh

    @staticmethod
    def save_img(img, output_path, format='jpeg', quality=85):
        """
        Save image in the desired quality.

        Parameters
        ----------
        img : numpy.ndarray
            cv2 image object to display.
        output_path : str
            File path to saved image.
        quality : int (default 85)
            Save quality factor. Max 100 (best quality).

        Returns
        -------
        str
            Output path of saved image.
        """
        ext = output_path.split(".")[-1].lower()
        params = []
        if format in ("jpg", "jpeg"):
            params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        if format == "webp":
            params = [cv2.IMWRITE_WEBP_QUALITY, quality]

        _, im_buf_arr = cv2.imencode(f".{ext}", img, params)
        im_buf_arr.tofile(output_path)
        return output_path