# Identify all ZIP files and other file types which are actually zip files

import zipfile
from identifier import Result

class IdInfo:
	def __init__(self, name, description, file_set):
		self.name = name
		self.description = description
		self.file_set = set(file_set)

ZIP_PATTERNS = [
	'50 4B 03 04 14'
]

ZIP_CONTENT_IDENTIFIERS = [
	IdInfo('DOCX', 'Microsoft Office Word', ['[Content_Types].xml', 'word/document.xml']),
	IdInfo('XLSX', 'Microsoft Office Excel', ['[Content_Types].xml', 'xl/workbook.xml']),
	IdInfo('PPTX', 'Microsoft Office Powerpoint', ['[Content_Types].xml', 'ppt/presentation.xml']),
	IdInfo('JAR', 'Java Archive', ['META-INF/MANIFEST.MF']),
]

class ZipResolver:
	def identify(self, stream):
		with zipfile.ZipFile(stream, mode='r') as zf:
			filename_set = set([info.filename for info in zf.infolist()])
			for id_data in ZIP_CONTENT_IDENTIFIERS:
				if len(id_data.file_set & filename_set) == len(id_data.file_set):
					return Result(id_data.name, description=id_data.description)

def load(hound):
	hound.add_matches(ZIP_PATTERNS, ZipResolver())