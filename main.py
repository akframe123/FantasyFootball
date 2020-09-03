import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from tabulate import tabulate
import numpy

class League:
    def __init__(self, league_name, link_qb, link_rb, link_wr, link_te, link_k, link_dst):
        self.league_name = league_name
        self.qbs = self.add_qbs(link_qb)
        self.rbs = self.add_rbs(link_rb)
        self.wrs = self.add_wrs(link_wr)
        self.tes = self.add_tes(link_te)
        # self.ks = self.add_ks(link_k)
        # self.dsts = self.add_dsts(link_dst)
        # self.pprint(self.qbs)
        # self.pprint(self.rbs)
        # self.pprint(self.wrs)
        # self.pprint(self.tes)
        # self.pprint(self.ks)
        # self.pprint(self.dsts)
        # self.set_league_points_rules()
    
    def pprint(self,df):
        print(tabulate(df,headers='keys', tablefmt='psql'))

    def set_league_points_rules(self):
        rules_dict_qb = {'td (Touchdowns Passes)':4,\
            'yds (Passing Yards)':0.04,'int (Interceptions Thrown)':-2,\
                'yds (Rushing Yards)':.1, 'fl (Fumbles Lost)':-2}
        self.adjust_points_qb(rules_dict_qb, self.qbs)

        rules_dict_wr_rb = {'td (Rushing Touchdowns)':6, 'yds (Rushing Yards)':0.1\
            , 'yds (Receiving Yards)':0.1, 'fl (Fumbles Lost)':-2, \
                'td (Receiving Touchdowns)':6,'ReFD (Receiving First Down)':1,\
                    'RuFD (Rushing First Down)':1}
        self.adjust_points_wr_rb(rules_dict_wr_rb, self.wrs)
        self.adjust_points_wr_rb(rules_dict_wr_rb, self.rbs)
       
        rules_dict_te = {'yds (Receiving Yards)':0.1, 'fl (Fumbles Lost)':-2, \
        'td (Receiving Touchdowns)':6,'ReFD (Receiving First Down)':1}
        self.adjust_points_te (rules_dict_te, self.tes)

        # self.pprint(self.wrs)
        # self.pprint(self.rbs)
        self.pprint(self.tes)

    def parse_link(self, link, defense=False):
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')

        table = soup.findChildren('table')
        rows = table[0].findChildren(['th','tr'])

        headers = table[0].find('tr','TableBase-headTr').text
        headers_lst = []

        for i in headers.split('\n'):
            if i != '\n' and i:
                headers_lst.append(i.strip())

        final_header = [headers_lst[0]]
        if not defense:
            final_header.append("Position")
            final_header.append("Team")
        headers_lst_clean = [x for x in headers_lst[1:] if x != '']

        for i,j in zip(headers_lst_clean[0::2], headers_lst_clean[1::2]):
            final_header.append(i+" (" + j + ")")
        return (final_header,rows)
    
    def get_players_by_row(self,rows,df):
        for row in rows:
            cells = row.findChildren('td')
            cur_player = []
            for cell in cells:
                if len(cell) > 1:
                    pos = cell.find('span')
                    for i in pos.text.strip().split("  "):
                        if i != "" and len(i.strip()) != 0:
                            cur_player.append(i.strip())
                else:
                    try:
                        cur_player.append(float(cell.string.strip()))
                    except:
                        cur_player.append(0.0)
            if cur_player:
                to_append = pd.Series(cur_player, index = df.columns)
                df = df.append(to_append,ignore_index=True)
        return df

    def add_qbs(self, link):
        parsed = self.parse_link(link)[0]
        rows = self.parse_link(link)[1]

        df_players_qb = pd.DataFrame(columns=parsed)
        df_players_qb = self.get_players_by_row(rows,df_players_qb)
    
        # print(tabulate(df_players_qb,headers='keys', tablefmt='psql'))
        return df_players_qb
    
    def add_rbs(self, link):
        parsed = self.parse_link(link)[0]
        rows = self.parse_link(link)[1]

        df_players_rb = pd.DataFrame(columns=parsed)
        df_players_rb = self.get_players_by_row(rows, df_players_rb)
        
        # print(tabulate(df_players_rb,headers='keys', tablefmt='psql'))
        return df_players_rb
    
    def add_wrs(self, link):
        parsed = self.parse_link(link)[0]
        rows = self.parse_link(link)[1]

        df_players_wr = pd.DataFrame(columns=parsed)
        df_players_wr = self.get_players_by_row(rows, df_players_wr)
                
        # print(tabulate(df_players_wr,headers='keys', tablefmt='psql'))
        return df_players_wr
    
    def add_tes(self, link):
        parsed = self.parse_link(link)[0]
        rows = self.parse_link(link)[1]

        df_players_te = pd.DataFrame(columns=parsed)
        df_players_te = self.get_players_by_row(rows, df_players_te)
                        
        # print(tabulate(df_players_te,headers='keys', tablefmt='psql'))
        return df_players_te
    
    def add_ks(self, link):
        parsed = self.parse_link(link)[0]
        rows = self.parse_link(link)[1]

        df_players_k = pd.DataFrame(columns=parsed)
        df_players_k = self.get_players_by_row(rows, df_players_k)
                                
        # print(tabulate(df_players_k,headers='keys', tablefmt='psql'))
        return df_players_k

    def add_dsts(self, link):
        parsed = self.parse_link(link, True)[0]
        rows = self.parse_link(link, True)[1]

        df_players_dst = pd.DataFrame(columns=parsed)
        df_players_dst = self.get_players_by_row(rows, df_players_dst)
                                        
        # print(tabulate(df_players_dst,headers='keys', tablefmt='psql'))
        return df_players_dst

    def adjust_points_qb(self, d, df):
        # print(d)
        # self.pprint(df)
        for index,row in df.iterrows():
            tot_points = 0
            for i in d:
                tot_points += row[i]*d[i]
            df.at[index,'adjusted fantasy points'] = tot_points
        # self.pprint(self.qbs)
    
    def adjust_points_wr_rb(self, d, df):
        '''
        ReFD (Receiving First Down)
        RuFD (Rushing First Down)
        '''
        for index,row in df.iterrows():
            tot_points = 0
            for i in d:
                try:
                    tot_points += row[i]*d[i]
                except KeyError:
                    temp1 = row['yds (Receiving Yards)']/20 * d[i]
                    tot_points += temp1
                    df.at[index,"ReFD (Receiving First Down)"] = temp1
                    temp2 = row['yds (Rushing Yards)']/20 * d[i]
                    tot_points += temp2
                    df.at[index,"RuFD (Rushing First Down)"] = temp2
            df.at[index,'adjusted fantasy points'] = tot_points
        # self.pprint(df)
    
    def adjust_points_te(self, d, df):
        for index,row in df.iterrows():
            tot_points = 0
            for i in d:
                try:
                    tot_points += row[i]*d[i]
                except KeyError:
                    temp = row['yds (Receiving Yards)']/20 * d[i]
                    tot_points += temp
                    df.at[index,"ReFD (Receiving First Down)"] = temp
            df.at[index,'adjusted fantasy points'] = tot_points

league = League("Radical Ultimate FFF Experience",\
'https://www.cbssports.com/fantasy/football/stats/QB/2019/season/projections/ppr/',\
    'https://www.cbssports.com/fantasy/football/stats/RB/2019/season/projections/ppr/',\
        'https://www.cbssports.com/fantasy/football/stats/WR/2019/season/projections/ppr/',\
            'https://www.cbssports.com/fantasy/football/stats/TE/2019/season/projections/ppr/',\
                'https://www.cbssports.com/fantasy/football/stats/K/2019/season/projections/ppr/',\
                    'https://www.cbssports.com/fantasy/football/stats/DST/2019/season/projections/ppr/')

'''
below this is the orginal functioning bs
'''

# league.add_qbs('https://www.cbssports.com/fantasy/football/stats/QB/2019/season/projections/ppr/')
# URL = 'https://www.cbssports.com/fantasy/football/stats/QB/2019/season/projections/ppr/'
# page = requests.get(URL)

# soup = BeautifulSoup(page.content, 'html.parser')

# results = soup.find(id='TableBase')

# table = soup.findChildren('table')
# rows = table[0].findChildren(['th','tr'])

# headers = table[0].find('tr','TableBase-headTr').text
# headers_lst = []

# for i in headers.split('\n'):
#     if i != '\n' and i:
#         headers_lst.append(i.strip())

# final_header = [headers_lst[0]]
# final_header.append("Position")
# final_header.append("Team")
# headers_lst_clean = [x for x in headers_lst[1:] if x != '']

# for i,j in zip(headers_lst_clean[0::2], headers_lst_clean[1::2]):
#     final_header.append(i+" (" + j + ")")

# df_players = pd.DataFrame(columns=final_header)
# idx = 0
# for row in rows:
#     cells = row.findChildren('td')
#     cur_player = []
#     for cell in cells:
#         if len(cell) > 1:
#             pos = cell.find('span')
#             for i in pos.text.strip().split("  "):
#                 if i != "" and len(i.strip()) != 0:
#                     # print(i.strip())
#                     cur_player.append(i.strip())
#         else:
#             try:
#                 data = cell.string
#                 cur_player.append(float(cell.string.strip()))
#             except:
#                 cur_player.append(0.0)
#     if cur_player:
#         # df_players.loc[i] = cur_player
#         # idx += 1
#         to_append = pd.Series(cur_player, index = df_players.columns)
#         df_players = df_players.append(to_append,ignore_index=True)
#         # print("HERE ",cur_player)
# print(tabulate(df_players,headers='keys', tablefmt='psql'))