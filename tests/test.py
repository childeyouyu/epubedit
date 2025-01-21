from epubedit import Epubedit
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


book = Epubedit("book.epub") # Replace your book.epub with your own one

book.change_metadata("epub_version", "3.0")
book.change_metadata("book_name", "新书")
book.change_metadata("author_name", "魏冬旭")
book.change_metadata("publisher_name", "九州出版社")

book.commit()

print(book.get_all_metadata())
