from src.epubedit.epubedit import Epubedit
from datetime import datetime

#
# book = Epubedit('book.epub')
# print(book.get_metadata('epub_version'))
# print(book.get_metadata('book_name'))
# print(book.get_metadata('author_name'))
# print(book.get_metadata('publisher_name'))
# print(book.get_metadata('ISBN'))
# print(book.get_metadata('ASIN'))
# print(book.get_metadata('bookid'))
# print(book.get_metadata('language'))
#
# print(book.get_all_metadata())



book = Epubedit("book.epub")

book.change_metadata("epub_version", "6")
book.change_metadata("rights", "无版权")
book.change_metadata("book_name", "新书")
book.change_metadata("ISBN", "95675226")
book.change_metadata("ASIN", "89525226")
book.change_metadata("publication_date", f"{datetime.today()}")

book.change_metadata('author_name', '魏冬旭')
book.change_metadata('publisher_name', "九州出版社")

book.commit()

print(book.get_all_metadata())