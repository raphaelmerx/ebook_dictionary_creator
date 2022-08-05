import sqlite3
import requests

from ebook_dictionary_creator.database_creator import create_database
from ebook_dictionary_creator.e_dictionary_creator.create_kindle_dict import (
    create_kindle_dict,
)
from ebook_dictionary_creator.e_dictionary_creator.create_tab_file import (
    create_nonkindle_dict,
)
from ebook_dictionary_creator.e_dictionary_creator.tatoeba_creator import TatoebaAugmenter

LANGUAGES_WITH_STRESS_MARKED_IN_DICT = ["Russian", "Ukraininian", "Belarusian", "Bulgarian", "Rusyn"]
"""Languages that have the stress marked in a dictionary, but not in general texts."""
class DictionaryCreator:

    # Initialize the class with the source language and target language
    def __init__(
        self,
        source_language: str,
        target_language: str = "English",
        kaikki_file_path=None,
        database_path=None,
    ):
        self.source_language = source_language
        self.target_language = target_language
        self.kaikki_file_path = kaikki_file_path
        self.database_path = database_path

    def download_data_from_kaikki(self, kaikki_file_path: str = None):
        # This downloads the data from kaikki.org, with the following format https://kaikki.org/dictionary/Czech/kaikki.org-dictionary-Czech.json
        # Only replace Czech with whatever language you want to download
        if kaikki_file_path == None:
            kaikki_file_path = "kaikki.org-dictionary-" + self.source_language + ".json"

        with open(kaikki_file_path, "w") as f:
            f.write(
                requests.get(
                    f"https://kaikki.org/dictionary/{self.source_language}/kaikki.org-dictionary-{self.source_language}.json"
                ).text
            )
        self.kaikki_file_path = kaikki_file_path

    def create_database(self, database_path: str = None, use_raw_glosses=True):
        # This creates the database from the kaikki.org file
        if database_path == None:
            database_path = self.source_language + "_" + self.target_language + ".db"
        create_database.create_database(
            database_path, self.kaikki_file_path, self.source_language, use_raw_glosses
        )
        self.database_path = database_path

    def add_data_from_tatoeba(self):

        # Get all the words from the database
        conn = sqlite3.connect(self.database_path)
        c = conn.cursor()
        c.execute("SELECT word FROM word")
        words = c.fetchall()
        # Convert to a proper list
        exception_word_list = {word[0] for word in words}      
        self.tatoeba_creator = TatoebaAugmenter(self.source_language, self.target_language, exception_word_list)
        test_output = self.tatoeba_creator.get_word_and_html_for_all_words_not_in_word_list()
        # Print dictionary to file
        with open("tatoeba_output.txt", "w", encoding="utf-8") as f:
            f.write(str(test_output))

    def export_to_tabfile(self, tabfile_path: str = None):
        # This exports the database to a tabfile
        if tabfile_path == None:
            tabfile_path = self.source_language + "_" + self.target_language + ".tsv"
        create_nonkindle_dict(self.database_path, tabfile_path, "Tabfile")
        self.tabfile_path = tabfile_path

    def export_to_stardict(self, author: str, title: str, stardict_path: str = None):
        # This exports the database to a stardict file
        if stardict_path == None:
            stardict_path = self.source_language + "_" + self.target_language + ".ifo"
        create_nonkindle_dict(
            self.database_path,
            stardict_path,
            "Stardict",
            self.source_language,
            self.target_language,
            author,
            title,
        )
        self.stardict_path = stardict_path

    def export_to_kindle(
        self,
        kindlegen_path: str,
        try_to_fix_failed_inflections: str,
        author: str,
        title: str,
        mobi_path: str = None,
    ):
        # This exports the database to a kindle file
        if mobi_path == None:
            mobi_path = self.source_language + "_" + self.target_language  # + ".mobi"
        create_kindle_dict(
            self.database_path,
            self.source_language,
            self.target_language,
            mobi_path,
            author,
            title,
            kindlegen_path,
            try_to_fix_kindle_lookup_stupidity=try_to_fix_failed_inflections,
        )
        self.mobi_path = mobi_path
