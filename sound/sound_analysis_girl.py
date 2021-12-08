import os

import librosa, librosa.display
import numpy as np
import tensorflow.keras as keras
import math
import matplotlib.pyplot as plt

SAMPLE_RATE = 22050
TRACK_DURATION = 15  # measured in seconds
SAMPLES_PER_TRACK = SAMPLE_RATE * TRACK_DURATION

girls_weird_path = os.path.join(os.getcwd(), "sound", "AI_model/girls_weird.h5")
toolonggirlsmodeltry_path = os.path.join(os.getcwd(), "sound", "AI_model/toolonggirlsmodeltry.h5")
isweirdmodel_girl = keras.models.load_model(girls_weird_path)
toolongmodel_girl = keras.models.load_model(toolonggirlsmodeltry_path)


def split_recordings_to_six(signal):
    """
    :param signal:
    :return 切兩刀的聲音
    """
    TRACK_DURATION = 6
    SAMPLE_RATE = 22050
    # measured in seconds
    SAMPLES_PER_TRACK = SAMPLE_RATE * TRACK_DURATION
    num_mfcc = 13
    n_fft = 2048
    hop_length = 512
    num_segments = 5
    samples_per_segment = int(SAMPLES_PER_TRACK / num_segments)
    num_mfcc_vectors_per_segment = math.ceil(samples_per_segment / hop_length)
    start = samples_per_segment
    finish = start + samples_per_segment
    samples_per_segment = int(SAMPLES_PER_TRACK / num_segments)
    num_mfcc_vectors_per_segment = math.ceil(samples_per_segment / hop_length)
    mfcc = librosa.feature.mfcc(signal[start:finish], n_mfcc=num_mfcc, n_fft=n_fft, hop_length=hop_length)
    mfcc = mfcc.T
    x_test = []
    x_test.append(mfcc.tolist())

    start2 = finish
    finish2 = start2 + samples_per_segment
    mfcc2 = librosa.feature.mfcc(signal[start2:finish2], n_mfcc=num_mfcc, n_fft=n_fft, hop_length=hop_length)
    mfcc2 = mfcc2.T
    x2_test = []
    x2_test.append(mfcc2.tolist())

    start3 = finish2
    finish3 = start3 + samples_per_segment
    mfcc3 = librosa.feature.mfcc(signal[start3:finish3], n_mfcc=num_mfcc, n_fft=n_fft, hop_length=hop_length)
    mfcc3 = mfcc3.T
    x3_test = []
    x3_test.append(mfcc3.tolist())

    start4 = finish3
    finish4 = start4 + samples_per_segment
    mfcc4 = librosa.feature.mfcc(signal[start4:finish4], n_mfcc=num_mfcc, n_fft=n_fft, hop_length=hop_length)
    mfcc4 = mfcc4.T
    x4_test = []
    x4_test.append(mfcc4.tolist())

    start5 = finish4
    finish5 = start5 + samples_per_segment
    mfcc5 = librosa.feature.mfcc(signal[start5:finish5], n_mfcc=num_mfcc, n_fft=n_fft, hop_length=hop_length)
    mfcc5 = mfcc5.T
    x5_test = []
    x5_test.append(mfcc5.tolist())

    return x_test, x2_test, x3_test, x4_test, x5_test


def split_recordings(signal):
    """
    :param signal:
    :return 切兩刀的聲音
    """
    SAMPLE_RATE = 22050
    TRACK_DURATION = 15  # measured in seconds
    SAMPLES_PER_TRACK = SAMPLE_RATE * TRACK_DURATION
    num_mfcc = 13
    n_fft = 2048
    hop_length = 512
    num_segments = 2
    samples_per_segment = int(SAMPLES_PER_TRACK / num_segments)
    num_mfcc_vectors_per_segment = math.ceil(samples_per_segment / hop_length)
    start = samples_per_segment
    finish = start + samples_per_segment
    samples_per_segment = int(SAMPLES_PER_TRACK / num_segments)
    num_mfcc_vectors_per_segment = math.ceil(samples_per_segment / hop_length)
    mfcc = librosa.feature.mfcc(signal[start:finish], n_mfcc=num_mfcc, n_fft=n_fft, hop_length=hop_length)
    mfcc = mfcc.T
    x_test = []
    x_test.append(mfcc.tolist())
    start2 = finish
    finish2 = start2 + samples_per_segment
    mfcc2 = librosa.feature.mfcc(signal[start2:finish2], n_mfcc=num_mfcc, n_fft=n_fft, hop_length=hop_length)
    mfcc2 = mfcc2.T
    x2_test = []
    x2_test.append(mfcc2.tolist())
    return x_test, x2_test


def is_stop_to_long(signal, signal2):
    """
    :param signal: 影片前半
    :param signal2: 影片後半
    :return key = 0 全部的聲音片段偵測到斷句太長
            key = 1 部分的聲音片段偵測到斷句太長
            key = 2 全部影片說話流暢
    """
    prediction = toolongmodel_girl.predict(signal)
    predicted_index = np.argmax(prediction, axis=1)

    prediction2 = toolongmodel_girl.predict(signal2)
    predicted_index2 = np.argmax(prediction2, axis=1)
    # print("\nSTOP　TOO LONG")
    # print("first segment: ", predicted_index)
    # print("second segment: ", predicted_index2)
    key = predicted_index2 + predicted_index

    return key


def is_weird_sound(s1, s2, s3, s4, s5):
    prediction = isweirdmodel_girl.predict(s1)
    prediction2 = isweirdmodel_girl.predict(s2)
    prediction3 = isweirdmodel_girl.predict(s3)
    prediction4 = isweirdmodel_girl.predict(s4)
    prediction5 = isweirdmodel_girl.predict(s5)

    p1 = np.argmax(prediction, axis=1)
    p2 = np.argmax(prediction2, axis=1)
    p3 = np.argmax(prediction3, axis=1)
    p4 = np.argmax(prediction4, axis=1)
    p5 = np.argmax(prediction5, axis=1)
    sum = p1 + p2 + p3 + p4 + p5
    if sum >= 4:
        return 2
    elif sum >= 2:
        return 1
    else:
        return 0


def is_voice_calm(dbfs, freq):
    """
    :return key = 0 全部聲音片段過於平淡
            key = 1 部分聲音片段過於平淡
            key = 2 全部聲音抑揚頓挫 起伏得當:
    """

    if dbfs == 2 & freq == 2:
        key = 1
    else:
        key = 2
    return key


def is_aptitude_good(signal1, PRETEST_DBFS):
    """
    :param signal1:
    :return  key = 0 說話聲音正常
             key = 1 說話聲音比平常大聲
             key = 2 說話聲音比平常小聲
    """
    signal2 = signal1[44100:]
    chunk_size = 44100
    num_chunk = len(signal2) // chunk_size
    sn = []
    for chunk in range(0, num_chunk):
        sn.append(np.mean(signal2[chunk * chunk_size:(chunk + 1) * chunk_size].astype(float) ** 2))
    logsn = 9 * np.log10(sn) + 115
    librosa.display.waveplot(signal1)
    avg_db = np.mean(logsn)

    key = 0
    if avg_db - PRETEST_DBFS > 15:
        key = 1
    elif PRETEST_DBFS - avg_db > 15:
        key = 2
    else:
        key = 0
    return key, avg_db


def is_frequency_good(signal,PRETEST_FRE):
    """
    :param signal:
    :return key = 0 正常
            key = 1 頻率比平常高:
            key = 2 頻率比平常低

    """
    fft = np.fft.rfft(signal)
    magnitude = np.abs(fft)
    frequency = np.linspace(0, SAMPLE_RATE, len(magnitude))
    left_frequency = frequency[1200:12000]
    left_magnitude = magnitude[1200:12000]

    sum = 0
    key = 0
    for i in range(1, 10000, 10):
        sum = sum + left_frequency[i] * left_magnitude[i]

    # print("sum = ", sum)

    if sum / PRETEST_FRE > 1.6:
        key = 1
    elif sum / PRETEST_FRE < 0.8:
        key = 2
    else:
        key = 0

    return key


def overall_score(scoreA, scoreB, scoreC, scoreD, scoreE):
    if (scoreA + scoreB + scoreC == 6) & (scoreD + scoreE == 0):
        score = 5
    elif (scoreA + scoreB + scoreC == 6) & (scoreD + scoreE != 0):
        score = 4
    elif (scoreA + scoreB + scoreC == 5) & (scoreD + scoreE == 0):
        score = 4
    elif (scoreA + scoreB + scoreC == 5) & (scoreD + scoreE != 0):
        score = 4
    elif (scoreA + scoreB + scoreC == 4) & (scoreD + scoreE == 0):
        score = 4
    elif (scoreA + scoreB + scoreC == 4) & (scoreD + scoreE != 0):
        score = 3
    elif (scoreA + scoreB + scoreC == 3) & (scoreD + scoreE == 0):
        score = 3
    elif (scoreA + scoreB + scoreC == 3) & (scoreD + scoreE != 0):
        score = 2
    elif (scoreA + scoreB + scoreC == 2) & (scoreD + scoreE == 0):
        score = 2
    elif (scoreA + scoreB + scoreC == 2) & (scoreD + scoreE != 0):
        score = 1
    elif (scoreA + scoreB + scoreC == 1) & (scoreD + scoreE == 0):
        score = 1
    elif (scoreA + scoreB + scoreC == 1) & (scoreD + scoreE != 0):
        score = 1
    elif (scoreA + scoreB + scoreC == 0):
        score = 0
    else:
        score = -1

    return score


def feedback(scoreA, scoreB, scoreC, scoreD, scoreE):
    sug = []
    comment = ""

    if scoreA == 2:
        sug.append("Well-controlled broken sentences")
    elif scoreA == 1:
        sug.append("Part of the sentence break is too long")
    elif scoreA == 0:
        sug.append("The sentence break is too long")

    if scoreB == 2:
        sug.append("No unnecessary sound")
    elif scoreB == 1:
        sug.append("Unnecessary speech sounds are detected in some sentences")
    elif scoreB == 0:
        sug.append("Unnecessary speech is detected in the sentence")

    if scoreC == 2:
        sug.append("Speaking voice intonation excellent!!")
    elif scoreC == 1:
        sug.append("Some phrases sound too flat")
    elif scoreC == 0:
        sug.append("The voice is too bland")

    if scoreD == 2:
        sug.append("Talking frequency lower than usual")
    elif scoreD == 1:
        sug.append("Talking frequency higher than usual")
    elif scoreD == 0:
        sug.append("Sound frequency is well controlled")

    if scoreE == 2:
        sug.append("Less loudness than normal speech")
    elif scoreE == 1:
        sug.append("Loudness of speech is greater than normal speech")
    elif scoreE == 0:
        sug.append("Speak with proper volume control")

    if (scoreA + scoreB + scoreC == 6) & (scoreC + scoreD == 0):
        sug.append("The phrases are properly interrupted, with intonation, rise and fall, without unnecessary sounds, "
                   "and the volume and frequency are well controlled, which is exemplary.")
        return sug

    if scoreA < 2 & scoreE == 2:
        comment += "From your conversation, we found that your voice was too long and your volume was too low. This " \
                   "problem may cause the interviewer to think that you are less confident and less generous. We " \
                   "suggest that you memorize the script when preparing this conversation so that you can bridge the " \
                   "sentences more smoothly, and then you will be more confident in the interview."
    elif scoreE == 1 & scoreD == 1 & scoreA == 2:
        comment += "From your conversation, we found that the volume was too loud and the pitch was too high. This " \
                   "problem may cause the interviewer to perceive your personality as arrogant and uncomfortable. We " \
                   "suggest that you try practicing the script in a normal tone, not too tight, so that the interview " \
                   "will be more calm. "
    elif scoreD == 0 & scoreE == 0:
        comment += "Your conversation is very natural in terms of voice control and sounds very stable."
    return sug, comment


def main_girl(TEST_PATH, pretest_fre, pretest_db):
    PRETEST_FRE = pretest_fre  # 這裡要跟前測頻率拿資料
    PRETEST_DBFS = pretest_db  # 這裡要跟前測分貝拿資料
    signal1, sr1 = librosa.load(TEST_PATH, sr=SAMPLE_RATE)
    segment1, segment2 = split_recordings(signal1)
    too_long_score = is_stop_to_long(segment1, segment2)

    s1, s2, s3, s4, s5 = split_recordings_to_six(signal1)
    weird_sound_score = is_weird_sound(s1, s2, s3, s4, s5)

    frequency_score = is_frequency_good(signal1,PRETEST_FRE)
    amplitude_score, avg_db = is_aptitude_good(signal1, PRETEST_DBFS)
    voice_calm_score = is_voice_calm(amplitude_score, frequency_score)
    overall = overall_score(too_long_score, weird_sound_score, voice_calm_score, frequency_score, amplitude_score)
    suggest, cmt = feedback(too_long_score, weird_sound_score, voice_calm_score, frequency_score, amplitude_score)
    suggest_dict = {}
    d_index = 0
    for i in suggest:
        suggest_dict[d_index] = i
        d_index += 1

    rank = ''
    if overall == 1:
        rank = 'D'
    elif overall == 2:
        rank = 'C'
    elif overall == 3:
        rank = 'B'
    elif overall == 4:
        rank = 'A'
    elif overall == 5:
        rank = 'S'
    response = {
        'avg_db': avg_db,
        'stop_too_long': int(too_long_score),
        'weird_sound': int(weird_sound_score),
        'voice_calm': int(voice_calm_score),
        'frequency': frequency_score,
        'amplitude': amplitude_score,
        'overall_score': overall,
        'rank': rank,
        'analyze_json': suggest_dict,
        'feedback': cmt
    }
    return response

# main()
