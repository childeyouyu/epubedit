import os
import shutil
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
    def commit(self, new_file_path = None) -> bool:
        if new_file_path is None:
            new_file_path = self.file_path
        try:
            # 创建一个临时目录来解压EPUB文件
            temp_dir = "temp_epub"  # 临时目录名称
            os.makedirs(temp_dir, exist_ok=True)  # 创建临时目录，如果目录已存在则忽略

            # 解压EPUB文件到临时目录
            with zipfile.ZipFile(new_file_path, 'r') as zip_ref:  # 打开EPUB文件（ZIP格式）
                zip_ref.extractall(temp_dir)  # 将EPUB文件解压到临时目录

            # 找到`container.xml`文件路径
            container_path = os.path.join(temp_dir, "META-INF", "container.xml")  # 拼接路径
            container_tree = Et.parse(container_path)  # 解析`container.xml`文件
            container_root = container_tree.getroot()  # 获取XML根元素

            # 从`container.xml`中找到`content.opf`文件的路径
            # `content.opf`文件通常包含EPUB的元数据
            rootfile = container_root.find(".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile")
            content_opf_path = os.path.join(temp_dir, rootfile.attrib["full-path"])  # 拼接`content.opf`的完整路径

            # 解析`content.opf`文件
            content_tree = Et.parse(content_opf_path)  # 解析`content.opf`文件
            content_root = content_tree.getroot()  # 获取XML根元素


            # 修改 协议版本
            content_root.attrib["version"] = self.epub_version
            # 修改 版权信息
            if self.rights:
                rights = content_root.find(".//{http://purl.org/dc/elements/1.1/}rights")  # 查找<rights>标签
                if rights is not None:  # 如果找到<rights>标签
                    rights.text = self.rights  # 修改版权信息内容
                else:
                    rights= Et.Element("{http://purl.org/dc/elements/1.1/}rights")
                    rights.text = self.rights
                content_root.append(rights)

            # 修改书名
            if self.title:
                title = content_root.find(".//{http://purl.org/dc/elements/1.1/}title")  # 查找<title>标签
                if title is not None:  # 如果找到<title>标签
                    title.text = self.title  # 修改标题内容
                else:
                    title = Et.Element("{http://purl.org/dc/elements/1.1/}title")
                    title.text = self.title
                content_root.append(title)


            # 修改作者
            # 找到所有的<creator>标签并删除
            if self.author:
                creators = content_root.findall(".//{http://purl.org/dc/elements/1.1/}creator")
                if creators is not None:
                    for creator in creators:
                        content_root.remove(creator)
                else:
                    creators = Et.Element("{http://purl.org/dc/elements/1.1/}creator")

                # 添加新的<creator>标签
                for author in self.author:
                    creators.text = author
                    content_root.append(creators)

            if self.isbn:
                isbn = content_root.find(".//{http://purl.org/dc/elements/1.1/}identifier")
                if isbn is not None:
                    for identifier in self.identifier:
                        # 检查是否是ISBN（通常以`urn:isbn:`开头）
                        if identifier.text.startswith("urn:isbn:"):
                            identifier.text = f"urn:isbn:{self.isbn}"  # 更新ISBN
                            content_root.append(identifier)
                            break
                else:
                    # 如果没有找到ISBN，添加一个新的<identifier>标签
                    identifier = Et.Element("{http://purl.org/dc/elements/1.1/}identifier")
                    identifier.text = f"urn:isbn:{self.isbn}"
                    identifier.set("id", "ISBN")  # 可选：设置ID
                    content_root.append(identifier)
            if self.asin:
                asin = content_root.find(".//{http://purl.org/dc/elements/1.1/}identifier")
                if asin is not None:
                    for identifier in self.identifier:
                        # 检查是否是ISBN（通常以`urn:asin:`开头）
                        if identifier.text.startswith("urn:asin:"):
                            identifier.text = f"urn:asin:{self.asin}"  # 更新ASIN
                            content_root.append(identifier)
                            break
                else:
                    # 如果没有找到ISBN，添加一个新的<identifier>标签
                    identifier = Et.Element("{http://purl.org/dc/elements/1.1/}identifier")
                    identifier.text = f"urn:asin:{self.asin}"
                    identifier.set("id", "ASIN")  # 可选：设置ID
                    content_root.append(identifier)
                    # 如果没有找到ASIN，添加一个新的<identifier>标签
            # 修改标签（如果提供了新标签列表）

            # 找到所有的<subject>标签并删除
            if self.subject:
                subjects = content_root.findall(".//{http://purl.org/dc/elements/1.1/}subject")
                for subject in subjects:
                    content_root.remove(subject)
                else:
                    subjects = Et.Element("{http://purl.org/dc/elements/1.1/}subject")

                # 添加新的<creator>标签
                for subject in self.subject:
                    subjects.text = subject
                    content_root.append(subjects)
            if self.publisher:
                publisher = content_root.find(".//{http://purl.org/dc/elements/1.1/}publisher")  # 查找<publisher>标签
                if publisher is not None:  # 如果找到<publisher>标签
                    ...  # 修改出版社内容
                else:
                    publisher = Et.Element("{http://purl.org/dc/elements/1.1/}publisher")
                publisher.text = self.publisher
                content_root.append(publisher)

            # 修改出版时间（如果提供了新出版时间）
            if self.published_date:
                # 找到所有的<dc:date>标签
                dates = content_root.findall(".//{http://purl.org/dc/elements/1.1/}date")
                for date in dates:
                    # 检查是否是出版时间（通常使用`event="publication"`属性）
                    if date.get("event") == "publication":
                        date.text = self.published_date  # 更新出版时间
                        break
                else:
                    # 如果没有找到出版时间，添加一个新的<dc:date>标签
                    date = Et.Element("{http://purl.org/dc/elements/1.1/}date")
                    date.text = self.published_date
                    date.set("event", "publication")  # 设置属性
                    content_root.append(date)

            # 修改修改时间（如果提供了新修改时间）
            # 找到所有的<dc:date>标签
            dates = content_root.findall(".//{http://purl.org/dc/elements/1.1/}date")
            for date in dates:
                # 检查是否是修改时间（通常使用`event="modification"`属性）
                if date.get("event") == "modification":
                    date.text = self.modified_date  # 更新修改时间
                    break
            else:
                # 如果没有找到修改时间，添加一个新的<dc:date>标签
                date = Et.Element("{http://purl.org/dc/elements/1.1/}date")
                date.text = self.modified_date
                date.set("event", "modification")  # 设置属性
                content_root.append(date)

            # 保存修改后的`content.opf`文件
            content_tree.write(content_opf_path, encoding="utf-8", xml_declaration=True)  # 将修改后的XML写回文件

            # 重新打包EPUB文件
            new_epub_path = new_file_path  # .replace(".epub", "_modified.epub")  # 新EPUB文件的路径
            with zipfile.ZipFile(new_epub_path, 'w') as zip_ref:  # 创建一个新的ZIP文件
                for root, dirs, files in os.walk(temp_dir):  # 遍历临时目录中的所有文件
                    for file in files:
                        file_path = os.path.join(root, file)  # 获取文件的完整路径
                        arcname = os.path.relpath(file_path, temp_dir)  # 计算文件在ZIP中的相对路径
                        zip_ref.write(file_path, arcname)  # 将文件添加到ZIP中

            # 删除临时目录
            shutil.rmtree(temp_dir)  # 递归删除临时目录及其内容
            return True
        except Exception as error:
            print(error)
            return False
        pass

    def change_metadata(
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