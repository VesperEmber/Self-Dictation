import random
from weight_calculation import CorpusWeight
# import weight_calculation
import numpy as np
from load_and_delete_words_corpus import load_words_from_corpus, load_words_from_txt, delete_words_from_txt
# from datetime import datetime
import datetime
import pandas as pd
from tabulate import tabulate
import os
import json
import sys

pd.set_option("display.unicode.east_asian_width", True)
pd.set_option('display.max_columns', None)  # 显示所有行(参数设置为 None 代表显示所有行, 也可以自行设置数字)
pd.set_option('display.max_rows', None)  # 显示所有列
pd.set_option('max_colwidth', 100)  # 设置数据的显示长度, 默认为 50
pd.set_option('expand_frame_repr', False)  # 禁止自动换行(设置为 False 不自动换行, True 反之)


def two_days_gap(start_date, end_date=str(datetime.datetime.now().date())):
    """
    接受两个以 '2023-10-24' 格式写成的日期, 这个日期可以是 str 类型, 也可以是 datetime.date 类型
    :param start_date: 起始日期
    :param end_date: 截至日期
    :return: 从 start_date 开始至 end_date 为止的天数, 是个 int, 可以为负
    """
    if not isinstance(start_date, datetime.date):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    if not isinstance(end_date, datetime.date):
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    delta = end_date - start_date
    return delta.days


def scaled_sigmoid(x, k=0.5, a=5, c=3):
    """
    把一个数值 x 在逻辑尺度上拉到0-1之间, x 的具体含义可以是相差的天数, 也可以是其他什么数值
    f(0)=0, f(1)=0.03, f(3)=0.13, f(5)=0.31, f(10)=0.71, f(20)=0.87, f(30)=0.91
    """
    return x / (x + c) / (1 + np.exp(-k * (x - a)))


def calculate_forget_curve_weight(start_date, end_date=str(datetime.datetime.now().date()), k=0.5, a=5, c=3):
    """
    将 start_date 至 end_date 之间相差天数映射为 "遗忘曲线权重"
    :param start_date: 起始日期, 例如 '2023-10-24', 可以为 str 或 datetime.date, 同时也可以为 None, 为 None 时代表从未考过这个词
    :param end_date: 截至日期, 例如 '2023-10-24', 可以为 str 或 datetime.date
    :param k: 斜率参数，决定了"遗忘曲线权重"函数的增长速度, k 值越大，函数的增长越快
    :param a: 位置参数，决定了"遗忘曲线权重"函数的中心位置
    :param c: 将"遗忘曲线权重"函数最小值拉到 0, 同时也控制函数增长速度, 较小的 c 值会使函数更快地增长
    :return: 遗忘权重, 是个 float, 范围 0-1, 当 start_date 为 None 即从未考过这个单词时, 直接返回 1.0(最大权重)
    """
    days_gap = two_days_gap(start_date, end_date) if start_date else None  # 若 days_gap 为 None 则代表从未考过
    return scaled_sigmoid(days_gap, k=k, a=a, c=c) if days_gap else 1.0


def complexity_weight(wordlist, meanings, length_weight=1, meaning_weight=4, k=3):
    """
    给定一个 wordlist 以及其对应的 meanings list, 计算每个单词的 "困难分数", 并缩放为 0-1 之间的一个值 "困难度", 返回 list
    :param wordlist: 给定单词的 list
    :param meanings: 给定 wordlist 的每个单词的意思列表组成的 list, 其本质是个二维 list, 每个元素对应一个单词的意思 list
    :param length_weight: 计算困难程度时考虑单词长度的权重
    :param meaning_weight: 计算困难程度时考虑意思数量的权重
    :param k: 缩放尺度, 用于把困难分数放大到一个值, 以扔到 scaled_sigmoid 中取得好看的结果
    :return: 每个单词的困难度 list, 困难度是 0-1 之间的一个数
    """
    word_lengths = np.array([len(word) for word in wordlist])
    num_meanings = np.array([len(meaning_list) for meaning_list in meanings])
    complexity_scores = k * (length_weight * word_lengths + meaning_weight * num_meanings) / (
            length_weight + meaning_weight)
    complexities = scaled_sigmoid(complexity_scores)
    return list(complexities)


# class Corpus(weight_calculation.CorpusWeight):
class Corpus(CorpusWeight):
    def __init__(self, corpus, language='english'):
        super().__init__(corpus=corpus, language=language)

    def calculate_probs(self, correct_rate=True, test_times=True, forget_curve=True, difficulty=True, cr=1.0, tt=1.0,
                        fc=1.0, di=1.0, temperature=1.0) -> list:
        """
        根据每个单词的考察权重, 计算其对应的被抽概率, 并以列表形式返回
        :param correct_rate: 布尔值, True 代表考虑听写正确率对抽查单词的影响
        :param test_times: 布尔值, True 代表考虑考察次数对抽查单词的影响
        :param forget_curve: 布尔值, True 代表考虑遗忘曲线对抽查单词的影响
        :param difficulty: 布尔值, True 代表考虑单词难度对抽查单词的影响
        :param cr: 浮点数, 为考虑 correct_rate 所占的权重
        :param tt: 浮点数, 为考虑 test_times 所占的权重
        :param fc: 浮点数, 为考虑 forget_curve 所占的权重
        :param di: 浮点数, 为考虑 difficulty 所占的权重
        :param temperature: 温度参数, 用来控制输出概率均匀程度, 越大越均匀, 越小差异越大
        :return: probs, 它是个 list, 其中每个元素是按权重分配的概率
        """
        weight_list = self.calculate_weights(correct_rate=correct_rate, test_times=test_times,
                                             forget_curve=forget_curve, difficulty=difficulty,
                                             cr=cr, tt=tt, fc=fc, di=di)
        adjusted_weights = np.array(weight_list) / temperature
        exp_weights = np.exp(adjusted_weights - np.max(adjusted_weights))
        probs = exp_weights / np.sum(exp_weights)
        return list(probs)

    def random_sample(self, nums=0) -> list:
        """
        简单随机抽样, 从 self.wordlist 单词本中随机抽取 nums 个单词, 组成 wordlist 列表并返回
        :param nums: 待抽词数, 若 <=0 则代表全部抽取
        :return: wordlist, 包含 nums 个从 self.corpus 中随机抽取的单词, 是个 list
        """
        wordlist = self.wordlist.copy()  # 为防止 wordlist 做 shuffle 影响到原本的 self.wordlist
        random.shuffle(wordlist)
        # nums <= 0 时认为是全部抽取
        if nums <= 0:
            return wordlist
        return wordlist[:nums]

    def smart_sample(self, nums=0, correct_rate=True, test_times=True, forget_curve=True, difficulty=True, cr=1.0,
                     tt=1.0, fc=1.0, di=1.0, temperature=1.0) -> list:
        """
        智能抽样, 从 self.wordlist 单词本中智能地抽取 nums 个单词, 组成 wordlist 列表并返回
        智能抽样会默认考虑(可通过传参修改)各种权重(正确率, 考察次数, 遗忘曲线, 单词困难度), 来生成其对应的考察权重(各权重占比可调), 并转换为考察概率
        考察概率列表和为 1, 每个元素为做对应单词做单次抽样的抽查概率
        如果 correct_rate, test_times, forget_curve, difficulty 参数全部设置为 False, 即不考虑任何一种权重, 那么智能抽样将退化为简单随机抽样
        :param nums: 待抽词数, 若 <=0 则代表全部抽取
        :param correct_rate: 布尔值, True 代表考虑听写正确率对抽查单词的影响
        :param test_times: 布尔值, True 代表考虑考察次数对抽查单词的影响
        :param forget_curve: 布尔值, True 代表考虑遗忘曲线对抽查单词的影响
        :param difficulty: 布尔值, True 代表考虑单词难度对抽查单词的影响
        :param cr: 浮点数, 为考虑 correct_rate 所占的权重
        :param tt: 浮点数, 为考虑 test_times 所占的权重
        :param fc: 浮点数, 为考虑 forget_curve 所占的权重
        :param di: 浮点数, 为考虑 difficulty 所占的权重
        :param temperature: 温度参数, 用来控制输出概率均匀程度, 越大越均匀, 越小差异越大
        :return: wordlist, 包含 nums 个从 self.corpus 中智能抽取的单词, 是个 list
        """
        if nums <= 0:  # 若 <=0 则全部抽取
            return self.wordlist
        probs = self.calculate_probs(correct_rate=correct_rate, test_times=test_times, forget_curve=forget_curve,
                                     difficulty=difficulty, cr=cr, tt=tt, fc=fc, di=di, temperature=temperature)
        wordlist = np.random.choice(self.wordlist, size=nums, p=probs, replace=False)  # 参数 replace=False 表示做不放回抽样
        return wordlist

    # def divide_corpus_by_date(self, start_date, end_date=str(datetime.now().date())):
    def divide_corpus_by_date(self, start_date, end_date=str(datetime.datetime.now().date())):
        """
        根据日期来划分目前持有的子单词本, 拿出从 start_date 起至 end_date 导入的单词, 并组成新的单词本(这个操作不会影响主单词本)
        :param start_date: 起始日期, 可以是 str 或 datetime.datetime.date, 但形式上必须为 '2023-10-24'
        :param end_date: 截止日期, 可以是 str 或 datetime.datetime.date, 但形式上必须为 '2023-10-24'
        """
        # 确保日期为 str 类型, 便于接下来做比较
        start_date = str(start_date)
        end_date = str(end_date)
        sub_corpus = {word: self.corpus[word] for word, import_date in zip(self.wordlist, self.import_date_list) if
                      start_date <= import_date <= end_date}
        # 更换目前持有的单词本
        self.__init__(sub_corpus, language=self.language)
        # print(f'divide_corpus_by_date {start_date} {end_date}')  # debug

    def divide_corpus_by_tag(self, tag):
        """
        根据单词的 tag 来划分目前持有的单词本并重新持有(这个操作不会影响主单词本)
        即挑出同时满足所有 tag 的单词
        :param tag: 单词的 tag, 可以是 str, 最好是由 str 组成的 list
        """
        # 保证 tag 一定为 list
        if not tag:
            tag = []
        if isinstance(tag, str):
            tag = [tag]
        sub_corpus = {word: self.corpus[word] for word, t in zip(self.wordlist, self.tag_list) if
                      set(tag).issubset(set(t))}
        if len(sub_corpus) == 0:
            print(
                "\033[31m" + f'Warning: none of the words have tags \"{", ".join(tag)}\", so nothing happened.' + "\033[0m")
        # 更换目前持有的词典
        else:
            self.__init__(sub_corpus, language=self.language)
        # print(f'divide_corpus_by_tag {tag}')  # debug

    def divide_corpus_by_nums(self, nums=0):
        """
        选取目前持有单词本的前 nums 个单词来划分子单词本, 并重新持有(这个操作不会影响主单词本)
        :param nums: 若 num <= 0 则什么都不做
        """
        if nums <= 0:
            return
        sub_corpus = {word: self.corpus[word] for word in self.wordlist[:nums]}
        # 更换目前持有的词典
        self.__init__(sub_corpus, language=self.language)
        # print(f'divide_corpus_by_nums {nums}')  # debug

    def display_corpus(self, nums=0, *args):
        """
        以直观的方式展示目前持有的单词本中前 nums 个单词的信息, 默认展示单词以及其对应意思
        输入除了 nums 外还可以有多个 arg 参数, arg 参数的合法范围包括:
        ['language', 'voice_name', 'import_date', 'last_test_date', 'test_times', 'correct',
         'wrong', 'case_sensitivity', 'tag', 'all_params', 'tabulate', 'weight']
         其中, 当只有 nums 没有 args 时默认仅展示单词以及其对应意思. 当有 args 时, args 其中参数若有包括例如 'language', 则会多出一列
         用于展示每个单词的 'language' 参数. 当 args 中包含 'all_params' 时则全部展示, 当 args 中包含 'tabulate' 时则会把展示结果以
         更为精美的表格形式呈现
        :param nums: 若 nums<=0 则全部展示
        :param args: 可变参数列表, 理论上来讲接受的应该是多个 str, 每个 str 代表一个指令例如 'import_date',
                     可以让函数按 args 的顺序在原本展示的拼写和中文后, 依次展示单词的相关信息
        """
        # 若 nums<=0 则全部展示, 同时也限制 nums 在合理范围内
        if nums <= 0 or nums > self.corpus_size:
            nums = self.corpus_size
        wordlist = self.wordlist[:nums]
        meanings_list = list(map(', '.join, self.meanings_list[:nums]))
        valid_order_list = ['language', 'voice_name', 'import_date', 'last_test_date', 'test_times', 'correct', 'wrong',
                            'case_sensitivity', 'tag', 'all_params', 'weight']  # 'tabulate' 也是合法的, 但未加入进去, 其在后面单独判断
        # valid_order 即为输入 args 参数中合法的项, invalid_order 为非法的项
        valid_order = sorted([order for order in args if order in valid_order_list])
        invalid_order = [order for order in args if order not in valid_order_list]
        if 'tabulate' in invalid_order:
            invalid_order.remove('tabulate')
        dt = {'<word>': wordlist, '<meanings>': meanings_list}

        if 'all_params' not in valid_order:
            dt.update({f'<{order}>': [self.corpus[word][order] for word in wordlist]
                       for order in valid_order if order not in ['tag', 'weight']})
            if 'tag' in valid_order:
                dt.update({'<tag>': [', '.join(tag) for tag in [self.corpus[word]['tag'] for word in wordlist]]})
            if 'weight' in valid_order:
                dt.update({'<weight>': map(lambda x: round(x, 2), self.calculate_weights())})
        else:  # 'all_params', 即展示目前持有的单词本的全部信息
            dt.update({f'<{order}>': [self.corpus[word][order] for word in wordlist]
                       for order in valid_order_list if order not in ['tag', 'all_params', 'weight']})
            dt.update({'<tag>': [', '.join(tag) for tag in [self.corpus[word]['tag'] for word in wordlist]]})
            dt.update({'<weight>': list(map(lambda x: round(x, 2), self.calculate_weights()))[:nums]})
        # print(dt)  # debug
        df = pd.DataFrame(dt)
        df.index = range(1, nums + 1)
        df.astype(str)
        if 'tabulate' in args:
            df.insert(0, '', [i + 1 for i in range(nums)])
            print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
            # print(f'{nums} words in total')
        else:
            if nums == 0:
                print(f'this (partial) "{self.language}" corpus you\'re currently holding is empty')
            else:
                print(df)
        if invalid_order:
            print('\033[31mWorning: \"' + ', '.join(invalid_order) + '\" are invalid params.\033[0m')
            print('\033[33mPlease use: \"' + ', '.join(valid_order_list + ['tabulate']) + '\" instead.\033[0m')

    def sort_corpus_by_instruction(self, instruction='import_date', reverse=False):
        """
        将目前持有的 self.corpus 按照 instruction 指出的关键词的对单词进行排序, 默认为升序
        :param instruction: 是一个 str, 其可以为
        ['word', 'import_date', 'last_test_date', 'test_times', 'correct', 'wrong', 'case_sensitivity', 'weight']
         若一个单词的 'last_test_date' 一项为 None, 则将其赋值为 '0', 这样可以在与如 '2023-10-25' 的 str 日期进行比较时算作更小
         'weights' 参数代表按照每个单词的考察权重进行排序, 这里的权重指的是按照全部 4 种子权重综合考虑后的结果
        :param reverse: 默认为 False 即升序排序, 若为 True 则进行降序排列
        """
        if reverse == 'reverse':
            reverse = True
        last_test_date_list = [last_test_date if last_test_date else '0' for last_test_date in self.last_test_date_list]
        # 定义合法 instruction 到其对应单词元素列表的映射
        dt = {'word': self.wordlist, 'import_date': self.import_date_list, 'last_test_date': last_test_date_list,
              'test_times': self.test_times_list, 'correct': self.correct_times_list, 'wrong': self.wrong_times_list,
              'case_sensitivity': self.case_sensitivity_list, 'weight': self.calculate_weights()}
        if instruction not in dt:
            print(f'\033[31m"{instruction}" is invalid instruction\033[0m')
            print('Please use: \033[33m\"' + ', '.join(list(dt.keys())) + '\" instead.\033[0m')
            return
        # 使用zip将字典键和权重列表合并，并使用sorted进行排序
        wordlist = self.wordlist.copy()
        sorted_item = sorted(zip(wordlist, dt[instruction]), key=lambda x: x[1], reverse=reverse)
        sorted_wordlist = [item[0] for item in sorted_item]
        sorted_corpus = {word: self.corpus[word] for word in sorted_wordlist}
        self.__init__(sorted_corpus, language=self.language)
        flag = ' in reverse order.' if reverse else '.'
        print(f'\033[33m\"Corpus has been sorted by keyword "{instruction}"{flag}\033[0m')

    def load_main_corpus(self, language):
        """
        更改目前持有的单词本为给定 language 的主单词本
        :param language: 一个 str, 例如 'english'
        """

        # current_script_path = os.path.abspath(__file__)
        # current_script_path = os.path.abspath(sys.executable)
        # current_script_directory = os.path.dirname(current_script_path).replace('\\', '/')
        current_script_directory = os.getcwd()
        # project_path = os.path.join(current_script_directory, "..")
        # project_path = os.path.normpath(project_path).replace('\\', '/')
        main_corpus_path = current_script_directory + '/vocabulary/' + language + '/corpus.json'
        with open(main_corpus_path, "r", encoding='utf-8') as json_file:
            main_corpus = json.load(json_file)
        self.__init__(main_corpus, language)

    def import_words_from_txt(self, filepath):
        load_words_from_txt(filepath)

    def delete_words_from_txt(self, filepath):
        delete_words_from_txt(filepath)

    def save_corpus_changes(self):
        """
        保存目前持有的 corpus 中对单词做出的修改操作
        可能的修改包括: 主动改变单词 tag, 听写后改变单词的 last_test_date, test_times, correct, wrong
        """
        # load_words_from_corpus 可以自动定位到主单词本 "language"/corpus.json 的位置加载它, 并用 self.corpus 更新然后存回原位
        load_words_from_corpus(self.corpus, language=self.language)
        # print(f'\033[33mCorpus has been updated back to the "{self.language}" corpus.\033[0m')


if __name__ == '__main__':
    corpus_path = 'D:/PythonProjects/PycharmProjects/Self_Dictation/vocabulary/english/corpus.json'
    with open(corpus_path, "r", encoding='utf-8') as json_file:
        corpus = json.load(json_file)

    corpus_obj = Corpus(corpus)
    # print(corpus_obj)
    # print(corpus_obj.corpus)
    # print(corpus_obj.wordlist)
    # while True:
    #     orders = input('orders:').split()
    #     try:
    #         orders[0] = int(orders[0])
    #     except:
    #         orders = [0] + orders
    #     corpus_obj.display_corpus(*orders)

    corpus_obj.display_corpus(0, 'all_params', 'tabulate')
    # corpus_obj.display_corpus(0, 'all_params')
    # corpus_obj.sort_corpus_by_instruction('weight')
    # corpus_obj.display_corpus(0, 'all_params')
    # corpus_obj.display_corpus(0, 'tabulate', 'weight')
    # corpus_obj.divide_corpus_by_tag('GRE')
    # # corpus_obj.display_corpus(0, 'all_params')
    # # corpus_obj.divide_corpus_by_tag(['CET4', 'GRE'])
    # # corpus_obj.display_corpus(0, 'all_params')
    # # corpus_obj.sort_corpus_by_instruction('last_test_dat')
    # corpus_obj.display_corpus(0, 'all_params', 'tabulate')
    #
    # corpus_obj.load_main_corpus(language='english')
    # corpus_obj.display_corpus(0, 'all_params', 'tabulate')
