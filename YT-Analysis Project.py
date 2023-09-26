#!/usr/bin/env python
# coding: utf-8

# In[5]:


from googleapiclient.discovery import build
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


# In[6]:


api_key = 'AIzaSyCQzbUya4BezbYlnymep7o9XxdLX_Q65R4'
#channel_id = 'UCOMRVYY863s0skWdKVmF4wQ' # my channel
channel_ids = ['UC7MGCyKDw8iQX7Vs0-BH9uA', #relab
               'UCjjsDJeZ0Kg7MhhiMmSUInw', #tuanngocday
               'UCvJ8leyn7YWgqmbmw1R5ZVg', #duongde
               'UCQ0jSGgYMLmRMeTE6UaPPXg', #duyluandethuong
               'UCOygiQNXiiQ_rpRjHU5ri-A' #duytham
            ]

youtube = build('youtube','v3', developerKey=api_key)


# ## Function to get channel statistics

# In[ ]:


# #my channel
# def get_channel_stats(youtube, channel_ids):
    
#     request = youtube.channels().list(
#                 part = 'snippet,contentDetails,statistics',
#                 id=channel_id)
    
#     response = request.execute()
    
#     data = dict(Channel_name = response['items'][0]['snippet']['title'],
#                 Subscribers = response['items'][0]['statistics']['subscriberCount'],
#                 Views = response['items'][0]['statistics']['viewCount'],
#                 Total_videos = response['items'][0]['statistics']['videoCount']
#                )
    
#     return data


# In[7]:


# use for port

def get_channel_stats(youtube, channel_ids):
    all_data = []
    
    request = youtube.channels().list(
                part = 'snippet,contentDetails,statistics',
                id=','.join(channel_ids))
    
    response = request.execute()
    
    for i in range(len(response['items'])):
        data = dict(Channel_name = response['items'][i]['snippet']['title'],
                    Subscribers = response['items'][i]['statistics']['subscriberCount'],
                    Views = response['items'][i]['statistics']['viewCount'],
                    Total_videos = response['items'][i]['statistics']['videoCount'],
                    playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads']
                   )
        
        all_data.append(data)
    
    return all_data


# In[8]:


channel_statistics = get_channel_stats(youtube, channel_ids)


# In[9]:


channel_data = pd.DataFrame(channel_statistics)


# In[10]:


channel_data


# In[11]:


channel_data.info()


# In[12]:


channel_data.dtypes


# In[13]:


channel_data['Subscribers'] = pd.to_numeric(channel_data['Subscribers'])
channel_data['Views'] = pd.to_numeric(channel_data['Views'])
channel_data['Total_videos'] = pd.to_numeric(channel_data['Total_videos'])
channel_data.dtypes


# In[14]:


import matplotlib.ticker as mtick  # Thêm thư viện này


# In[15]:


df_channel_total = channel_data.groupby(['Channel_name']).sum()
df_channel_total


# In[16]:


sns.set(rc={'figure.figsize':(8,6)})
ax = sns.barplot(x='Channel_name', y='Subscribers', data=channel_data)
# Định dạng số không viết tắt trên trục y
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: format(int(x), ',')))

# Thêm data label và định dạng số
for p in ax.patches:
    height = p.get_height()
    ax.text(p.get_x() + p.get_width() / 2, height + 10000, format(int(height), ','), ha='center')


# In[17]:


ax = sns.barplot(x='Channel_name', y='Views', data=channel_data)
# Định dạng số không viết tắt trên trục y
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: format(int(x), ',')))

# Thêm data label và định dạng số
for p in ax.patches:
    height = p.get_height()
    ax.text(p.get_x() + p.get_width() / 2, height + 10000, format(int(height), ','), ha='center')


# In[18]:


ax = sns.barplot(x='Channel_name', y='Total_videos', data=channel_data)
# Định dạng số không viết tắt trên trục y
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: format(int(x), ',')))

# Thêm data label và định dạng số
for p in ax.patches:
    height = p.get_height()
    ax.text(p.get_x() + p.get_width() / 2, height + 150, format(int(height), ','), ha='center')


# ## Function to get video ids

# In[19]:


channel_data


# In[20]:


playlist_id = channel_data.loc[channel_data['Channel_name'] == 'ReLab', 'playlist_id'].iloc[0]


# In[21]:


playlist_id


# In[22]:


def get_video_ids(youtube, playlist_id):
    request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId = playlist_id,
                maxResults = 50 #because 50 is the maximum value you can pass
                )
    
    response = request.execute()
    
    video_ids = []
    
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
        
    next_page_token = response.get('nextPageToken')
    more_pages = True
    
    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                        part='contentDetails',
                        playlistId = playlist_id,
                        maxResults = 50,
                        pageToken = next_page_token
                        )
            response = request.execute()
            
            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
                
            next_page_token = response.get('nextPageToken')
    
    return video_ids


# In[23]:


video_ids = get_video_ids(youtube, playlist_id)


# In[24]:


video_ids


# ## function to get video details

# In[25]:


import datetime

def get_video_details(youtube, video_ids):
    all_video_stats = []
    
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
                    part='snippet,statistics',
                    id=','.join(video_ids[i:i+50])
                )
        response = request.execute()
        
        for video in response['items']:
            
            # Lấy ngày hiện tại
            current_date = datetime.datetime.now().isoformat()
            
            video_stats = dict(Title = video['snippet']['title'],
                               Published_date = video['snippet']['publishedAt'],
                               Current_date=current_date,  # Thêm ngày hiện tại
                               Views = video['statistics']['viewCount'],
                               Likes = video['statistics']['likeCount'],
                               #Dislikes = video['statistics']['dislikeCount'], #json ko trả ra dislike
                               #Comments = video['statistics']['commentCount']
                              )
            
            all_video_stats.append(video_stats)
            
    return all_video_stats


# In[26]:


video_details = get_video_details(youtube, video_ids)


# In[27]:


video_data = pd.DataFrame(video_details)


# In[28]:


video_data


# In[29]:


# modified date value
video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
#video_data['Comments'] = pd.to_numeric(video_data['Comments'])
video_data.dtypes


# In[30]:


video_data


# In[31]:


top10_videos_views = video_data.sort_values(by='Views', ascending=False).head(10)


# In[32]:


top10_videos_views


# In[33]:


ax1 = sns.barplot(x='Views', y='Title', data= top10_videos_views)
# Định dạng số không viết tắt trên trục x
def format_xaxis(value, tick_number):
    if value >= 1e6:
        return f'{value/1e6:.1f}M'
    elif value >= 1e3:
        return f'{value/1e3:.1f}K'
    else:
        return str(int(value))

ax1.xaxis.set_major_formatter(mtick.FuncFormatter(format_xaxis))

# Thêm data label và định dạng số
for p in ax1.patches:
    width = p.get_width()
    ax1.text(width, p.get_y() + p.get_height() / 2, format_xaxis(width, None), ha='left', va='center')

plt.show()


# In[34]:


# convert thêm cột tên tháng từ cột ngày
video_data['Month_name'] = pd.to_datetime(video_data['Published_date']).dt.strftime('%b')
video_data


# In[35]:


# convert thêm cột tháng năm từ cột ngày
video_data['Month_year'] = pd.to_datetime(video_data['Published_date']).dt.to_period('M')
video_data


# In[36]:


# convert thêm cột năm - year từ cột ngày
video_data['year'] = pd.to_datetime(video_data['Published_date']).dt.to_period('Y').astype(str)
video_data


# In[37]:


video_per_month = video_data.groupby('Month_year', as_index=False).size()
video_per_month


# In[38]:


video_data.dtypes


# In[39]:


video_data['Month_year'] = video_data['Month_year'].astype(str)
video_data['year'] = video_data['year'].astype(str)
video_data.dtypes


# In[71]:


# Total views và Likes theo từng tháng-nam
video_per_month_year = video_data[['Month_year', 'Views', 'Likes']]
video_per_month_total = video_per_month_year.groupby(['Month_year']).sum().reset_index()
video_per_month_total


# In[41]:


# Total views và Likes theo từng tháng
video_per_month_name = video_data[['Month_name', 'Views', 'Likes']]
video_per_month_name_total = video_per_month_name.groupby(['Month_name']).sum().reset_index()
video_per_month_name_total


# In[42]:


video_data


# In[43]:


# Total views và Likes theo từng năm
video_per_year = video_data[['year', 'Views', 'Likes']]
video_per_year_total = video_per_year.groupby(['year']).sum().reset_index()
video_per_year_total


# In[44]:


video_per_month_name = video_data.groupby('Month_name', as_index=False).size()
video_per_month_name


# In[45]:


sort_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


# In[46]:


video_per_month_name_total.index=pd.CategoricalIndex(video_per_month_name_total['Month_name'], categories=sort_order, ordered=True)


# In[47]:


video_per_month_name_total = video_per_month_name_total.sort_index()


# In[48]:


ax2 = sns.barplot(x='Month_name', y='Views', data=video_per_month_name_total)
# Định dạng số không viết tắt trên trục y
ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: format(int(x), ',')))

# Thêm data label và định dạng số
for p in ax2.patches:
    height = p.get_height()
    ax2.text(p.get_x() + p.get_width() / 2, height + 150, format(int(height), ','), ha='center')


# In[49]:


video_data


# In[77]:


# Chuyển cột 'Month_year' thành kiểu ngày tháng
video_data['Month_year'] = pd.to_datetime(video_data['Month_year'], format='%Y-%m')


# In[78]:


video_per_month_year


# In[79]:


# Total views và Likes theo từng tháng-nam
video_per_month = video_data[['Month_year', 'Views', 'Likes']]
video_per_month_year_total = video_per_month.groupby(['Month_year']).sum().reset_index()
video_per_month_year_total


# In[86]:


# biều đồ line chart thể hiện trend theo từng tháng từ năm 2023

# Lọc dữ liệu từ năm 2022 đến hiện tại
start_date = pd.Timestamp('2023-01-01')
filtered_data_2022 = video_per_month_year_total[video_per_month_year_total['Month_year'] >= start_date]

plt.plot(filtered_data_2022['Month_year'], filtered_data_2022['Likes'],linestyle=':', color ='r')

# Định dạng số trên trục y thành "X.XM" (triệu) hoặc "X.XK" (nghìn)
def y_format(x, pos):
    millions = x / 1e6
    thousands = x / 1e3
    if millions >= 1:
        return f'{millions:.1f}M'
    elif thousands >= 1:
        return f'{thousands:.1f}K'
    else:
        return str(int(x))

plt.gca().get_yaxis().set_major_formatter(mtick.FuncFormatter(y_format))

# Định dạng số và thêm data label
for x, y in zip(filtered_data_2022['Month_year'], filtered_data_2022['Likes']):
    plt.text(x, y, y_format(y, None), ha='center', va='bottom')

# Định dạng số trên trục y
plt.gca().get_yaxis().set_major_formatter(mtick.FuncFormatter(y_format))

# Đặt góc xoay cho nhãn trục x
plt.xticks(rotation=45)

plt.show()


# In[64]:


# biểu đồ line chart thể hiện views qua từng năm
plt.plot(video_per_year_total['year'], video_per_year_total['Views'], linestyle=':', color ='b')

# Định dạng số không viết tắt trên trục y
plt.gca().get_yaxis().set_major_formatter(mtick.FuncFormatter(lambda x, p: format(int(x), ',')))

# Định dạng số trên trục y thành "X.XM" (triệu) hoặc "X.XK" (nghìn)
def y_format(x, pos):
    millions = x / 1e6
    thousands = x / 1e3
    if millions >= 1:
        return f'{millions:.1f}M'
    elif thousands >= 1:
        return f'{thousands:.1f}K'
    else:
        return str(int(x))

plt.gca().get_yaxis().set_major_formatter(mtick.FuncFormatter(y_format))

# Thêm data label
# zip là một hàm tích hợp trong Python được sử dụng để ghép nối từng phần tử của nhiều danh sách 
# (hoặc iterable objects) lại với nhau theo cặp. Trong trường hợp này, 
# chúng ta đang sử dụng zip để ghép nối danh sách video_per_year_total['year'] và video_per_year_total['Views'] 
# lại với nhau theo cặp giá trị.

# Định dạng số và thêm data label
for x, y in zip(video_per_year_total['year'], video_per_year_total['Views']):
    plt.text(x, y, y_format(y, None), ha='center', va='bottom')

# Định dạng số trên trục y
plt.gca().get_yaxis().set_major_formatter(mtick.FuncFormatter(y_format))
    
plt.show()


# In[ ]:


video_data.to_csv('Data_video_relab_details')

