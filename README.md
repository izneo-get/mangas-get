# mangas-get
Ce script permet de récupérer une BD présente sur https://www.mangas.io dans la limite des capacités de notre compte existant.

Le but est de pouvoir lire une BD sur un support non compatible avec les applications fournies par Mangas.io. 
Il est évident que les BD ne doivent en aucun cas être conservées une fois la lecture terminée ou lorsque votre abonnement ne vous permet plus de la lire.


## Utilisation
```
python mangas_get.py [-h] [--login LOGIN] [--password PASSWORD] [--output-folder OUTPUT_FOLDER]
                     [--output-format {both,img,cbz}] [--config CONFIG] [--from-page FROM_PAGE] [--limit LIMIT]
                     [--pause PAUSE] [--full-only] [--continue] [--user-agent USER_AGENT]
                     [--convert-images {original,webp,jpeg}] [--convert-quality CONVERT_QUALITY]
                     [--force-title FORCE_TITLE]
                     [url]

Script pour sauvegarder une BD Mangas.io.

positional arguments:
  url                   L'URL de la BD à récupérer ou le chemin vers un fichier local contenant une liste d'URLs

optional arguments:
  -h, --help            show this help message and exit
  --login LOGIN, -l LOGIN
                        L'identifiant (email) sur le site
  --password PASSWORD, -p PASSWORD
                        Le mot de passe sur le site
  --output-folder OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        Répertoire racine de téléchargement
  --output-format {both,img,cbz}, -f {both,img,cbz}
                        Format de sortie
  --config CONFIG       Fichier de configuration
  --from-page FROM_PAGE
                        Première page à récupérer (défaut : 0)
  --limit LIMIT         Nombre de pages à récupérer au maximum (défaut : 1000)
  --pause PAUSE         Pause (en secondes) à respecter après chaque téléchargement d'image
  --full-only           Ne prend que les liens de BD dont toutes les pages sont disponibles
  --continue            Pour reprendre là où on en était. Par défaut, on écrase les fichiers existants.
  --user-agent USER_AGENT
                        User agent à utiliser
  --convert-images {original,webp,jpeg}
                        Conversion en JPEG ou WEBP
  --convert-quality CONVERT_QUALITY
                        Qualité de la conversion en JPEG ou WEBP
  --force-title FORCE_TITLE
                        Le titre à utiliser dans les noms de fichier, à la place de celui trouvé sur la page
```

Exemple :  
Pour récupérer la BD dans un répertoire d'images + CBZ, en conservant le format et la qualité d'image originale (fichier de config présent) :  
```
python mangas_get.py https://www.mangas.io/lire/naruto/1/1
```


Pour récupérer la BD dans une archive CBZ uniquement, en forçant le titre (fichier de config présent) :  
```
python mangas_get.py https://www.mangas.io/lire/naruto/1/1 --output-format cbz --force-title "Naruto - Tome 01, Chapitre 01"
```

Pour récupérer la BD dans une archive CBZ uniquement, avec des images converties en JPEG (fichier de config présent) :  
```
python mangas_get.py https://www.mangas.io/lire/naruto/1/1 --output-format cbz --convert-images jpeg --convert-quality 70
```



## Installation
### Prérequis
- Python 3.9+ (non testé avec les versions précédentes)
- pip (désormais inclus avec Python)
- Librairies SSL
- Drivers Chrome (pour la version "Selenium")
- Chrome (pour la version "Selenium")

#### Sous Windows
##### Python
Allez sur ce site :  
https://www.python.org/downloads/windows/  
et suivez les instructions d'installation de Python 3.


##### Librairies SSL
- Vous pouvez essayer de les installer avec la commande :  
```
pip install pyopenssl
```
- Vous pouvez télécharger [OpenSSL pour Windows](http://gnuwin32.sourceforge.net/packages/openssl.htm). 


#### Sous Linux
Si vous êtes sous Linux, vous n'avez pas besoin de moi pour installer Python, Pip ou SSL...  


### Installation
- En ligne de commande, clonez le repo : 
```
git clone https://github.com/izneo-get/mangas-get.git
cd mangas-get
```
- (optionnel) Créez un environnement virtuel Python dédié : 
```
python -m venv env
env\Scripts\activate
python -m pip install --upgrade pip
```
- Installez les dépendances : 
```
python -m pip install -r requirements.txt
```

  
ou  
  
  
- Vous pouvez télécharger uniquement le [binaire Windows](https://github.com/izneo-get/mangas-get/releases/latest) (expérimental).  
