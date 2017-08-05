import csv
import pandas as pd


def read_csv():
    with open('data.csv', 'rb') as data:
        reader = csv.reader(data)
        row = [r for r in reader]
    print row[9]
    print row[88]


def scan_snippet():
    csv_file = "data.csv"
    df = pd.read_csv(csv_file)
    saved_column = df.Snippet


def scan_dict():
    with open('data.csv', 'rt') as f:
        reader = csv.DictReader(f)
        for row in reader:
            term = "help"
            words = row['Snippet'].split()
            if term in words:
                print row['Snippet']
                print "Found !"
                print ''


scan_dict()
