<!--
 * @Date: 2024-07-18 21:44:17
 * @LastEditors: youyu 2000601104@cjlu.edu.cn
 * @LastEditTime: 2024-07-22 23:47:12
-->
# EpubEdit

> Regarding epubedit, this is a Python package for viewing and editing epub file metadata

## Installation and Usage

* Installation:

``` Python
pip install epubedit
```

* Usage

``` Python

from epubedit import read_epub_info


book = read_epub_info('book_name')
book.get_infos()
```

## Functions

### read_info(str) -> str | list

Read the value of a single metadata
Supported parameters:
            [
                'epub_version',
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

Example:

``` Python
from epubedit import read_epub_info

book = read_epub_info("Moby Dick.epub")
print(book.get_info('book_name'))
```

Running results

```Python
Moby Dick; Or, The Whale
```

### read_infos(list) -> list

Pass a list and transmit the corresponding metadata values

``` Python
from epubedit import read_epub_info

book = read_epub_info("Moby Dick.epub")
print(book.get_infos(["book_name", "epub_version", "language"]))
```

Running results

```Python
{"book_name": "Moby Dick; Or, The Whale", "epub_version": "3.0", "language": "en"}
```

### read_all_infos() -> dict

No input value, all metadata information is transmitted. If there is a lack of relevant information in EPUB, it will return str: "" or list: []

``` Python
book = read_epub_info('Moby Dick.epub')
print(book.get_all_infos())
```

Running results

```Python
{
    "epub_version": "3.0",
    "rights": "Public domain in the USA.",
    "book_name": "Moby Dick; Or, The Whale",
    "author": ["Herman Melville"],
    "isbn": "",
    "asin": "",
    "publisher": "",
    "published_date": "",
    "modified_date": "2024-07-20T22:24:39Z",
    "language": "en",
    "subject": [
        "Whaling -- Fiction",
        "Sea stories",
        "Psychological fiction",
        "Ship captains -- Fiction",
        "Adventure stories",
        "Mentally ill -- Fiction",
        "Ahab, Captain (Fictitious character) -- Fiction",
        "Whales -- Fiction",
        "Whaling ships -- Fiction",
    ],
}
```

## Links

* **GitHub Repository :** [EpubEdit](https://github.com/childeyouyu/epubedit)
