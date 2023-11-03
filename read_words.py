import sounddevice as sd
from scipy.io.wavfile import read as readwav
import speech_synthesis
import os
import hashlib
import base62
# import sys


def get_md5_hash_base62_encoded(s):
    hash_value = hashlib.md5(s.encode()).hexdigest()
    hash_int = int(hash_value, 16)
    base62_encoded = base62.encode(hash_int)
    return base62_encoded


def get_corpus_path(language='english'):
    # current_script_path = os.path.abspath(__file__)
    # current_script_path = os.path.abspath(sys.executable)
    # current_script_directory = os.path.dirname(current_script_path).replace('\\', '/')

    current_script_directory = os.getcwd()
    # project_path = os.path.join(current_script_directory, "..")
    # project_path = os.path.normpath(project_path).replace('\\', '/')
    # corpus_path = project_path + '/utterances/' + language
    corpus_path = current_script_directory + '/utterances/' + language
    return corpus_path


def read(word, language='english', voice_name=None, speed=200, auto_download=False):
    """
    若有对应language的语料库中有word的.wav音源，则优先直接播放音源
    若无音源，则尝试向Azure api请求下载按language读word的音源，并以.wav格式存储在对应language的语料库中
    若下载音源失败，则使用替代的低质量pyttsx3方案读出word
    :param word: 待读的单词
    :param language: 使用language读word
    :param voice_name: 指定音源来自
    :param speed:若最终使用pyttsx3方案，speed用于指定这个方案的语速
    :param auto_download:若为True，则会在没有音源时自动尝试下载音源
    :return: 字符串，代表最终使用的读单词方案
    """

    corpus_path = get_corpus_path(language=language)
    word_path = corpus_path + '/' + get_md5_hash_base62_encoded(word) + '.wav'
    if os.path.exists(word_path):
        # print(f'use existing "{language}" sound source for "{word}"', word_path)
        # playsound(word_path)
        rate, data = readwav(word_path)
        sd.play(data, rate)
        sd.wait()
        return 'azure'
    elif auto_download:
        speech_synthesis.azure_text_to_speech(word, language=language, to_file=True, voice_name=voice_name)
        if os.path.exists(word_path):
            print(f'successfully downloaded "{word}": "{language}" sound source', word_path)
            # playsound(word_path)
            rate, data = readwav(word_path)
            sd.play(data, rate)
            sd.wait()
            return 'azure'
    # print(f'failed to download: word "{word}" for corpus "{language}", try using pyttsx3 to read.')
    if speech_synthesis.pyttsx3_text_to_speech(word, language=language, speed=speed):
        return 'pyttsx3'
    else:
        return f'pyttsx3 can only read Chinese and English, not for "{language}"'


if __name__ == '__main__':
    # read('お元気ですか?', language='japanese')
    # read('お元気ですか', language='japanese')
    # read('你好，你吃了吗', language='chinese')
    # read('synonymous and trajectory', language='english')
    # read('Guten Morgen!', language='german')
    # read('Wie geht es Ihnen?', language='deutsch')
    #
    # read('这一条估计read不出去了', language='chinese')
    print(get_corpus_path())
