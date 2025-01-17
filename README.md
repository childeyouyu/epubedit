<!--
 * @Date: 2024-07-18 21:44:17
 * @LastEditors: youyu 2000601104@cjlu.edu.cn
 * @LastEditTime: 2024-07-22 23:47:12
-->
# EpubEdit

> **EpubEdit** is a Python package for viewing and editing EPUB file metadata.

## Installation and Usage

* Installation:

``` Python
pip install epubedit
```

* Usage:

``` Python
from epubedit import Epubedit # import the library

book = Epubedit('book_name') # create Epubedit object 
book.get_metadata() 
```

## Methods

1. get_metadata -> `str | List[str]`
2. get_selected_metadata -> `Dict[str: str]`
3. get_all_metadata -> `Dict[str: str]`

  ### 1. get_metadata(str) -> `str | List`

  Read the value of a single metadata 
  
  Supported parameters:

  - "epub_version"
  - "book_name"
  - "author_name"
  - "publisher_name"
  - "ISBN"
  - "ASIN"
  - "bookid"
  - "describe"
  - "language"
  - "rights"
  - "publication_date"
            

  Example:
  
  ``` Python
  from epubedit import Epubedit
  
  book = Epubedit("Moby Dick.epub")
  print(book.get_metadata('book_name'))
  ```

  Running results
  
  ```Python
  Moby Dick; Or, The Whale
  ```
  ### 2. get_selected_metadata(Iterable[str]) -> `Dict[str: str]`
  
  Pass a list and transmit the corresponding metadata values
  
  ``` Python
  from epubedit import Epubedit
  
  book = Epubedit("Moby Dick.epub")
  print(book.get_selected_metadata(["book_name", "epub_version", "language"]))
  ```
  
  Running results
  
  ```Python
  {"book_name": "Moby Dick; Or, The Whale", "epub_version": "3.0", "language": "en"}
  ```

### 3. get_all_metadata() -> `Dict[str: str]`

No input value, all metadata information is transmitted. If there is a lack of relevant information in EPUB, it will return str: "" or list: []

``` Python
book = Epubedit('Moby Dick.epub')
print(book.get_all_metadata())
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
        "Whaling ships -- Fiction"
    ]
}
```

### change_metadata(Dict[str: str]) -> `None`

```
book = Epubedit("your.epub")

book.change_metadata("epub_version", "3.0")
book.change_metadata("book_name", "new_name")
book.change_metadata("author_name", "new_author")
book.change_metadata("publisher_name", "new_publisher")

book.commit()
```

## Links

* **GitHub Repository :** [EpubEdit](https://github.com/childeyouyu/epubedit)
