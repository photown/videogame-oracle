from topia.termextract import extract

class KeywordExtractor:
  def __init__(self):
    self.extractor = extract.TermExtractor()
    self.extractor.filter = extract.permissiveFilter

  def extract(self, text):
    return self.extractor(text.lower())