import requests
from collections import Counter
from itertools import product


bind = 'USDT'
triples, sort, trade = [[] for i in range(3)]

url = 'https://gate.kickex.com/api/v1/market/pairs?type=market'
data = [dat["pairName"] for dat in requests.get(url).json()]
coins = [i.split('/') for i in data]

for first_pair, second_pair, third_pair in product(coins, coins, coins):
    condition = [first_pair != second_pair, first_pair != third_pair, second_pair != third_pair]
    if all(condition):
        triples.append([first_pair[0], first_pair[1],
                        second_pair[0], second_pair[1],
                        third_pair[0], third_pair[1]])

for pairs in triples:
    pair_count = Counter(pairs)

    if len(pair_count) == 3:
        if bind in pairs[1] and bind in pairs[5]:
            sort.append([f'{pairs[0]}/{pairs[1]}', f'{pairs[2]}/{pairs[3]}', f'{pairs[4]}/{pairs[5]}'])

for pairs in sort:
    first_pair, second_pair, third_pair = pairs[0].split('/'), pairs[1].split('/'), pairs[2].split('/')

    if first_pair[0] == second_pair[0]:
        trade.append({pairs[0]: 'Buy', pairs[1]: 'Sell', pairs[2]: 'Sell'})
    elif first_pair[0] == second_pair[1]:
        trade.append({pairs[0]: 'Buy', pairs[1]: 'Buy', pairs[2]: 'Sell'})
    else:
        trade.append({pairs[0]: 'Buy', pairs[1]: 'Sell', pairs[2]: 'Buy'})


#That needs to write example in txt file

# with open('pairs.txt', 'w', encoding='utf-8') as file:
#     for record in trade:
#         for key, value in record.items():
#             file.write(f' {key} : {value}')
#         file.write('\n')
