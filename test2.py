import zipfile
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import contextlib
import tempfile


class EPUBModifier:
    def __init__(
        self,
        file_path,
        epub_version=None,
        rights=None,
        title=None,
        author=None,
        isbn=None,
        asin=None,
        subject=None,
        publisher=None,
        published_date=None,
        modified_date=None,
    ):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"EPUB file not found: {file_path}")

        self.epub_version = epub_version
        self.rights = rights
        self.title = title
        self.author = author
        self.isbn = isbn
        self.asin = asin
        self.subject = subject
        self.publisher = publisher
        self.published_date = published_date
        self.modified_date = modified_date
        self.namespaces = {
            "ns": "urn:oasis:names:tc:opendocument:xmlns:container",
            "dc": "http://purl.org/dc/elements/1.1/",
            "opf": "http://www.idpf.org/2007/opf",
        }

    def _create_temp_directory(self):
        """创建临时目录并返回路径"""
        return Path(tempfile.mkdtemp(prefix="epub_"))

    def _clean_directory(self, directory):
        """安全清理目录"""
        try:
            if directory.exists():
                shutil.rmtree(directory)
        except Exception as e:
            print(f"Warning: Failed to clean directory {directory}: {e}")

    def modify_epub(self, new_file_path=None):
        """修改 EPUB 文件"""
        if new_file_path is None:
            new_file_path = self.file_path.parent / f"modified_{self.file_path.name}"
        new_file_path = Path(new_file_path)

        temp_dir = None
        try:
            temp_dir = self._create_temp_directory()

            # 解压 EPUB 文件
            with zipfile.ZipFile(self.file_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # 处理 container.xml
            container_path = temp_dir / "META-INF" / "container.xml"
            if not container_path.exists():
                raise FileNotFoundError("container.xml not found in EPUB")

            container_tree = ET.parse(container_path)
            rootfile = container_tree.getroot().find(".//ns:rootfile", self.namespaces)
            if rootfile is None:
                raise ValueError("Invalid EPUB: rootfile element not found")

            # 处理 content.opf
            content_opf_path = temp_dir / rootfile.get("full-path")
            if not content_opf_path.exists():
                raise FileNotFoundError(f"content.opf not found at: {content_opf_path}")

            # 确保父目录存在
            new_file_path.parent.mkdir(parents=True, exist_ok=True)

            # 更新 metadata
            self._update_metadata(content_opf_path)

            # 创建新的 EPUB
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
        """更新 metadata 部分"""
        tree = ET.parse(content_opf_path)
        root = tree.getroot()
        metadata = root.find(f".//{{{self.namespaces['opf']}}}metadata")

        if metadata is None:
            metadata = ET.SubElement(root, f"{{{self.namespaces['opf']}}}metadata")

        # 更新各项 metadata
        if self.epub_version:
            root.set("version", self.epub_version)

        if self.title:
            self._update_dc_element(metadata, "title", self.title)

        if self.author:
            self._update_creator_elements(metadata)

        if self.rights:
            self._update_dc_element(metadata, "rights", self.rights)

        # 保存更新后的文件
        tree.write(content_opf_path, encoding="utf-8", xml_declaration=True)

    def _update_dc_element(self, metadata, element_name, value):
        """更新或创建 DC 元素"""
        element = metadata.find(f".//{{{self.namespaces['dc']}}}{element_name}")
        if element is None:
            element = ET.SubElement(
                metadata, f"{{{self.namespaces['dc']}}}{element_name}"
            )
        element.text = value

    def _update_creator_elements(self, metadata):
        """更新创建者信息"""
        # 移除现有的创建者元素
        for creator in metadata.findall(f".//{{{self.namespaces['dc']}}}creator"):
            metadata.remove(creator)

        # 添加新的创建者元素
        if isinstance(self.author, str):
            authors = [self.author]
        else:
            authors = self.author

        for author in authors:
            creator = ET.SubElement(metadata, f"{{{self.namespaces['dc']}}}creator")
            creator.text = author


if __name__ == "__main__":
    modifier = EPUBModifier(
        file_path="改变世界的机器：精益生产之道 【美】沃麦克（Womack，J. P. ）,【英】琼斯（Jones，D. T. ） etc. Z-Library-20240919135458-4tk0xsv.epub",
        epub_version="3.0",
        rights="版权2023",
        title="N新标题",
        author=["作者", "魏冬旭"],
        isbn="1234567890",
        asin="B0ABCD1234",
        subject=["小时", "Science"],
        publisher="New Publisher",
        published_date="2023-01-01",
        modified_date="2023-10-01",
    )

    if modifier.modify_epub("modified_example.epub"):
        print("EPUB modified successfully!")
    else:
        print("Failed to modify EPUB.")
