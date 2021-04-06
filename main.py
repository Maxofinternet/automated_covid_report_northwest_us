import feedparser
import os
import shapely
import shapefile
import plotly
from plotly.figure_factory._county_choropleth import create_choropleth
import xlrd
import geopandas
from googletrans import Translator
translator = Translator()
import requests
import pandas as pd
import io
import datetime
import plotly.figure_factory as ff
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import twint
import nest_asyncio
nest_asyncio.apply()


import json
import tweepy
consumer_key= ''
consumer_secret= ''
access_token=''
access_token_secret= ''
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

API = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
statestoletters = {'NV' : 'Nevada', 
                          'CA' : 'California', 
                          'UT' : 'Utah', 
                          'WY' : 'Wyoming' , 
                          'ID' : 'Idaho', 
                          'WA' : 'Washington', 
                          'OR' : 'Oregon', 
                          'MT' :'Montana',
                          'AK' : 'Alaska',
                          'HI' : 'Hawaii'}
listofsatates = ['Nevada', 'California', 'Utah', 'Wyoming', 'Idaho', 'Washington', 'Oregon', 'Montana', 'Alaska', 'Hawaii']

lts = inv_map = {v: k for k, v in statestoletters.items()}
datapop = pd.read_csv('/covid_county_population_usafacts.csv')
datapop = datapop.groupby(['State'], as_index = False).agg({ 'population' : 'sum'})
datapop['State'] = datapop['State'].map(statestoletters)
dictpop = dict(datapop[['State', 'population']].values)
level = 'state'
urlData = requests.get(url).content
rawData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
rawData = rawData[rawData['state'].isin(listofsatates)]
rawData['date'] = rawData['date'].astype('datetime64[ns]')
 
date_Nplus1_days_ago = rawData['date'].max() - datetime.timedelta(days=7)
curData = rawData[rawData['date'] >= date_Nplus1_days_ago]
joe = rawData['date'].max()
joe = joe.strftime("%d/%m/%Y")

joe1 = rawData['date'].max()
joe1 = joe1.strftime("%d_%m")
try : 
  os.makedirs('rapport bi-hebdomadaire COVID/'+joe1)
except : 
  dufhsdfiushdf = 0



datacases = []
columns = ['State']
columns.extend(sorted(set(curData['date']))[1:])
columns.extend(['total 7d'])

for i in set(curData['state']) :
  tempData = curData[curData['state'] == i]
  tempData = tempData.sort_values(by ='date')
  templist = [i]
  butlist =  tempData['cases'].tolist()
  t = 0
  for z in butlist[1:] :
    marg = z - butlist[t]
    marg = marg / dictpop[i] * 100000
    templist.extend([marg])
    t += 1
  totaldif = butlist[-1] - butlist[0] 
  totaldif = totaldif / dictpop[i] * 100000
  templist.extend([totaldif])
  datacases.append(templist)

tabstate = pd.DataFrame(datacases, columns=columns)
tabstate['code'] = tabstate['State'].map(lts)




tabstate.to_csv('rapport bi-hebdomadaire COVID/'+joe1+'/table.csv')
tabstatefig = tabstate[columns[0:-2]]
tabstatefig = tabstatefig.melt(id_vars=["State"], 
        var_name="Date", 
        value_name="Value")

  
fig = px.area(tabstatefig, x=tabstatefig['Date'], y =tabstatefig['Value'],  facet_col="State", facet_col_wrap=2, color=tabstatefig['State'])
fig.show()
fig2 = go.Figure(data=go.Choropleth(
    locations=tabstate['code'], # Spatial coordinates
    z = tabstate['total 7d'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = 'Nouveaux cas pour 100K habitants le {}'.format(joe))
)

fig2.update_layout(
    geo_scope='usa',
    margin={"r":0,"t":0,"l":0,"b":0},
    #geo = dict(visible = False)
)

fig2.show()


url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
datapop = pd.read_csv('/covid_county_population_usafacts.csv')
datapop['State'] = datapop['State'].map(statestoletters)
dictpop = dict(datapop[['countyFIPS', 'population']].values)
level = 'county'

listofsatates = ['Nevada', 'California', 'Utah', 'Wyoming', 'Idaho', 'Washington', 'Oregon', 'Montana', 'Alaska', 'Hawaii']

urlData = requests.get(url).content
rawData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
rawData = rawData[rawData['state'].isin(listofsatates)]
rawData['date'] = rawData['date'].astype('datetime64[ns]')
preftc = rawData[['fips', 'county']].drop_duplicates()
ftc = dict(preftc[['fips', 'county']].values)
prefts = rawData[['fips', 'state']].drop_duplicates('fips')
fts = dict(prefts[['fips', 'state']].values)

 
date_Nplus1_days_ago = rawData['date'].max() - datetime.timedelta(days=7)
curData = rawData[rawData['date'] >= date_Nplus1_days_ago]
datacases = []
columns = ['fips']
columns.extend(sorted(set(curData['date']))[1:])
columns.extend(['total 7d'])


for i in set(curData['fips']) :
  tempData = curData[curData['fips'] == i]
  tempData = tempData.sort_values(by ='date')
  templist = [i]
  butlist =  tempData['cases'].tolist()
  t = 0
  try : 
    for z in butlist[1:] :
      marg = z - butlist[t]
      if marg <= 0 :
        marg = 0 
      marg = marg / dictpop[i] * 100000
      templist.extend([marg])
      t += 1
    totaldif = butlist[-1] - butlist[0] 
    if totaldif <= 0 :
      totaldif = 0 
    totaldif = totaldif / dictpop[i] * 100000
    templist.extend([totaldif])
    datacases.append(templist)
  except : 
    continue
tabstate = pd.DataFrame(datacases, columns=columns)
tabstatefig = tabstate[columns[0:-2]]
tabstatefig = tabstatefig.melt(id_vars=["fips"], 
        var_name="Date", 
        value_name="Value")
tabstate = tabstate.sort_values(by ='total 7d', ascending=False)
listworstcounties = tabstate['fips'].to_list()[0:10]
tabstatefig = tabstatefig[tabstatefig['fips'].isin(listworstcounties)]
tabstatefig['county'] = tabstatefig['fips'].map(ftc)
tabstatefig['state'] = tabstatefig['fips'].map(fts)
tabstate['state'] = tabstate['fips'].map(fts)


fig3 = px.area(tabstatefig, x=tabstatefig['Date'], y =tabstatefig['Value'],  facet_col="county", facet_col_wrap=2, color=tabstatefig['state'])
fig3.show()
listofsatatesforthemap = ['Nevada', 'California', 'Utah', 'Wyoming', 'Idaho', 'Washington', 'Oregon', 'Montana']
tabstateforthemap = tabstate[tabstate['state'].isin(listofsatatesforthemap)]

values = tabstateforthemap['total 7d'].tolist()
fips = tabstateforthemap['fips'].tolist()
endpts = list(np.mgrid[min(values):max(values):4j])
colorscale = ['#ffffe0','#ffe9d8','#ffd3cf','#e1a0a2', '#a65051', '#6b0000']
fig4 = ff.create_choropleth(
      fips=fips, values=(values),
  binning_endpoints=endpts, round_legend_values=True,
      colorscale=colorscale, scope=listofsatatesforthemap, county_outline={'color': 'rgb(128,128,128)', 'width': 0.1},
      state_outline={'color': 'rgb(0,0,0)', 'width': 0.2},
      legend_title='Nouveaux cas pour 100K habitants le {}'.format(joe))
fig4.show()


poleveentsdata = pd.read_csv('https://raw.githubusercontent.com/OxCGRT/USA-covid-policy/master/data/OxCGRT_US_latest.csv')
poleveentsdata = poleveentsdata[poleveentsdata['RegionName'].isin(listofsatates)]
poleveentsdata['Date'] = pd.to_datetime(poleveentsdata['Date'], format='%Y%m%d')
date_N_days_ago = datetime.datetime.now() - datetime.timedelta(days=10)
poleveentsdata = poleveentsdata[poleveentsdata['Date'] >= date_N_days_ago]
poleveentsdata = poleveentsdata[['RegionName', 'Date', 'C1_Notes', 'C2_Notes', 'C3_Notes', 'C4_Notes' ,'C5_Notes' ,'C6_Notes' ,
                                 'C7_Notes' ,'C8_Notes', 'E1_Notes',  'E2_Notes', 'E3_Notes', 'E4_Notes', 'H1_Notes' , 'H2_Notes' , 'H3_Notes' , 'H4_Notes' , 'H5_Notes', 'M1_Notes']]
poleveentsdata = poleveentsdata.dropna(thresh=3) 
text = """Gouvernement"""

for i in set(poleveentsdata['RegionName']) : 
  text = text + """\n \n""" + str(i)
  tempData = poleveentsdata[poleveentsdata['RegionName'] == i]
  tempData.index = tempData['Date'].dt.strftime('%Y-%m-%d')
  for z in tempData.index : 
    temptext = """"""
    temptext = temptext + """\n""" + z
    check = 0
    for k in ['C1_Notes', 'C2_Notes', 'C3_Notes', 'C4_Notes' ,'C5_Notes' ,'C6_Notes' , 'C7_Notes' ,'C8_Notes', 'E1_Notes',  'E2_Notes', 'E3_Notes', 'E4_Notes', 'H1_Notes' , 'H2_Notes' , 'H3_Notes' , 'H4_Notes' , 'H5_Notes', 'M1_Notes'] : 
      robert = tempData.loc[z, k]
      if isinstance(robert, float)  : 
        continue
      else :
        temptext = temptext + """\n""" + str(robert)
      text = text + """\n \n      """ + temptext
    
    


govtwitstat = {
    'Guam' : 'louleonguerrero',
    'Nevada' : 'GovSisolak', 
    'California' : 'GavinNewsom', 
    'Utah' : 'GovHerbert', 
    'Wyoming' : 'GovernorGordon', 
    'Idaho' : 'GovernorLittle', 
    'Washington' : 'GovInslee', 
    'Oregon' : 'OregonGovBrown', 
    'Montana': 'governorbullock', 
    'Alaska' : 'GovDunleavy', 
    'Hawaii' : 'GovHawaii'

}
datetwit = date_Nplus1_days_ago.date()
text2 = ''
for i in govtwitstat.keys() :
  text2 = text2 + str(i) + '\n'
  search = API.search(f'virus OR pandemic OR COVID OR reopening OR disease OR COVID19 from:{govtwitstat[i]}')
  json.dumps(search)
  for z in range(0, len(search['statuses'])) : 
    text2 = text2 + search['statuses'][z]['text']
  text2 = text2 + '\n \n \n'



text3 = "LA Times \n \n \n"
keywords = ['virus', 'pandemic', 'COVID', 'reopening', 'disease', 'COVID19', 'coronavirus']
NewsFeedLATimes = feedparser.parse("https://www.latimes.com/california/rss2.0.xml#nt=1col-7030col1")
for i in range(0, len(NewsFeedLATimes.entries)) : 
  entry = NewsFeedLATimes.entries[i]
  date = datetime.datetime(entry['published_parsed'].tm_year, entry['published_parsed'].tm_mon, entry['published_parsed'].tm_mday)
  article = entry['title'] + '\n' + entry['summary'] 
  if date >= date_N_days_ago and any(a in article for a in keywords):
    text3 += entry['published'] + '\n' +  article + '\n \n \n \n \n'


print(text3)

text4 = "Seattle Times \n \n \n"
keywords = ['virus', 'pandemic', 'COVID', 'reopening', 'disease', 'COVID19', 'coronavirus']
NewsFeedLATimes = feedparser.parse("https://www.seattletimes.com/northwest/feed/")
for i in range(0, len(NewsFeedLATimes.entries)) : 
  entry = NewsFeedLATimes.entries[i]
  date = datetime.datetime(entry['published_parsed'].tm_year, entry['published_parsed'].tm_mon, entry['published_parsed'].tm_mday)
  article = entry['title'] + '\n' + entry['summary'] 
  if date >= date_N_days_ago and any(a in article for a in keywords):
    text4 += entry['published'] + '\n' +  article + '\n \n \n \n \n'


print(text4)

fig.write_image('/'+joe1+'/statebstateoverweek.pdf')
fig2.write_image('/'+joe1+'/statebstateoverlastday.pdf')
fig3.write_image('/'+joe1+'/countybcountyoverweek.pdf')
fig4.write_image('/'+joe1+'/countybcountyoverlastday.pdf')
print(text + '\n \n \n tw' + text2)
text_file = open('/'+joe1+'actualités.txt', "w") 
text_file.write(text + '\n \n \n \n \n twitter \n \n \n' + text2 + '\n \n \n \n \n Journaux \n \n \n' + text3 + '\n \n \n' + text4) 
text_file.close()
