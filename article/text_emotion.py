import operator
import time
from mutagen.flac import FLAC
from article.API_config import *
import os
import re
from zhon.hanzi import punctuation
import mutagen


def video2audio(audio_file_path):
    audio_dir_path = os.path.dirname(audio_file_path)
    wav_file_path = os.path.join(
        audio_dir_path, os.path.splitext(audio_file_path)[0] + ".wav")
    flac_file_path = os.path.join(
        audio_dir_path, os.path.splitext(audio_file_path)[0] + ".flac")
    os.system(f'ffmpeg -i \"{audio_file_path}\"  -preset ultrafast \"{wav_file_path}\"')
    os.system(f'ffmpeg -i \"{wav_file_path}\"  -preset ultrafast \"{flac_file_path}\"')
    print(Rf"{audio_file_path} to {flac_file_path}")
    return flac_file_path


def transcribe_file(speech_file, frame_rate, channels):
    """Transcribe the given audio file."""
    from google.cloud import speech
    import io
    from requests import post

    client = speech.SpeechClient()

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    # audio = speech.RecognitionAudio(uri=gcs_uri)
    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=frame_rate,
        enable_automatic_punctuation=True,
        audio_channel_count=channels,
        language_code="zh-TW",
        enable_word_time_offsets=True,
    )
    time_start = time.time()
    audio_info = mutagen.File(speech_file).info.length

    print("start recognize...............")
    # 一分鐘內
    # response = client.recognize(config=config, audio=audio)
    full_text = ''

    # 超過一分鐘
    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result()
    # print(response)
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        full_text += result.alternatives[0].transcript

    text = re.sub("[%s]+" % punctuation, "", full_text)
    # print(text)
    # 冗詞
    redundant_1 = '就是'
    redundant_2 = '那個'
    redundant_3 = '然後'
    redundant_4 = '所以'
    redundant_1_count = text.count(redundant_1)
    redundant_2_count = text.count(redundant_2)
    redundant_3_count = text.count(redundant_3)
    redundant_4_count = text.count(redundant_4)

    payload_sense2 = {
        "username": username,
        "keymoji_key": keymoji_key,
        "input_str": full_text,
        "sense": "sense2",
        "context_sensitivity": True
    }
    payload_sense8 = {
        "username": username,
        "keymoji_key": keymoji_key,
        "input_str": full_text,
        "sense": "sense8",
        "context_sensitivity": True
    }

    response_s8 = post(url, json=payload_sense8)
    response_s2 = post(url, json=payload_sense2)

    # to json
    data_s8 = response_s8.json()
    data_s2 = response_s2.json()
    data = []

    result_s2 = {}
    suggest = []
    negative_count = 0
    positive_count = 0
    neutral_count = 0

    for i in data_s2['results']:
        result_s2[i['input_str']] = i['sentiment']
        if i['sentiment'] == 'neutral':
            neutral_count += 1
        elif i['sentiment'] == 'negative':
            negative_count += 1
        elif i['sentiment'] == 'positive':
            positive_count += 1

    max_sentence_count = max(neutral_count, negative_count, positive_count)

    if max_sentence_count == neutral_count:
        suggest.append(
            'In the part of sentence meaning analysis, the most frequently occurring phrase is a neutral one. In '
            'total, there were ' + str(neutral_count) + ' times. It is recommended to add more positive words, '
                                                        'such as introducing your strengths and advantages, '
                                                        'which may impress the interviewer more!!')
    elif max_sentence_count == negative_count:
        suggest.append(
            'In the part of sentence meaning analysis, the most frequently occurring phrase is a negative one. In '
            'total, there were ' + str(negative_count) + ' times. It is recommended to reduce the use of negative '
                                                         'words and add some positive words, the overall score of the'
                                                         ' article will also increase!')
    elif max_sentence_count == positive_count:
        suggest.append('In the part of sentence meaning analysis, the most frequently occurring phrase is a positive '
                       'one. In total, there were' + str(positive_count) + ' times. Very Good! Please keep it up!')

    for i, j in zip(data_s8['results'], data_s2['results']):
        if i['input_str'] == j['input_str']:
            i.update({'sentiment': j['sentiment']})
            data.append(i)

    speed = round(len(full_text) / audio_info * 60, 3)

    if speed > 220:
        suggest.append('In the speed section, the speed of this test is ' + str(
            speed) + ' words/min, the normal speed of speech is about 160-200 words/min. It is a little too fast to '
                     'speak. It is recommended to slow down the speed of speech to make the words more clear, '
                     'too fast speed of speech will easily make the interviewer feel that the interviewer is '
                     'impatient.')
    elif 220 >= speed >= 160:
        suggest.append('In the speed section, the speed of this test is ' + str(
            speed) + ' words/min, the normal speed of speech is about 160-200 words/min. Moderate language speed! Very '
                     'Good! The right speed of speech allows the interviewer to focus and deliver the content '
                     'effectively.')
    elif speed < 160:
        suggest.append('In the speed section, the speed of this test is ' + str(
            speed) + ' words/min, the normal speed of speech is about 160-200 ' \
                     'words/min. Need to speak faster! Suggest to speak faster, More content in a limited amount of '
                     'time will also help the interviewer to understand you better! If you speak too slowly, '
                     'the interviewer will feel uninformed and will have a negative impression that the interviewer '
                     'is slow to respond.')

        # 計分
    joy_sum = 0
    trust_sum = 0
    surprise_sum = 0
    anticipation_sum = 0
    fear_sum = 0
    sadness_sum = 0
    anger_sum = 0
    disgust_sum = 0
    sentence_count = 0
    joy_coefficient = -15.46565737
    trust_coefficient = -10.42994652
    surprise_coefficient = 20.90687248
    anticipation_coefficient = 14.47577979
    fear_coefficient = -11.37868111
    sadness_coefficient = -1.635467311
    anger_coefficient = -5.636488605
    disgust_coefficient = 5.679913021
    constant = 57.5184
    for i in data_s8['results']:
        if i['Joy'] == 0 and i['Trust'] == 0 and i['Surprise'] == 0 and i['Anticipation'] == 0:
            continue
        else:
            sentence_count += 1
            joy_sum += i['Joy']
            trust_sum += i['Trust']
            surprise_sum += i['Surprise']
            anticipation_sum += i['Anticipation']
            fear_sum += i['Fear']
            sadness_sum += i['Sadness']
            anger_sum += i['Anger']
            disgust_sum += i['Disgust']
    score = joy_sum / sentence_count * joy_coefficient + trust_sum / sentence_count * trust_coefficient + surprise_sum / sentence_count * surprise_coefficient + anticipation_sum / sentence_count * anticipation_coefficient + fear_sum / sentence_count * fear_coefficient + sadness_sum / sentence_count * sadness_coefficient + anger_sum / sentence_count * anger_coefficient + disgust_sum / sentence_count * disgust_coefficient + constant

    rank = ''
    if 0 <= score <= 20:
        rank = 'D'
    elif 20 < score <= 40:
        rank = 'C'
    elif 40 < score <= 60:
        rank = 'B'
    elif 60 < score <= 80:
        rank = 'A'
    elif 80 < score:
        rank = 'S'

    # s8各項分數
    s8_list = {'joy': joy_sum / sentence_count, 'trust': trust_sum / sentence_count,
               'surprise': surprise_sum / sentence_count, 'anticipation': anticipation_sum / sentence_count,
               'fear': fear_sum / sentence_count, 'sadness': sadness_sum / sentence_count,
               'anger': anger_sum / sentence_count, 'disgust': disgust_sum / sentence_count
               }

    # 中文對照
    s8_chinese = {
        'joy': '歡樂', 'trust': '信任', 'surprise': '驚喜', 'anticipation': '期待', 'fear': '恐懼',
        'sadness': '悲傷', 'anger': '憤怒', 'disgust': '厭惡'
    }
    # 高於一個標準差
    higher_score = {
        'joy': 4.769441602, 'trust': 4.472139509, 'surprise': 4.47709133, 'anticipation': 4.413322929,
        'fear': 2.855518644,
        'sadness': 3.126179733, 'anger': 2.445219902, 'disgust': 2.852926154
    }
    # 低於一個標準差
    lower_score = {
        'joy': 1.443758904, 'trust': 1.693142064, 'surprise': 1.427063164, 'anticipation': 1.328544081,
        'fear': 0.6921923285,
        'sadness': 0.7754272165, 'anger': 0.6353545837, 'disgust': 0.954607237
    }

    higher_pos_list = []
    higher_neg_list = []
    lower_pos_list = []
    lower_neg_list = []

    index = 0
    for emoji in s8_list:
        if s8_list[emoji] > higher_score[emoji] and index < 4:
            higher_pos_list.append(emoji)
        elif s8_list[emoji] < lower_score[emoji] and index < 4:
            lower_pos_list.append(emoji)
        elif s8_list[emoji] > higher_score[emoji] and index >= 4:
            higher_neg_list.append(emoji)
        elif s8_list[emoji] < lower_score[emoji] and index >= 4:
            lower_neg_list.append(emoji)
        index += 1

    if len(higher_pos_list):
        emotion_str = ''
        flag = 1
        for element in higher_pos_list:
            if flag:
                emotion_str += s8_chinese[element] + '、'
                flag += 1
                flag = 0 if len(higher_pos_list) == flag else flag
            else:
                emotion_str += s8_chinese[element]
        suggest.append(
            'In the section on sentiment analysis, in the article, The scores of positive emotions such as the '
            'following performed well, ' + emotion_str + '. Please keep it up.')
    if len(lower_pos_list):
        emotion_str = ''
        flag = 1
        for element in lower_pos_list:
            if flag:
                emotion_str += s8_chinese[element] + '、'
                flag += 1
                flag = 0 if len(lower_pos_list) == flag else flag
            else:
                emotion_str += s8_chinese[element]
        suggest.append(
            'In the section on sentiment analysis, in the article, The scores of positive emotions such as the '
            'following are on the low side, ' + emotion_str + ', Appropriate positive statements can generate '
                                                              'positive comments from the interviewer, Suggest more '
                                                              'positive words in the article. Such as hope, '
                                                              'expertise, motivation, competence.')

    if len(higher_neg_list):
        emotion_str = ''
        flag = 1
        for element in higher_neg_list:
            if flag:
                emotion_str += s8_chinese[element] + '、'
                flag += 1
                flag = 0 if len(higher_neg_list) == flag else flag
            else:
                emotion_str += s8_chinese[element]
        suggest.append(
            'In the section on sentiment analysis, in the article, The scores of negative emotions such as the '
            'following are on the low side,' + emotion_str + '. Too much negativity in the essay may give a negative '
                                                             'impression to the interviewer. It is recommended to '
                                                             'adjust the wording and reduce the negative wording.')

    time_end = time.time()
    time_c = time_end - time_start  # 執行所花時間
    print('total spent time', time_c, 's')

    suggest_dict = {}
    d_index = 0
    for i in suggest:
        suggest_dict[d_index] = i
        d_index += 1

    final_result = {'全文': full_text,
                    '文章長度': len(full_text),
                    '文章長度(不含標點符號)': len(text),
                    '就是次數': redundant_1_count,
                    '那個次數': redundant_2_count,
                    '然後次數': redundant_3_count,
                    '所以次數': redundant_4_count,
                    'joy': joy_sum / sentence_count,
                    'trust': trust_sum / sentence_count,
                    'surprise': surprise_sum / sentence_count,
                    'anticipation': anticipation_sum / sentence_count,
                    'fear': fear_sum / sentence_count,
                    'sadness': sadness_sum / sentence_count,
                    'anger': anger_sum / sentence_count,
                    'disgust': joy_sum / sentence_count,
                    'total_score': score,
                    'rank': rank,
                    'talk_speed': speed,
                    'suggest_json': suggest_dict,
                    'detail': result_s2
                    }
    # print(final_result)
    return final_result


def frame_rate_channel(audio_file_name):
    frame_rate = FLAC(audio_file_name).info.sample_rate
    channels = FLAC(audio_file_name).info.channels
    return frame_rate, channels
