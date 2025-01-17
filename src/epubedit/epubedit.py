import contextlib
import os
import shutil
import tempfile
import zipfile
import xml.etree.ElementTree as Et
from typing import Literal, List, Dict, Iterable
from pathlib import Path


class Epubedit:
    namespaces = {
        "ns": "urn:oasis:names:tc:opendocument:xmlns:container",
        "dc": "http://purl.org/dc/elements/1.1/",
        "opf": "http://www.idpf.org/2007/opf",
    }

    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.bookid = None
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
        metadata_keys: Iterable[
            Literal[
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
            ]
        ],
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
            "isbn": self.isbn,
            "asin": self.asin,
            "publisher": self.publisher,
            "published_date": self.published_date,
            "modified_date": self.modified_date,
            "language": self.language,
            "subject": self.subject,
        }

    @staticmethod
    def _create_temp_directory():
        """Create a temporary directory and return the path"""
        return Path(tempfile.mkdtemp(prefix="epub_"))

    @staticmethod
    def _clean_directory(directory):
        """Safe clean directory"""
        try:
            if directory.exists():
                shutil.rmtree(directory)
        except Exception as e:
            print(f"Warning: Failed to clean directory {directory}: {e}")

    def commit(self, new_file_path=None) -> str | bool:
        """Modify EPUB files"""
        if new_file_path is None:
            new_file_path = Path(self.file_path)
            print("new_file_path: ", new_file_path)
        new_file_path = Path(new_file_path)

        temp_dir = None
        try:
            temp_dir = self._create_temp_directory()

            # Unzip EPUB file
            with zipfile.ZipFile(self.file_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # Process container.xml
            container_path = temp_dir / "META-INF" / "container.xml"
            if not container_path.exists():
                raise FileNotFoundError("container.xml not found in EPUB")

            container_tree = Et.parse(container_path)
            rootfile = container_tree.getroot().find(".//ns:rootfile", self.namespaces)
            if rootfile is None:
                raise ValueError("Invalid EPUB: rootfile element not found")

            # Process content.opf
            content_opf_path = temp_dir / rootfile.get("full-path")
            if not content_opf_path.exists():
                raise FileNotFoundError(f"content.opf not found at: {content_opf_path}")

            new_file_path.parent.mkdir(parents=True, exist_ok=True)
            self._update_metadata(content_opf_path)

            # Create new EPUB
            with zipfile.ZipFile(new_file_path, "w", zipfile.ZIP_DEFLATED) as zip_ref:
                for file_path in temp_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zip_ref.write(file_path, arcname)
            return True
        except Exception as e:
            print(f"Error modifying EPUB: {str(e)}")
            if new_file_path.exists():
                with contextlib.suppress(Exception):
                    new_file_path.unlink()
            raise

        finally:
            if temp_dir:
                self._clean_directory(temp_dir)

    def _update_metadata(self, content_opf_path):
        """Update metadata section"""
        tree = Et.parse(content_opf_path)

        root = tree.getroot()
        metadata = root.find(f".//{{{self.namespaces['opf']}}}metadata")

        if metadata is None:
            metadata = Et.SubElement(root, f"{{{self.namespaces['opf']}}}metadata")

        # Update various metadata
        if self.epub_version:
            root.set("version", self.epub_version)

        if self.title:
            self._update_dc_element(metadata, "title", self.title)

        if self.author:
            self._update_creator_elements(metadata)

        if self.rights:
            self._update_dc_element(metadata, "rights", self.rights)

        # if self.identifier:
        #     self._update_dc_element(metadata, "identifier", self.identifier)
        # Save updated file
        tree.write(content_opf_path, encoding="utf-8", xml_declaration=True)

    def _update_dc_element(self, metadata, element_name, value):
        """Update or create DC elements"""
        element = metadata.find(f".//{{{self.namespaces['dc']}}}{element_name}")
        if element is None:
            element = Et.SubElement(
                metadata, f"{{{self.namespaces['dc']}}}{element_name}"
            )
        element.text = value

    def _update_creator_elements(self, metadata):
        """Update creator information"""
        for creator in metadata.findall(f".//{{{self.namespaces['dc']}}}creator"):
            metadata.remove(creator)

        if isinstance(self.author, str):
            authors = [self.author]
        else:
            authors = self.author

        for author in authors:
            creator = Et.SubElement(metadata, f"{{{self.namespaces['dc']}}}creator")
            creator.text = author

    def change_metadata(
        self,
        metadata_key: Literal[
            "epub_version",
            "book_name",
            "author_name",
            "publisher_name",
            # "ISBN",
            # "ASIN",
            # "bookid",
            # "describe",
            # "language",
            # "rights",
            # "publication_date",
        ] = None,
        new_value: str = None,
    ) -> bool:
        if metadata_key == "epub_version":
            self.epub_version = new_value
        elif metadata_key == "book_name":
            self.title = new_value
        elif metadata_key == "epub_version":
            self.epub_version = new_value
        elif metadata_key == "author_name":
            self.author = new_value
        elif metadata_key == "publisher_name":
            self.publisher = new_value
        elif metadata_key == "ISBN":
            self.isbn = new_value
        elif metadata_key == "ASIN":
            self.asin = new_value
        elif metadata_key == "bookid":
            self.bookid = new_value
        elif metadata_key == "language":
            self.language = new_value
        elif metadata_key == "describe":
            self.subject = new_value
        elif metadata_key == "rights":
            self.rights = new_value
        elif metadata_key == "publication_date":
            self.published_date = new_value
        # return self.get_metadata(metadata_key)
        return True
