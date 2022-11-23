from concurrent.futures import ThreadPoolExecutor
import logging
import string
import openai
import random
import re
import httpx
import json
import urllib
from pprint import pprint
from fake_useragent import UserAgent
import cv2
import pafy

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    value = re.sub(r"[-\s]+", "-", value)
    return value

def split(a, n):
    """
    Split a list into n chunks
    example:
    >>> list(split(range(11), 3))
    [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10]]    
    """
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def call_api(*params):
    """
    Call the API with the given arguments
    'frequency_penalty':0,
    'presence_penalty':0,
    'best_of':1,
    'n':1,
    'echo':False,
    'stream':False,
    "model": "text-davinci-002",
    "temperature": 0.7,
    "max_tokens": 164,
    "top_p":1,
    'prompt':'',    
    """
    response = openai.Completion.create(**params[0])
    return response

def get_simple_list(prompt):
    params = {
        'model': "text-davinci-002",
        'temperature': random.randint(4,8)/10,
        'echo': False,
        'prompt' : prompt,
        'max_tokens': 2048,
        'top_p': 1,
        'frequency_penalty': 0.4,
        'presence_penalty': 0.4,
        'best_of': 1,
        'n': 1,
        'stream': False,
    }
    r = call_api(params)
    l = r['choices'][0]['text'].strip().split('\n')
    l = [re.sub(r'^[^A-Z]+', r'', x) for x in l]
    l = [x for x in l if x]

    return l

def get_simple_text(prompt):
    params = {
        'model': "text-davinci-002",
        'temperature': random.randint(4,8)/10,
        'echo': False,
        'prompt' : prompt,
        'max_tokens': 2048,
        'top_p': 1,
        'frequency_penalty': 1.5,
        'presence_penalty': 1.5,
        'best_of': 1,
        'n': 1,
        'stream': False,
    }
    r = call_api(params)
    return r['choices'][0]['text'].strip()

def gen_content(record_id,input_topic,input_outline,input_keywords):
    titles = input_outline
    md_text=""
    text=""
    try:
        md_text+=f"# {input_topic}\n"
        text+=f"{input_topic}\n"
        
        # Si pas de outlines, ils son générés par GPT-3
        if len(input_outline) == 0:
            prompt=f'Ecris, en français, une liste de titre d\'un texte dont le sujet principal est "{input_topic}":\n-'
            titles = get_simple_list(prompt)

        
        
        for i,title in enumerate(titles):
            prompt=f'Dans un article dont le titre "{input_topic}" écris, en français, le paragraphe dont le titre est "{title}":\n'
            if len(input_keywords[i])>0:
                prompt=f'Dans un article dont le titre "{input_topic}" écris, en français, le paragraphe dont le titre est "{title}" en utilisant les mots-clés "{input_keywords[i]}".\n'

            logging.info("prompt : "+prompt)
            content = get_simple_text(prompt)
            md_text+=f"## {title}\n"
            text+=f"{title}\n"
            md_text+=f"{content}\n"
            text+=f"{content}\n"
            prompt=f'Développe le texte suivant, en evitant les répétitions, dont le sujet principal est "{input_topic}" et qui traite spéciquement de "{title}":\n{content}'
            # prompt=f'{content}\nDéveloppe le texte précédent, en evitant les répétitions:\n'
            logging.info("prompt : "+prompt)
            extended_content = get_simple_text(prompt)
            md_text+=f"{extended_content}\n\n"
            text+=f"{extended_content}\n\n"
    except Exception as e:
        logging.error(f"Error {input_topic}")
        logging.error(e)

    return record_id,md_text,text



def get_unsplash(kw):
    parsekw = urllib.parse.quote(kw)
    image_url = "https://source.unsplash.com/random"
    key = "4t8Dm6fQdVm8g2vBHslSs88GclceZMte9p3TnSatAy8"
    # Query unsplash api for images from the keyword parsekw
    url = f"https://api.unsplash.com/search/photos?page=1&query={parsekw}&client_id={key}&content_filter=high&orientation=landscape"
    r = httpx.get(url)
    txt_data = r.text
    data = json.loads(txt_data)
    image_urls=[]
    if data['total'] >= 3:
        image_urls.append(data['results'][0]['urls']['regular'])
        image_urls.append(data['results'][1]['urls']['regular'])
        image_urls.append(data['results'][2]['urls']['regular'])

    return image_urls


def words_count(text):
    res = sum([i.strip(string.punctuation).isalpha() for i in text.split()])
    return res

def get_youtube_videos(keyword):
    url = f"https://www.youtube.com/results?search_query={keyword}"
    ua = UserAgent()
    user_agent = ua.chrome
    headers = {'User-Agent': user_agent}
    keyword = urllib.parse.quote_plus(keyword)
    resp = httpx.get(url, timeout=60, headers=headers)
    doc = resp.text
    x = re.findall('\"url\":\"(\/watch\?v=.*?)\"', doc)
    x = [i for i in x if "t=" not in i]
    # remove duplicates from x
    x = list(dict.fromkeys(x))
    youtube_urls = [f"https://www.youtube.com{i}" for i in x]
    return youtube_urls


def get_image_from_youtube(youtube_url,num_images=3,image_prefix="yt_",image_extension="png"):
    video = pafy.new(youtube_url)
    best  = video.getbest()
    capture = cv2.VideoCapture(best.url)
    length = int(capture.get(cv2. CAP_PROP_FRAME_COUNT))
    img_positions = []
    file_name=""
    for i in range(num_images):
        v0 = int(length / num_images * i)
        v1 = int(length / num_images * (i+1))
        r = random.randint(v0,v1)
        img_positions.append(r)

    for img_position in img_positions:
        capture.set(cv2.CAP_PROP_POS_FRAMES, img_position)
        ret, frame = capture.read()
        if ret:
            file_name = f"{image_prefix}{img_position}.{image_extension}"
            cv2.imwrite(file_name, frame)
            print(f"{file_name} OK")
        else:
            print("error")
            break

    capture.release()
    return file_name