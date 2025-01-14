from src.epubedit.epubedit import Epubedit


book = Epubedit('改变世界的机器：精益生产之道 【美】沃麦克（Womack，J. P. ）,【英】琼斯（Jones，D. T. ） etc. Z-Library-20240919135458-4tk0xsv.epub')
print(book.get_all_metadata())
