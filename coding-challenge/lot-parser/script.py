#First part
import os
import json
import codecs
import sys

#Get all the files in the directory
data_path1 = 'data/2015-03-18'
data_path2 = 'data/2017-12-20'

files1 = os.listdir(data_path1)
files2 = os.listdir(data_path2)

names = []
titles = []
prices = []
currencies = []
total_value = {}

#Parse through the files
filepaths = []

for f in files1:
    file_path = data_path1 + '/' + f
    filepaths.append(file_path)
    
for f in files2:
    file_path = data_path2 + '/' + f
    filepaths.append(file_path)
    
for file_path in filepaths:
    with codecs.open(file_path,'r', encoding = 'utf-8') as file:
        prev_line = ''
        for line in file:
            if '<title>' in prev_line: #getting the title and artist
                titleline = line.lstrip()
                for i in range(len(titleline)):
                    c = titleline[i]
                    if c == ':': #colon seperates title and artist
                        break
                name = titleline[:i]
                title = titleline[i+2:-1]
                
                #Some of the names have dates in them, so I just remove them
                for i in range(len(name)):
                    c = name[i]
                    if c == '(':
                        name = name[:i-1]
                        break
                        
            if 'Price realised' in prev_line: # getting the price
                priceline = line.lstrip()
                price = ''.join(c for c in priceline if c.isdigit())
                currency = priceline[5:8]
            prev_line = line
        
        #Store the values for this html file
        
        #convert currency
        if currency != 'USD':
            currency = 'USD'
            price = str(round(int(price) / 1.34))
        
        names.append(name)
        titles.append(title)
        prices.append(price)
        currencies.append(currency)
        
        #get total value
        if name in total_value.keys():
            total_value[name] += int(price)
        else:
            total_value[name] = int(price)

#Each works in html file
works = [{'title': title, 'currency': currency, 'amount': price} for title, currency, price in zip(titles, currencies, prices)]
        
#Combine the author's works to be shown together
nameset = list(set(names))

artist_works = [] #all the artist's works
artist_totals = [] #the total lifetime value

for i in range(len(nameset)):
    artist_works.append([])
    name = nameset[i]
    artist_totals.append('USD ' + str(total_value[name]))

for i in range(len(names)):
    name = names[i]
    name_index = nameset.index(name)
    work = works[i]
    artist_works[name_index].append(work)
 
output = [{'artist': artist, 'totalValue': value, 'works': work} for artist, value, work in zip(nameset, artist_totals, artist_works)]

std

output = json.dumps(output)

sys.stdout.write(output)