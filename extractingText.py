import json
import glob
import re
import emoji
import demoji
import numpy as np
import time
import urllib.request, os

start = time.time()

# check for the images folder
def check_folder_exists(folder_name):
  if not os.path.isdir(folder_name):
    os.makedirs(folder_name)

# extracting emojis
def extract_emojis(s):
    all_emojis = ''.join(c for c in s if c in emoji.distinct_emoji_list(s))
    emojis_meaning = demoji.findall(all_emojis)

    return emojis_meaning

# extracting images
def extract_images(url, file_name):
    try:
        folder_name = str('/home/shakir/Documents/R-Sir/sentimental-analysis-on-twitter-data/images')
        check_folder_exists(folder_name)
        file_name = file_name + '.jpg'
        full_filename = os.path.join(folder_name, file_name)
        urllib.request.urlretrieve(url, full_filename)
    except BaseException as err:
        print(err)
        return False


all_texts = []
all_emojis = []


files = glob.glob('/home/shakir/Desktop/tweets/tweet/*.json', recursive=True)

# print(type(files))
print('Collecting data...')
i = 0
while i < len(files):
    with open(files[i], 'r') as f:
        json_file1 = json.load(f)
        user_emojis = []
        user_texts = []

        if json_file1['lang'] == 'en':
            data_object = {
                'tweet_id': json_file1['id'],
                'text': re.sub(r"[^a-zA-Z0-9.' ]", "", re.sub(r"http\S+", "", json_file1['text']).replace('/', '').strip()),
                'user_id': json_file1['user']['id'],
                'followers_count': json_file1['user']['followers_count'],
                'friends_count': json_file1['user']['friends_count']
            }
            # print(data_object['text'])
            # extracting images
            if 'media' in json_file1['entities']:
                k = 0
                images_array = []
                for media in json_file1['entities']['media']:
                    is_image_downloaded = extract_images(
                        media['media_url_https'], media['id_str'])
                    if is_image_downloaded:
                        images_array.append(media['id'])
                        k += 1
                if len(images_array) > 0:
                    data_object['tweet_images'] = images_array

            # extracting emojis
            result = extract_emojis(json_file1['text'])
            if len(result) > 0:
                # print(result)
                emojis_object = {
                    'tweet_id': json_file1['id'],
                    'user_id': json_file1['user']['id'],
                    'tweet_emojis': result,
                }
                user_emojis.append(emojis_object)

            user_texts.append(data_object)
            j = i + 1
            while j < len(files):
                with open(files[j], 'r') as f2:
                    json_file2 = json.load(f2)
                    if json_file1['user']['id'] == json_file2['user']['id']:
                        result = ''
                        result = extract_emojis(json_file2['text'])
                        data_object = {
                            'tweet_id': json_file2['id'],
                            'text': re.sub(r"[^a-zA-Z0-9-. ]", "", re.sub(r"http\S+", "", json_file2['text']).replace('/', '').strip()),
                            'user_id': json_file2['user']['id'],
                            'followers_count': json_file2['user']['followers_count'],
                            'friends_count': json_file2['user']['friends_count']
                        }

                        # extracting images
                        if 'media' in json_file2['entities']:
                            k = 0
                            images_array = []
                            for media in json_file2['entities']['media']:
                                is_image_downloaded = extract_images(
                                    media['media_url_https'], media['id_str'])
                                if is_image_downloaded:
                                    images_array.append(media['id'])
                                    k += 1
                            if len(images_array) > 0:
                                data_object['tweet_images'] = images_array

                        # extracting emojis
                        if len(result) > 0:
                            emojis_object = {
                                'tweet_id': json_file2['id'],
                                'user_id': json_file2['user']['id'],
                                'tweet_emojis': result,
                            }
                            user_emojis.append(emojis_object)
                        user_texts.append(data_object)
                        del files[j]
                    else:
                        j += 1

            all_texts.append(user_texts)
            if len(user_emojis) > 0:
                all_emojis.append(user_emojis)
                # print("emojis:==========", all_emojis)
            # print(all_texts)
        else:
            del files[i]
        i += 1


with open('users_texts.json', 'w') as outfile:
    json.dump(all_texts, outfile)

with open('user_emoji_list.json', 'w') as outfile:
    json.dump(all_emojis, outfile)


print(time.time()-start)
