import os
from moviepy.editor import VideoFileClip
from .gaze_tracking import GazeTracking
import numpy as np

import librosa

SAMPLE_RATE = 22050


class Tools(object):

    def __init__(self, videoname):
        self.videoname = videoname

    def doAll(self):
        FileSplit = self.videoname.split('.')
        ResultFile = FileSplit[0] + '_fast' + '.mp4'

        ResultfilePath, Duration = self.fastenvideo(ResultFile)
        GazeModel = GazeTracking(ResultfilePath)
        print('start...')
        eyebrow_height_mean, eyebrow_pitch_mean, mouth_height_mean, mouth_pitch_mean, eyes_pitch_mean = self.CollectPredata(
            GazeModel)
        print('end...')
        return eyebrow_height_mean, eyebrow_pitch_mean, mouth_height_mean, mouth_pitch_mean, eyes_pitch_mean

    def fastenvideo(self, resultfile):
        # 設定路徑
        FilePath = os.path.join('./media/prevideo/', self.videoname)
        ResultfilePath = os.path.join('./media/prevideo/fast/', resultfile)
        # 選取影片+設定時間
        video = VideoFileClip(FilePath)
        duration = video.duration
        # 影片加速
        video = video.time_transform(lambda t: 2 * t, apply_to=['mask', 'video', 'audio']).with_duration(duration / 2)
        video.write_videofile(ResultfilePath)

        return ResultfilePath, duration / 2

    def delete3std(self, listbefore):
        listafter = listbefore
        var = np.std(listafter)
        mean = np.mean(listafter)
        j = 0
        time = len(listafter)

        while True:
            if listafter[j] >= (mean + 3 * var) or listafter[j] <= (mean - 3 * var):
                del listafter[j]
                time -= 1
                if j == time:
                    break
                continue
            j += 1
            if j == time:
                break

        return listafter

    def CollectPredata(self, gazemodel):
        eyebrow_height, eyebrow_pitch, mouth_height, mouth_pitch, eyes_pitch, outblinking, outright, outleft, outcenter = gazemodel.learning_face()
        eyebrow_height_list = self.delete3std(eyebrow_height)
        eyebrow_height_mean = np.mean(eyebrow_height_list)

        eyebrow_pitch_list = self.delete3std(eyebrow_pitch)
        eyebrow_pitch_mean = np.mean(eyebrow_pitch_list)

        mouth_height_list = self.delete3std(mouth_height)
        mouth_height_mean = np.mean(mouth_height_list)

        mouth_pitch_list = self.delete3std(mouth_pitch)
        mouth_pitch_mean = np.mean(mouth_pitch_list)

        eyes_pitch_mean = np.mean(eyes_pitch)

        return eyebrow_height_mean, eyebrow_pitch_mean, mouth_height_mean, mouth_pitch_mean, eyes_pitch_mean

    def saveings(self, signal, gender):
        sum_freq = 0
        if gender == 'M':  # boy
            signal2 = signal[44100:]
            chunk_size = 44100
            num_chunk = len(signal2) // chunk_size
            sn = []
            for chunk in range(0, num_chunk):
                sn.append(np.mean(signal2[chunk * chunk_size:(chunk + 1) * chunk_size].astype(float) ** 2))
            logsn = 20 * np.log10(sn) + 130
            avg_db = np.mean(logsn)

            fft = np.fft.rfft(signal)
            magnitude = np.abs(fft)
            frequency = np.linspace(0, SAMPLE_RATE, len(magnitude))
            left_frequency = frequency[1200:7000]
            left_magnitude = magnitude[1200:7000]
            for i in range(1, 5800, 10):
                sum_freq = sum_freq + left_frequency[i] * left_magnitude[i]
        else:  # girl
            signal2 = signal[44100:]
            chunk_size = 44100
            num_chunk = len(signal2) // chunk_size
            sn = []
            for chunk in range(0, num_chunk):
                sn.append(np.mean(signal2[chunk * chunk_size:(chunk + 1) * chunk_size].astype(float) ** 2))
            logsn = 9 * np.log10(sn) + 115
            avg_db = np.mean(logsn)

            fft = np.fft.rfft(signal)
            magnitude = np.abs(fft)
            frequency = np.linspace(0, SAMPLE_RATE, len(magnitude))
            left_frequency = frequency[1200:12000]
            left_magnitude = magnitude[1200:12000]
            for i in range(1, 10000, 10):
                sum_freq = sum_freq + left_frequency[i] * left_magnitude[i]

        return avg_db, sum_freq

    def presound(self, genderIn):
        soundFileSplit = self.videoname.split('.')
        soundResultFile = soundFileSplit[0] + '_trans' + '.wav'
        FilePath = os.path.join('./media/prevideo/', self.videoname)
        ResultfilePath = os.path.join('./media/prevideo/wav/', soundResultFile)
        # TODO 這裡要輸入影片及音訊儲存的資料夾
        video = VideoFileClip(FilePath)

        video.audio.write_audiofile(ResultfilePath)

        # TODO 這裡要輸入音訊儲存的資料夾
        TEST_PATH = ResultfilePath
        signal1, sr1 = librosa.load(TEST_PATH, sr=SAMPLE_RATE)

        # TODO 這裡要輸入性別
        gender = genderIn
        avg, freq = self.saveings(signal1, gender)

        return avg, freq
