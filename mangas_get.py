from Scrapers.mangas_io_scraper import MangasIoScraper
import argparse
import configparser
import os
import re
import sys
import shutil
import requests

__VERSION__ = "1.01.00"

def check_version():
    latest_version_url = (
        "https://raw.githubusercontent.com/izneo-get/mangas-get/master/VERSION"
    )
    res = requests.get(latest_version_url)
    if res.status_code != 200:
        print(f"Version {__VERSION__} (impossible de vérifier la version officielle)")
    else:
        latest_version = res.text.strip()
        if latest_version == __VERSION__:
            print(f"Version {__VERSION__} (version officielle)")
        else:
            print(
                f"Version {__VERSION__} (la version officielle est différente: {latest_version})"
            )
            print(
                "Please check https://github.com/izneo-get/mangas-get/releases/latest"
            )
    print()


if __name__ == "__main__":
    # Parse des arguments passés en ligne de commande.
    parser = argparse.ArgumentParser(description="""Script pour sauvegarder une BD Mangas.io.""")
    parser.add_argument(
        "url",
        type=str,
        default="",
        nargs="?",
        help="L'URL de la BD à récupérer ou le chemin vers un fichier local contenant une liste d'URLs",
    )
    parser.add_argument(
        "--login",
        "-l",
        type=str,
        default=None,
        help="L'identifiant (email) sur le site",
    )
    parser.add_argument("--password", "-p", type=str, default=None, help="Le mot de passe sur le site")
    parser.add_argument(
        "--output-folder",
        "-o",
        type=str,
        default=None,
        help="Répertoire racine de téléchargement",
    )

    parser.add_argument(
        "--output-format",
        "-f",
        choices={"cbz", "img", "both"},
        type=str,
        default="both",
        help="Format de sortie",
    )
    parser.add_argument("--config", type=str, default=None, help="Fichier de configuration")
    parser.add_argument(
        "--from-page",
        type=int,
        default=0,
        help="Première page à récupérer (défaut : 0)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Nombre de pages à récupérer au maximum (défaut : 1000)",
    )
    parser.add_argument(
        "--pause",
        type=int,
        default=0,
        help="Pause (en secondes) à respecter après chaque téléchargement d'image",
    )
    parser.add_argument(
        "--full-only",
        action="store_true",
        default=False,
        help="Ne prend que les liens de BD dont toutes les pages sont disponibles",
    )
    parser.add_argument(
        "--continue",
        action="store_true",
        dest="continue_from_existing",
        default=False,
        help="Pour reprendre là où on en était. Par défaut, on écrase les fichiers existants.",
    )
    parser.add_argument("--user-agent", type=str, default=None, help="User agent à utiliser")
    parser.add_argument(
        "--convert-images",
        choices={"jpeg", "webp", "original"},
        type=str,
        default="original",
        help="Conversion en JPEG ou WEBP",
    )
    parser.add_argument(
        "--convert-quality",
        type=int,
        default=90,
        help="Qualité de la conversion en JPEG ou WEBP",
    )
    parser.add_argument(
        "--smart-crop",
        action="store_true",
        default=False,
        help="Supprimer les bords blancs des images (avec --convert-images uniquement)",
    )
    parser.add_argument(
        "--force-title",
        type=str,
        default=None,
        help="Le titre à utiliser dans les noms de fichier, à la place de celui trouvé sur la page",
    )
    args = parser.parse_args()

    # Vérification que c'est la dernière version.
    check_version()

    # Lecture de la config.
    config = configparser.RawConfigParser()
    if args.config:
        config_name = args.config
    else:
        config_name = re.sub(r"\.py$", ".cfg", os.path.abspath(sys.argv[0]))
        config_name = re.sub(r"\.exe$", ".cfg", config_name)
    config.read(config_name)

    def get_param_or_default(config, param_name, default_value, cli_value=None):
        if cli_value is None:
            return config.get("DEFAULT", param_name) if config.has_option("DEFAULT", param_name) else default_value
        else:
            return cli_value

    login = get_param_or_default(config, "login", "", args.login)
    password = get_param_or_default(config, "password", "", args.password)
    user_agent = get_param_or_default(config, "user_agent", "", args.user_agent)
    pause_sec = get_param_or_default(config, "pause", "", args.pause)
    output_folder = get_param_or_default(
        config,
        "output_folder",
        os.path.dirname(os.path.abspath(sys.argv[0])) + "/DOWNLOADS",
        args.output_folder,
    )
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)
    url = args.url
    from_page = args.from_page
    nb_page_limit = args.limit
    full_only = args.full_only
    force_title = args.force_title
    overwrite_if_exists = not args.continue_from_existing
    convert_images = args.convert_images
    convert_quality = args.convert_quality
    output_format = args.output_format
    smart_crop = args.smart_crop
    
    while not os.path.isfile(url) and not url.lower().startswith("http"):
        url = input("URL de la BD ou fichier : ")

    url_list = []
    if os.path.isfile(url):
        # if encoding:
        #     with open(url, "r", encoding=encoding) as f:
        #         lines = f.readlines()
        # else:
        with open(url, "r") as f:
            lines = f.readlines()
        next_forced_title = ""
        for line in lines:
            line = line.strip()
            # On cherche si on a un titre forcé.
            res = ""
            if line and line.strip()[0] == "#":
                res = line.strip()[1:].strip()
            if res:
                next_forced_title = res
            if line and line.strip()[0] != "#":
                url_list.append([line, next_forced_title])
                next_forced_title = ""
    else:
        url_list.append([url, force_title])

    for url in url_list:
        force_title = url[1]
        url = url[0]

        scraper = MangasIoScraper(login_email=login, password=password, user_agent=user_agent)
        result = scraper.download(
            url,
            force_title=force_title,
            output_folder=output_folder,
            overwrite_if_exists=overwrite_if_exists,
            pause_sec=pause_sec,
            from_page=from_page,
            nb_page_limit=nb_page_limit,
            full_only=full_only,
        )

        if convert_images in ("jpeg", "webp"):
            scraper.convert_images(result, convert_images, convert_quality, smart_crop)

        if output_format in ("cbz", "both"):
            scraper.create_cbz(result)

        if output_format == "cbz":
            shutil.rmtree(result)