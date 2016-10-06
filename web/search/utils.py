import csv

with open('/Users/Kostiantyn/Desktop/strains/strain_import.csv') as f:
    reader = csv.reader(f)
    headers = next(reader, None)

    raw = []

    for row in reader:
        row = {
            'name': row[0],
            'variety': row[1],
            'category': row[2],
            'effects': row[3],
            'benefits': row[4],
            'side_effects': row[5],
            'flavor': row[6],
            'about': row[7]
        }

        raw.append(row)

    print('strains', raw)
