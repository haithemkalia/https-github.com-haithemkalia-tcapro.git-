import pandas as pd

# Lire le fichier Excel
df = pd.read_excel('قائمة الزبائن معرض_أكتوبر2025 (38).xlsx')

print('Nombre total de lignes:', len(df))
print('\nNombre de colonnes:', len(df.columns))
print('\nListe complète des colonnes:')
for i, col in enumerate(df.columns):
    print(f'{i+1}. {col}')

print('\nInformations sur les données:')
print(df.info())

print('\nPremières 3 lignes:')
print(df.head(3))

print('\nDernières 3 lignes:')
print(df.tail(3))