import azure.cognitiveservices.speech as speechsdk
import json
import os
import pyttsx3
import hashlib
import base62
# import sys
import sounddevice as sd
from scipy.io.wavfile import read


def get_speech_config_dt():
    # current_script_path = os.path.abspath(sys.executable)
    # current_script_directory = os.path.dirname(current_script_path)

    current_script_directory = os.getcwd()  # debug

    with open(current_script_directory.replace('\\', '/') + '/speech_config.json', 'r') as f:
        speech_config_dt = json.load(f)
    return speech_config_dt


# with open('config.json', 'r') as f:
#     config = json.load(f)
#
# subscription_key = config['SPEECH_KEY']
# service_region = config['SPEECH_REGION']
# language = config['language']


def get_md5_hash_base62_encoded(s):
    hash_value = hashlib.md5(s.encode()).hexdigest()
    hash_int = int(hash_value, 16)
    base62_encoded = base62.encode(hash_int)
    return base62_encoded


def pyttsx3_text_to_speech(word, language, speed=None):
    if language not in ['english', 'chinese']:
        print('pyttsx3 can only read Chinese and English.')
        return False
    engine = pyttsx3.init()
    if speed:
        engine.setProperty('rate', speed)
    engine.say(word)
    engine.runAndWait()
    # print('pyttsx3 speech synthesized for text [' + word + ']')
    return True


def azure_text_to_speech(word, subscription_key=get_speech_config_dt()['SPEECH_KEY'],
                         service_region=get_speech_config_dt()['SPEECH_REGION'],
                         language=get_speech_config_dt()['language'], to_file=False,
                         voice_name=None):
    # 设置语音服务的配置
    try:

        speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
    except Exception as e:
        # print(e)
        if to_file:
            print(f'\033[31mFailed to load "{word}" audio to "{language}" corpus.\033[0m')
        else:
            pyttsx3_text_to_speech(word, language=language)
            # print(f'use pyttsx3 to read "{word}" instead')
        return

    # if language not in config["voice_name"]:
    #     language = 'english'
    #     print('The language does not exist or is not supported yet, auto changed to English.')
    # speech_config.speech_synthesis_voice_name = config['voice_name'][language]
    if not voice_name:
        voice_name = get_speech_config_dt()['voice_name'][language]

    speech_config.speech_synthesis_voice_name = voice_name

    # current_script_path = os.path.abspath(__file__)
    # current_script_path = os.path.abspath(sys.executable)
    # current_script_directory = os.path.dirname(current_script_path)
    current_script_directory = os.getcwd()
    project_path = current_script_directory
    # project_path = os.path.join(current_script_directory, "..", "..")
    # project_path = os.path.normpath(project_path).replace('\\', '/')
    if to_file:
        save_path = project_path + '/utterances/' + language
        sound_save_path = save_path + '/' + get_md5_hash_base62_encoded(word) + '.wav'
        # print(sound_save_path)  # debug
        sound_save_path = sound_save_path.replace('\\', '/')
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        else:
            if os.path.exists(sound_save_path):
                # print(f'"{language}" sound source word "{word}" {get_md5_hash_base62_encoded(word)}.wav already existing')
                print(
                    f'Audio of \033[33m"{word}"\033[0m is \033[33malready existed\033[0m at \033[33m{sound_save_path}\033[0m')
                # f'\033[33m{get_md5_hash_base62_encoded(word)}.wav\033[0m')
                return
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True, filename=sound_save_path)
    else:
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    try:
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    except Exception as e:  # debug
        print(e)
        file_name = "outputaudio.wav"
        file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)
        # input('就是这里！')

    speech_synthesis_result = speech_synthesizer.speak_text_async(word).get()
    # input("debug!")
    # if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    #     print("Azure speech synthesized for text [{}]".format(word))
    # elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
    if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        # print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                # print("Error details: {}".format(cancellation_details.error_details))
                # print("Did you set the speech resource key and region values?")
                pass
        if to_file:
            print(f'\033[31mCannot load "{word}" sound source to "{language}".\033[0m')
        else:
            pyttsx3_text_to_speech(word, language=language)
            # print(f'use pyttsx3 to read "{word}" instead')
        return False
    if to_file:
        print(
            f'Audio of \033[33m"{word}"\033[0m has been \033[36mloaded into\033[0m: \033[33m' + project_path + '/utterances/' + language + '/' +
            get_md5_hash_base62_encoded(word) + '.wav\033[0m')
    return True


def azure_system_speech(word, subscription_key=get_speech_config_dt()['SPEECH_KEY'],
                        service_region=get_speech_config_dt()['SPEECH_REGION'],
                        language='english', voice_name=None, wait=True):
    connection = True
    # 设置语音服务的配置
    try:
        speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
    except Exception as e:
        # print(e)
        connection = False
        pyttsx3_text_to_speech(word, language=language)
        return connection

    if not voice_name:
        voice_name = get_speech_config_dt()['voice_name'][language]
    speech_config.speech_synthesis_voice_name = voice_name

    # current_script_path = os.path.abspath(sys.executable)
    # current_script_directory = os.path.dirname(current_script_path)
    current_script_directory = os.getcwd()
    project_path = current_script_directory
    project_path = os.path.normpath(project_path).replace('\\', '/')
    save_path = project_path + '/property'
    sound_save_path = save_path + '/' + get_md5_hash_base62_encoded(word) + '.wav'

    if not os.path.exists(save_path):
        os.makedirs(save_path)
    else:
        if os.path.exists(sound_save_path):
            rate, data = read(sound_save_path)
            sd.play(data, rate)
            if wait:
                sd.wait()
            return connection

    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True, filename=sound_save_path)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    speech_synthesis_result = speech_synthesizer.speak_text_async(word).get()
    rate, data = read(sound_save_path)
    sd.play(data, rate)
    if wait:
        sd.wait()
    return connection


if __name__ == '__main__':
    word = 'what the fuck'
    # azure_text_to_speech(word, to_file=True)
    azure_text_to_speech(word)
    # pyttsx3_text_to_speech(word, language=language)
