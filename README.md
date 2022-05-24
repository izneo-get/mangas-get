# mangas-get
Ce script permet de récupérer une BD présente sur https://www.mangas.io dans la limite des capacités de notre compte existant.

Le but est de pouvoir lire une BD sur un support non compatible avec les applications fournies par Mangas.io. 
Il est évident que les BD ne doivent en aucun cas être conservées une fois la lecture terminée ou lorsque votre abonnement ne vous permet plus de la lire.


## Utilisation
```
python mangas_get.py [-h] [--login LOGIN] [--force-login] [--password PASSWORD] [--output-folder OUTPUT_FOLDER]
                     [--output-format {img,cbz,both}] [--config CONFIG] [--from-page FROM_PAGE] [--limit LIMIT]
                     [--pause PAUSE] [--full-only] [--continue] [--user-agent USER_AGENT]
                     [--convert-images {webp,jpeg,original}] [--convert-quality CONVERT_QUALITY] [--smart-crop]
                     [--force-title FORCE_TITLE] [--list] [--list-write LIST_WRITE] [--infos] [--version]
                     [url]

Script pour sauvegarder une BD Mangas.io.

positional arguments:
  url                   L'URL de la BD à récupérer ou le chemin vers un fichier local contenant une liste d'URLs

options:
  -h, --help            show this help message and exit
  --login LOGIN, -l LOGIN
                        L'identifiant (email) sur le site
  --force-login         Ne lit pas le token en cache et force une authentification
  --password PASSWORD, -p PASSWORD
                        Le mot de passe sur le site
  --output-folder OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        Répertoire racine de téléchargement
  --output-format {img,cbz,both}, -f {img,cbz,both}
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
  --convert-images {webp,jpeg,original}
                        Conversion en JPEG ou WEBP
  --convert-quality CONVERT_QUALITY
                        Qualité de la conversion en JPEG ou WEBP
  --smart-crop          Supprimer les bords blancs des images (avec --convert-images uniquement)
  --force-title FORCE_TITLE
                        Le titre à utiliser dans les noms de fichier, à la place de celui trouvé sur la page
  --list                Liste les URLs des chapitres disponibles (option exclusive)
  --list-write LIST_WRITE
                        Liste les URLs des chapitres disponibles et les enregistre dans un fichier texte (option
                        exclusive)
  --infos               Affiche les informations sur la BD (option exclusive)
  --version             Affiche la version du script
```

### Exemples  
Pour récupérer la BD dans un répertoire d'images + CBZ, en conservant le format et la qualité d'image originale (fichier de config présent) :  
```
python mangas_get.py https://www.mangas.io/lire/naruto/1/1
```


Pour récupérer la BD dans une archive CBZ uniquement, en forçant le titre (fichier de config présent) :  
```
python mangas_get.py https://www.mangas.io/lire/naruto/1/1 --output-format cbz --force-title "%title%/%title% - Tome %volume_2d%/%title% Chapitre %chapter_3d%"
```
Cette commande enregistrera les fichiers dans un répertoire "Naruto/Naruto - Tome 01" avec comme préfixe de nom "Naruto Chapitre 001". 
On peut utiliser les tags `%title%`, `%author%`, `%volume%`, `%volume_2d%`, `%volume_3d%`, `%chapter%`, `%chapter_2d%`, `%chapter_3d%`, `%chapter_title%`. 

Pour récupérer la BD dans une archive CBZ uniquement, avec des images converties en JPEG (fichier de config présent) :  
```
python mangas_get.py https://www.mangas.io/lire/naruto/1/1 --output-format cbz --convert-images jpeg --convert-quality 70
```

Pour récuper la liste de toutes les URLs d'une série et la stocker dans un fichier et forcer le nom avec un template particulier : 
```
python mangas_get.py https://www.mangas.io/lire/naruto --list-write naruto.txt --force-title "%title%/%title% - Volume %volume_2d%/%title% %volume_2d% - Chapitre %chapter_3d%. %chapter_title%"
```

Pour télécharger toutes les BD listées dans un fichier : 
```
python mangas_get.py naruto.txt 
```

Pour voir les informations d'un chapitre : 
```
python mangas_get.py https://www.mangas.io/lire/naruto --infos
```
retournera 
> Champ                      Tag              Valeur
> -------------------------  ---------------  -------------------------------------------
> URL                        %url%            https://www.mangas.io/lire/naruto/1/1
> Slug                       %slug%           naruto
> Titre                      %title%          Naruto
> Sens de lecture            %direction%      rtol
> Auteur                     %author%         KISHIMOTO Masashi
> Volume                     %volume%         1
> Volume                     %volume_2d%      01
> Volume                     %volume_3d%      001
> Numéro de chapitre         %chapter%        1
> Numéro de chapitre         %chapter_2d%     01
> Numéro de chapitre         %chapter_3d%     001
> Chapitre                   %chapter_title%  Chap.01 : Naruto Uzumaki !!
> Nombre de pages            %pages%          55
> Nom du fichier par défaut  %default%        Naruto - 01x01. Chap.01 : Naruto Uzumaki !!
> Description : Naruto est un garçon un peu spécial. Il est toujours tout seul et son caractère fougueux ne l'aide pas vraiment à se faire apprécier dans son village. Malgré cela, il garde au fond de lui une ambition: celle de devenir un maître Hokage, la plus haute distinction dans l'ordre des ninjas, et ainsi obtenir la reconnaissance de ses pairs...


## Installation
### Prérequis
- Python 3.9+ (non testé avec les versions précédentes)
- pip (désormais inclus avec Python)
- Librairies SSL

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
