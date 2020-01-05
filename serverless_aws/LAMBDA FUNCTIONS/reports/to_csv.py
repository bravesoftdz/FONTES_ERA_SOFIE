from tempfile import SpooledTemporaryFile
from csv import DictWriter

def to_csv(fields: list, data: list):
    """
    
    """
    file = SpooledTemporaryFile(mode='w+t', encoding='UTF-8')
    file.write(u'\ufeff')
    
    f_csv = DictWriter(file, fields, delimiter=';')
    f_csv.writeheader()
    f_csv.writerows(data)
    
    file.seek(0)
    
    return file.read()