"""simple script to scrape and analyze a bunch of vitamin brands!"""

import threading
import requests
import bs4
import os
import csv

os.chdir('/Users/ilja/Dropbox/labdoor')

# scraping main page
res = requests.get("https://labdoor.com/rankings")
res.raise_for_status()
soup = bs4.BeautifulSoup(res.text, 'lxml')
categories = soup.findAll("a", {"class": "rankingsListItemLink"})
cat_names = soup.findAll("span", {"class": "rankingsListItemDesc"})

print(len(categories))

# needed to append brands
not_two_word_brands = set(['MegaFood', 'Garden of Life', 'Solgar', 'Wellesse', 'MusclePharm',
                           'MyProtein', 'Sheer Strength Labs', 'Bodybuilding.com', 'Bodytech',
                           'Twinlab', 'MRM', 'MET-Rx', 'Cellucor', 'UltraChamp',
                           'Bluebonnet', 'GNC', 'Solaray', 'Swanson', 'Citracal', 'Vitafusion', 'Posture-D',
                           'Child Life Essentials', 'Herbalife', 'Caltrate', 'TUMS',
                           'NutriONN', 'Nutrigold', 'NatureWise', 'Deva', 'Vitafusion', 'Decacor',
                           'Ghirardelli', 'Lindt', 'Godiva', '365', 'Gatorade', 'Ultima', 'WHC',
                           'OmegaVia', 'Omax3', 'The Vitamin Shoppe', 'InnovixLabs', 'Life & Food', 'Bausch and Lomb',
                           'Schiff', 'Sundown', 'Natrol', 'DietWorks', 'Nutribody', 'MagixLabs', 'NuSci', 'VitaBreeze',
                           'BodyTech', 'Metagenics', 'Good State Health', 'Kal', 'MagOx', 'ChildLife', 'One A Day',
                           'Myogenix', 'Hyperbiotics', 'Advocare', 'Natrogix', 'Pedia-Lax', 'Hyperbiotics', 'Garden Of Life',
                           'Phillips', 'NuTru', 'Ovega-3', 'Amala', 'VeganSafe', 'Good \'n Natural'])

# we'll have to merge 12 csvs later
all_csvs = []


def get_all_products(start, stop, batch_n):

    # setting up file
    name = f'supps_{batch_n}.csv'
    all_csvs.append(name)
    f = open(name, 'w')
    csv_writer = csv.writer(f)

    # scraping categories
    for i in range(start, stop):
        cat_url = "https://labdoor.com"+categories[i]["href"]
        cat_name = cat_names[i].text.strip()
        print(f'[1] STARTING NEW CATEGORY.... {cat_name}')

        res = requests.get(cat_url)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, 'lxml')

        # because some web pages have 2 containers and some only one - we want to zoom in on the one we care about
        container = soup.find("ul", {"class": "categoryList js-sortContainer"}).descendants
        products = []

        # extra loop because of the "zoom in", but I couldn't find a better way
        for c in container:
            try:
                p_url = "https://labdoor.com"+c.find("a", {"class": "categoryListItemLink"})['href']
                p_name = c.find("span", {"class": "categoryListItemNameV2"}).text
                products.append((p_url, p_name))
            except TypeError:
                pass

        print(f'there are {len(products)} products in this category!')

        # scraping proudcts
        for j in range(len(products)):
            p_url, p_name = products[j]
            print(f'[2] STARTING NEW PRODUCT.... {p_name}, {p_url}')

            res = requests.get(p_url)
            res.raise_for_status()
            soup = bs4.BeautifulSoup(res.text, 'lxml')
            labels = soup.findAll("blockquote", {"class": "widgetPercentage mBM"})
            try:
                last_label = soup.findAll("blockquote", {"class": "widgetPercentage mBXL"})
                labels.append(last_label[0])
            except:
                pass

            # let's also get the brand
            for ntw in not_two_word_brands:
                if p_name.startswith(ntw):
                    brand = ntw
                    break  # need this break or will over-write
                else:
                    brand = " ".join(p_name.split()[:2])

            # scraping data
            for k in range(len(labels)):
                desc = list(labels[k].descendants)
                label = desc[2]
                data_val = desc[4]["data-value"]
                csv_writer.writerow([cat_name, p_name, brand, label, data_val])

    print(f'done executing batch from {start} to {stop}')
    f.close()


# we know that length of categories is 36
# get_all_products(0, 36, 'one_go')


# # we download each batch into a separate file, otherwise rows fuck up
threads = []
for i in range(0, 36, 3):
    start = i
    end = i+3
    t = threading.Thread(target=get_all_products, args=(start, end, start))
    threads.append(t)
    t.start()
for t in threads:
    t.join()
print(f'DONE with total threads of {len(threads)}')

# # then we merge them into one
with open('supps_TOTAL.csv', 'w') as fw:
    csv_writer = csv.writer(fw)

    for c in all_csvs:
        with open(c, 'r') as fr:
            csv_reader = csv.reader(fr)

            for row in csv_reader:
                csv_writer.writerow(row)


# ==============================================================================
# EXCEL VERSION - WAY MORE COMPLICATED, DUE TO HAVING TO MANUALLY COUNT ROWS

# import openpyxl
# wb = openpyxl.Workbook()
# s = wb.active
# product_ns = []

# def get_all_products(start, stop):
#     # scraping categories
#     for i in range(start, stop):
#         cat_url = "https://labdoor.com"+categories[i]["href"]
#         cat_name = cat_names[i].text
#         print(f'[1] STARTING NEW CATEGORY.... {cat_name}')
#
#         res = requests.get(cat_url)
#         res.raise_for_status()
#         soup = bs4.BeautifulSoup(res.text, 'lxml')
#
#         # because some web pages have 2 containers and some only one - we want to zoom in on the one we care about
#         container = soup.find("ul", {"class": "categoryList js-sortContainer"}).descendants
#         products = []
#
#         # extra loop because of the "zoom in", but I couldn't find a better way
#         for c in container:
#             try:
#                 p_url = "https://labdoor.com"+c.find("a", {"class": "categoryListItemLink"})['href']
#                 p_name = c.find("span", {"class": "categoryListItemNameV2"}).text
#                 products.append((p_url, p_name))
#             except TypeError:
#                 pass
#
#         product_n = len(products)
#         product_ns.append(product_n)
#         print(f'there are {product_n} products in this category!')
#
#         # scraping proudcts
#         for j in range(product_n):
#             p_url, p_name = products[j]
#             print(f'[2] STARTING NEW PRODUCT.... {p_name}, {p_url}')
#
#             res = requests.get(p_url)
#             res.raise_for_status()
#             soup = bs4.BeautifulSoup(res.text, 'lxml')
#             labels = soup.findAll("blockquote", {"class": "widgetPercentage mBM"})
#             last_label = soup.findAll("blockquote", {"class": "widgetPercentage mBXL"})
#             labels.append(last_label[0])
#             label_n = len(labels)
#
#             # let's also get the brand
#             for ntw in not_two_word_brands:
#                 if p_name.startswith(ntw):
#                     brand = ntw
#                     break  # need this break or will over-write
#                 else:
#                     brand = " ".join(p_name.split()[:2])
#
#             # scraping data
#             for k in range(label_n):
#                 desc = list(labels[k].descendants)
#                 label = desc[2]
#                 data_val = desc[4]["data-value"]
#
#                 line_num = i*product_ns[i-1]*label_n + j*label_n + k + 1
#                 [print(line_num)]
#
#                 # write the categogry in column A
#                 s['A'+str(line_num)] = str(cat_name)
#
#                 # write the name of the product in column B
#                 s['B'+str(line_num)] = str(p_name)
#
#                 # write the brand in column c
#                 s['C'+str(line_num)] = str(brand)
#
#                 # write the 5 labels in column d
#                 s['D'+str(line_num)] = str(label)
#
#                 # write the 5 data points in column e
#                 s['E'+str(line_num)] = str(data_val)
#
#             print('saving...')
#             wb.save('supps.xlsx')
#
#     print(f'done executing batch from {start} to {stop}')
#
#
# get_all_products(0, len(categories))


# implementing threading to make it more efficient
# OK SO THE BELOW WORKS, BUT THE PROBLEM IS IT COMPLETELY FUCKS UP ROWS. CBA.
# threads = []
# for i in range(0, 9, 3):
#     start = i
#     end = i+2
#     t = threading.Thread(target=get_all_products, args=(start, end))
#     threads.append(t)
#     t.start()
# for t in threads:
#     t.join()
# print(f'DONE with total threads of {len(threads)}')

# OLD DIDN'T WORK BECAUSE SOME PAGES HAD MULTIPLE CONTAINERS
# ==============================================================================
# product_urls = container.findAll("a", {"class": "categoryListItemLink"})
# product_names = container.findAll("span", {"class": "categoryListItemNameV2"})
# product_n = len(product_urls)
# print(product_n)

# scraping products
# for j in range(2):
#     p_url = "https://labdoor.com"+product_urls[j]['href']
#     p_name = product_names[j].text
#     print(f'scraping product --> {p_name}, {p_url}')
