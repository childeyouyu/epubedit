import zipfile
import xml.etree.ElementTree as Et
from typing import Literal, List, Dict, Iterable


class Epubedit:
    ns = {

    }

    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.subject = []
        self.author = []
        self.rights = ""
        self.epub_version = ""
        self.title = ""
        self.publisher = ""
        self.published_date = ""
        self.modified_date = ""
        self.language = ""
        self.isbn = ""
        self.asin = ""

        with zipfile.ZipFile(self.file_path, "r") as epub:
            if "OEBPS/content.opf" in epub.namelist():
                self.opf_name = "OEBPS/content.opf"
            if "content.opf" in epub.namelist():
                self.opf_name = "content.opf"
            elif "EPUB/package.opf" in epub.namelist():
                self.opf_name = "EPUB/package.opf"

            self.opf_data = epub.read(self.opf_name).decode("utf-8")
            self.root = Et.fromstring(self.opf_data)
        self._retrieve_metadata()

    def _retrieve_metadata(self) -> None:
        self.epub_version = self.root.attrib["version"]
        for child in self.root:
            if child.tag == "{http://www.idpf.org/2007/opf}metadata":
                for metadata in child:
                    if metadata.tag == "{http://purl.org/dc/elements/1.1/}rights":
                        self.rights = metadata.text
                    elif metadata.tag == "{http://purl.org/dc/elements/1.1/}identifier":
                        self.identifier = metadata.text
                        if "id" in metadata.attrib:
                            self.bookid = metadata.text
                        if "{http://www.idpf.org/2007/opf}scheme" in metadata.attrib:
                            if (
                                    metadata.attrib["{http://www.idpf.org/2007/opf}scheme"]
                                    == "ASIN"
                            ):
                                self.asin = metadata.text
                            elif (
                                    metadata.attrib["{http://www.idpf.org/2007/opf}scheme"]
                                    == "ISBN"
                            ):
                                self.isbn = metadata.text
                    elif metadata.tag == "{http://purl.org/dc/elements/1.1/}creator":
                        self.author.append(metadata.text)
                    elif metadata.tag == "{http://www.idpf.org/2007/opf}meta":
                        try:
                            if metadata.attrib["property"] == "dcterms:modified":
                                self.modified_date = metadata.text
                        except KeyError:
                            pass
                    elif metadata.tag == "{http://purl.org/dc/elements/1.1/}title":
                        self.title = metadata.text
                    elif metadata.tag == "{http://purl.org/dc/elements/1.1/}language":
                        self.language = metadata.text
                    elif metadata.tag == "{http://purl.org/dc/elements/1.1/}subject":
                        self.subject.append(metadata.text)
                    elif metadata.tag == "{http://purl.org/dc/elements/1.1/}date":
                        try:
                            if (
                                    metadata.attrib["{http://www.idpf.org/2007/opf}event"]
                                    == "modification"
                            ):
                                self.modified_date = metadata.text
                            else:
                                self.published_date = metadata.text
                        except Exception as error:
                            print(error)
                    elif metadata.tag == "{http://purl.org/dc/elements/1.1/}source":
                        self.source = metadata.text
                    elif metadata.tag == "{http://purl.org/dc/elements/1.1/}publisher":
                        self.publisher = metadata.text

    def get_metadata(
            self,
            metadata_key: Literal[
                "epub_version",
                "book_name",
                "author_name",
                "publisher_name",
                "ISBN",
                "ASIN",
                "bookid",
                "describe",
                "language",
                "rights",
                "publication_date",
            ],
    ) -> List[str] | str:
        """
        return str or list
        """
        if metadata_key == "epub_version":
            return self.epub_version
        elif metadata_key == "book_name":
            return self.title
        elif metadata_key == "epub_version":
            return self.epub_version
        elif metadata_key == "author_name":
            return self.author
        elif metadata_key == "publisher_name":
            return self.publisher
        elif metadata_key == "ISBN":
            return self.isbn
        elif metadata_key == "ASIN":
            return self.asin
        elif metadata_key == "bookid":
            return self.bookid
        elif metadata_key == "language":
            return self.language
        elif metadata_key == "describe":
            return self.subject
        elif metadata_key == "rights":
            return self.rights
        elif metadata_key == "publication_date":
            return self.published_date

    def get_selected_metadata(
            self,
            metadata_keys: Iterable[Literal[
                "epub_version",
                "book_name",
                "author_name",
                "publisher_name",
                "ISBN",
                "ASIN",
                "bookid",
                "describe",
                "language",
                "rights",
                "publication_date",]
            ]
    ) -> Dict[str, str]:
        infos = {}
        for metadata_key in metadata_keys:
            if self.get_metadata(metadata_key):
                infos.update({metadata_key: self.get_metadata(metadata_key)})
        return infos

    def get_all_metadata(self) -> Dict[str, str]:
        return {
            "epub_version": self.epub_version,
            "rights": self.rights,
            "book_name": self.title,
            "author": self.author,
            'isbn': self.isbn,
            "asin": self.asin,
            "publisher": self.publisher,
            "published_date": self.published_date,
            "modified_date": self.modified_date,
            "language": self.language,
            "subject": self.subject,
        }
