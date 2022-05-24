from Scrapers.scraper import Scraper
import Scrapers.scraper
import requests
import re
import os
from getpass import getpass
from urllib.parse import urlparse
import sys
import time
from tabulate import tabulate

class MangasIoScraper(Scraper):
    """
    Classe qui permet de gérer le téléchargement d'une BD de Mangas.io.
    """

    bearer: str = ""  # Le token de session
    slug: str = ""  # Slug de la BD
    chapter_nb: str = ""  # Numéro du chapitre / tome à télécharger
    title: str = ""  # Titre de la série
    volume_title: str = ""  # Titre du tome
    volume_number: int = -1  # Numéro du tome
    chapter_title: str = ""  # Titre du chapitre
    chapter_number: int = -1  # Numéro du chapitre
    page_count: int = 0  # Nombre de pages d'après les métadonnées
    rtl: bool = False  # Sens de la lecture de droite à gauche
    authors: list = []  # Auteurs
    pages: dict = {}  # Informations sur les pages du tome
    infos: list = []  # Informations générales sur le chapitre
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "*/*",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        # 'Accept-Encoding': 'gzip, deflate, br',
        "Content-Type": "application/json; charset=utf-8",
        "Origin": "https://www.mangas.io",
        "DNT": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    def __init__(self, login_email="", password="", user_agent="", force_login=False):
        super().__init__()
        self.login_email = login_email
        self.password = password
        if user_agent:
            self.headers["User-Agent"] = user_agent

        if force_login:
            self.bearer = self.get_bearer(login_email, password)
        else:
            self.read_token()
        while not self.is_token_valid():
            print("INVALIDE")
            self.bearer = self.get_bearer(login_email, password)
        self.write_token(self.bearer)
        print("OK")

    def read_token(self):
        """Lecture du token de session depuis un fichier de cache"""
        print("Lecture du token en cache...")
        file_token = "cache/TOKEN_MANGAS_IO"
        if not os.path.isfile(file_token):
            os.makedirs(os.path.dirname(file_token), exist_ok=True)
            with open(file_token, "w") as f:
                f.write("")

        with open(file_token, "r") as f:
            self.bearer = f.read()

    def write_token(self, token):
        """Ecriture du token de session dans un fichier de cache"""
        file_token = "cache/TOKEN_MANGAS_IO"
        if not os.path.isfile(file_token):
            os.makedirs(os.path.dirname(file_token), exist_ok=True)
        with open(file_token, "w") as f:
            f.write(token)

    def is_token_valid(self):
        """Vérifie si le token de session est encore valide"""
        print("Vérification du token...", end=" ")
        if not self.bearer:
            return False
        json_data = {
            "token": self.bearer,
        }
        response = requests.post(
            "https://api.mangas.io/auth/token_validation", headers=self.headers, json=json_data, allow_redirects=True
        )
        if response.status_code != 200:
            print("Erreur :", response.status_code)
            return False
        return response.json()["status"] == "success"

    def get_bearer(self, login_email, password):
        """Récupère le token de session"""
        print("Récupération d'un nouveau token...", end=" ")
        if not login_email:
            login_email = input("Email de connexion : ")
        if not password:
            password = getpass("Mot de passe (ne sera pas affiché lors de la saisie) : ")

        json_data = {
            "email": login_email,
            "password": password,
        }

        response = requests.post(
            "https://api.mangas.io/auth/login", headers=self.headers, json=json_data, allow_redirects=True
        )
        if response.status_code != 200:
            print("Erreur :", response.status_code)
            return ""
        print("OK")
        return response.json()["token"]

    def get_chapter_list(self, slug, outputfile="", force_title=""):
        json_data = {
            "operationName": "GetManga",
            "variables": {
                "slug": slug,
            },
            "query": "query GetManga($slug: String) {\n  manga(slug: $slug) {\n    _id\n    slug\n    title\n    description\n    releaseDate\n    age\n    trailer\n    isOngoing\n    alternativeTitles\n    chapterCount\n    ctas {\n      url\n      image {\n        url\n        __typename\n      }\n      __typename\n    }\n    bannerMobile: banner(target: MOBILE) {\n      url\n      __typename\n    }\n    banner {\n      url\n      __typename\n    }\n    categories {\n      label\n      level\n      __typename\n    }\n    authors {\n      _id\n      name\n      __typename\n    }\n    thumbnail {\n      url\n      __typename\n    }\n    publishers {\n      publisher {\n        _id\n        name\n        countryCode\n        logo {\n          url\n          __typename\n        }\n        __typename\n      }\n      releaseDate\n      __typename\n    }\n    volumes {\n      _id\n      title\n      ean13\n      label\n      description\n      number\n      publicationDate\n      releaseDate\n      thumbnail {\n        url\n        pos_x\n        pos_y\n        __typename\n      }\n      chapterStart\n      chapterEnd\n      chapters {\n        _id\n        number\n        title\n        isRead\n        isBonus\n        isSeparator\n        access\n        publicationDate\n        releaseDate\n        pageCount\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
        }
        response = requests.post(
            "https://api.mangas.io/api", headers=self.headers, json=json_data, allow_redirects=True
        )
        if response.status_code != 200:
            print(f"Erreur : {response.status_code}")
            return False
        data = response.json()
        self.title = data["data"]["manga"]["title"]
        self.authors = [author["name"] for author in data["data"]["manga"]["authors"]]
        for volume in data["data"]["manga"]["volumes"]:
            self.volume_title = volume["title"]
            self.volume_number = volume["number"]
            if isinstance(self.volume_number, int):
                volume_number_2 = f"{self.volume_number:02d}"
                volume_number_3 = f"{self.volume_number:03d}"
            else:
                volume_number_2 = f"{int(self.volume_number):02d}" + "." + str(self.volume_number).split(".")[-1]
                volume_number_3 = f"{int(self.volume_number):03d}" + "." + str(self.volume_number).split(".")[-1]
            for chapter in volume["chapters"]:
                self.chapter_title = chapter["title"]
                self.chapter_number = chapter["number"]
                self.page_count = chapter["number"]

                if isinstance(self.chapter_number, int):
                    chapter_number_2 = f"{self.chapter_number:02d}"
                    chapter_number_3 = f"{self.chapter_number:03d}"
                else:
                    chapter_number_2 = f"{int(self.chapter_number):02d}" + "." + str(self.chapter_number).split(".")[-1]
                    chapter_number_3 = f"{int(self.chapter_number):03d}" + "." + str(self.chapter_number).split(".")[-1]


                title_used = self.get_title()
                direction = "?"
                authors = ", ".join(self.authors)
                self.infos = []
                self.infos.append(["URL", "%url%", self.url])
                self.infos.append(["Slug", "%slug%", slug])
                self.infos.append(["Titre", "%title%", self.title])
                self.infos.append(["Sens de lecture", "%direction%", direction])
                self.infos.append(["Auteur", "%author%", authors])
                self.infos.append(["Volume", "%volume%", self.volume_number])
                self.infos.append(["Volume", "%volume_2d%", volume_number_2])
                self.infos.append(["Volume", "%volume_3d%", volume_number_3])
                self.infos.append(["Numéro de chapitre", "%chapter%", self.chapter_number])
                self.infos.append(["Numéro de chapitre", "%chapter_2d%", chapter_number_2])
                self.infos.append(["Numéro de chapitre", "%chapter_3d%", chapter_number_3])
                self.infos.append(["Chapitre", "%chapter_title%", self.chapter_title])
                self.infos.append(["Nombre de pages", "%pages%", self.page_count])
                self.infos.append(["Nom du fichier par défaut", "%default%", self.get_title()])
                
                if force_title:
                    title_used = self.replace_title(force_title)
                if not outputfile:
                    print(f"# {title_used}")
                else:
                    with open(outputfile, "a", encoding="utf-8") as f:
                        f.write(f"# {title_used}\n")
                if not chapter["isSeparator"]:
                    if not outputfile:
                        print(f"https://www.mangas.io/lire/{slug}/{chapter['number']}/1")
                    else:
                        with open(outputfile, "a", encoding="utf-8") as f:
                            f.write(f"https://www.mangas.io/lire/{slug}/{chapter['number']}/1\n")

    def get_title(self):
        title_used = self.title
        if isinstance(self.volume_number, int):
            volume_number = f"{self.volume_number:02d}"
        else:
            volume_number = f"{int(self.volume_number):02d}" + "." + str(self.volume_number).split(".")[-1]
        if isinstance(self.chapter_number, int):
            chapter_number = f"{self.chapter_number:02d}"
        else:
            chapter_number = f"{int(self.chapter_number):02d}" + "." + str(self.chapter_number).split(".")[-1]

        if self.chapter_title:
            title_used = self.title + " - " + self.chapter_title
        if self.chapter_number >= 0:
            title_used = self.title + " - " + chapter_number
        if self.chapter_number >= 0 and self.volume_number >= 0:
            title_used = self.title + " - " + f"{volume_number}x{chapter_number}"
        if self.chapter_title and self.chapter_number >= 0:
            title_used = self.title + " - " + f"{chapter_number}" + ". " + self.chapter_title
        if self.chapter_title and self.chapter_number >= 0 and self.volume_number >= 0:
            title_used = self.title + " - " + f"{volume_number}x{chapter_number}" + ". " + self.chapter_title

        return title_used

    def print_infos(self, url):
        self.url = url
        res = re.search("https://www.mangas.io/lire/([^/]+)/([\d\.]+)", self.url)
        if not res:
            print("URL invalide")
            return False
        self.slug, self.chapter_nb = res.groups()
        self.chapter_nb = float(self.chapter_nb)

        self.get_pages()

        print(tabulate(self.infos, headers=['Champ', 'Tag', 'Valeur']))
        print("Description :", self.volume_description)

        return True

    def replace_title(self, title):
        new_title = title.replace("/", "¤")
        for elem in self.infos:
            new_title = new_title.replace(elem[1], str(elem[2]))
        new_title = Scrapers.scraper.clean_name(new_title)
        new_title = new_title.replace("¤", "/")
        return new_title

    def download(
        self,
        url,
        output_folder="DOWNLOADS",
        force_title="",
        overwrite_if_exists=True,
        pause_sec=0,
        from_page=0,
        nb_page_limit=1000,
        full_only=False,
    ):
        self.url = url
        self.slug, self.chapter_nb = re.search("https://www.mangas.io/lire/([^/]+)/([\d\.]+)", self.url).groups()
        self.chapter_nb = float(self.chapter_nb)

        """ Télécharge la BD """
        self.get_pages()
        if not self.pages:
            print("Erreur : Aucune page trouvée")
            return False
        if len(self.pages) != self.page_count:
            print(f"Attention : {self.page_count} pages attendues, mais {len(self.pages)} annoncées")
            if full_only:
                return False
        title_used = self.get_title()
        folder_used = title_used
        if force_title:
            new_title = self.replace_title(force_title)
            print(
                'Téléchargement de "'
                + Scrapers.scraper.clean_name(title_used)
                + '" en tant que "'
                + new_title
                + '"'
            )
            title_used = new_title.split('/')[-1]
            folder_used = title_used
            if '/' in new_title:
                folder_used = '/'.join(new_title.split('/')[:-1])
        else:
            title_used = Scrapers.scraper.clean_name(title_used)
            print('Téléchargement de "' + title_used + '"')
        save_path = f"{output_folder}/{folder_used}"
        progress_bar = ""
        for page in self.pages:
            if page < from_page or page >= from_page + nb_page_limit:
                continue
            progress_bar += "." if self.download_page(page, save_path, title_used, overwrite_if_exists) else "x"
            progress_message = f"\r[page {page + 1} / {len(self.pages)}] {progress_bar}"
            print(progress_message, end="")
            sys.stdout.flush()
            time.sleep(pause_sec)
        print(" Terminé !")
        return save_path

    def get_pages(self):
        """Récupère les métadonnées de la BD, dont la liste des pages"""
        headers = self.headers
        headers["authorization"] = f"Bearer {self.bearer}"
        json_data = {
            "operationName": "getReadingChapter",
            "variables": {
                "chapterNb": self.chapter_nb,
                "slug": self.slug,
                "quality": "HD",
            },
            "query": "query getReadingChapter($slug: String, $chapterNb: Float) {\n  manga(slug: $slug) {\n    _id\n    title\n    contentWarning\n    direction\n    authors {\n      _id\n      name\n      __typename\n    }\n    volumes {\n      _id\n      number\n      description\n      chapters {\n        _id\n        title\n        number\n        isRead\n        isSeparator\n        releaseDate\n        __typename\n      }\n      __typename\n    }\n    chapter(number: $chapterNb) {\n      _id\n      number\n      title\n      releaseDate\n      pageCount\n      access\n      copyright\n      pages {\n        _id\n        isDoublePage\n        number\n        image {\n          meta {\n            width\n            height\n            blurhash\n            ratio\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      next {\n        _id\n        title\n        number\n        releaseDate\n        access\n        __typename\n      }\n      previous {\n        _id\n        title\n        number\n        pageCount\n        releaseDate\n        access\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
        }
        response = requests.post("https://api.mangas.io/api", headers=headers, json=json_data, allow_redirects=True)
        if response.status_code != 200:
            print(f"Erreur : {response.status_code}")
            return False
        data = response.json()
        if data:
            self.fill_infos(data)
        return True


    def fill_infos(self, data):
        self.title = data["data"]["manga"]["title"]
        self.rtl = data["data"]["manga"]["direction"] == "rtl"
        self.authors = [author["name"] for author in data["data"]["manga"]["authors"]]
        chapter_id = data["data"]["manga"]["chapter"]["_id"]
        volume = None
        self.volume_number = 0
        self.volume_description = ""
        for v in data["data"]["manga"]["volumes"]:
            for c in v["chapters"]:
                if c["_id"] == chapter_id:
                    volume = v
                    break
        if volume:
            self.volume_number = volume["number"]
            self.volume_description = volume["description"]
        self.chapter_title = data["data"]["manga"]["chapter"]["title"]
        self.chapter_number = data["data"]["manga"]["chapter"]["number"]
        self.page_count = data["data"]["manga"]["chapter"]["pageCount"]
        self.pages = {}
        if data["data"]["manga"]["chapter"]["pages"]:
            self.pages = {page["number"]: page["_id"] for page in data["data"]["manga"]["chapter"]["pages"]}

        if isinstance(self.volume_number, int):
            volume_number_2 = f"{self.volume_number:02d}"
            volume_number_3 = f"{self.volume_number:03d}"
        else:
            volume_number_2 = f"{int(self.volume_number):02d}" + "." + str(self.volume_number).split(".")[-1]
            volume_number_3 = f"{int(self.volume_number):03d}" + "." + str(self.volume_number).split(".")[-1]

        if isinstance(self.chapter_number, int):
            chapter_number_2 = f"{self.chapter_number:02d}"
            chapter_number_3 = f"{self.chapter_number:03d}"
        else:
            chapter_number_2 = f"{int(self.chapter_number):02d}" + "." + str(self.chapter_number).split(".")[-1]
            chapter_number_3 = f"{int(self.chapter_number):03d}" + "." + str(self.chapter_number).split(".")[-1]
    
        direction = "rtol" if self.rtl else "ltor"
        authors = ", ".join(self.authors)
        self.infos = []
        self.infos.append(["URL", "%url%", self.url])
        self.infos.append(["Slug", "%slug%", self.slug])
        self.infos.append(["Titre", "%title%", self.title])
        self.infos.append(["Sens de lecture", "%direction%", direction])
        self.infos.append(["Auteur", "%author%", authors])
        self.infos.append(["Volume", "%volume%", self.volume_number])
        self.infos.append(["Volume", "%volume_2d%", volume_number_2])
        self.infos.append(["Volume", "%volume_3d%", volume_number_3])
        self.infos.append(["Numéro de chapitre", "%chapter%", self.chapter_number])
        self.infos.append(["Numéro de chapitre", "%chapter_2d%", chapter_number_2])
        self.infos.append(["Numéro de chapitre", "%chapter_3d%", chapter_number_3])
        self.infos.append(["Chapitre", "%chapter_title%", self.chapter_title])
        self.infos.append(["Nombre de pages", "%pages%", self.page_count])
        self.infos.append(["Nom du fichier par défaut", "%default%", self.get_title()])
        return

    def download_page(
        self,
        page_nb,
        save_path="DOWNLOADS",
        title="",
        overwrite_if_exists=True,
    ):
        """Télécharge une page"""
        os.makedirs(save_path, exist_ok=True)
        title = Scrapers.scraper.clean_name(title)
        headers = self.headers
        headers["authorization"] = f"Bearer {self.bearer}"

        json_data = {
            "operationName": "getPageById",
            "variables": {
                "id": self.pages[page_nb],
                "quality": "HD",
            },
            "query": "query getPageById($id: ID!, $quality: PageType) {\n  page(id: $id) {\n    _id\n    isDoublePage\n    image(type: $quality) {\n      url\n      __typename\n    }\n    __typename\n  }\n}",
        }

        response = requests.post("https://api.mangas.io/api", headers=headers, json=json_data, allow_redirects=True)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return False
        data = response.json()
        if data:
            url = data["data"]["page"]["image"]["url"]
            file_ext = os.path.splitext(urlparse(url).path)[1]
            file_name = f"{title}_{page_nb:03d}{file_ext}"
            if len(self.pages) >= 1000:
                file_name = f"{title}_{page_nb:04d}{file_ext}"
            if os.path.isfile(f"{save_path}/{file_name}") and not overwrite_if_exists:
                return False
            res = Scrapers.scraper.requests_retry_session().get(url, allow_redirects=True, headers=self.headers)
            if res.status_code != 200:
                print(f"Erreur : {res.status_code}")
                return False
            with open(f"{save_path}/{file_name}", "wb") as output:
                output.write(res.content)
            return True
