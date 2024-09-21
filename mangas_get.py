from Scrapers.mangas_io_scraper import MangasIoScraper
from downloader import process


def main() -> None:
    scraper = MangasIoScraper()
    process(scraper)


if __name__ == "__main__":
    main()
