import pandas as pd

# Загрузка CSV-файла
df = pd.read_csv('copa_results.csv')

# Создание объекта Excel-файла
excel_file = 'copa_results.xlsx'

# Сохранение данных в Excel
df.to_excel(excel_file, index=False)
