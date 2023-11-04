import datetime
import numpy as np


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
    # return x / (x + c) / (1 + np.exp(-k * (x - a)))
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
    return scaled_sigmoid(days_gap, k=k, a=a, c=c) if days_gap is not None else 1.0


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
    # word_lengths = np.array([len(word) for word in wordlist])
    # num_meanings = np.array([len(meaning_list) for meaning_list in meanings])
    word_lengths = np.array([len(word) for word in wordlist])
    num_meanings = np.array([len(meaning_list) for meaning_list in meanings])
    complexity_scores = k * (length_weight * word_lengths + meaning_weight * num_meanings) / (
            length_weight + meaning_weight)
    complexities = scaled_sigmoid(complexity_scores)
    return list(complexities)


class CorpusWeight:
    def __init__(self, corpus: dict, language='english'):
        self.language = language
        self.corpus = corpus
        self.wordlist = list(self.corpus.keys())
        self.corpus_size = len(self.wordlist)
        self.meanings_list = [self.corpus[word]['meanings'] for word in self.wordlist]
        self.import_date_list = [self.corpus[word]['import_date'] for word in self.wordlist]
        self.last_test_date_list = [self.corpus[word]['last_test_date'] for word in self.wordlist]
        self.test_times_list = [self.corpus[word]['test_times'] for word in self.wordlist]
        self.correct_times_list = [self.corpus[word]['correct'] for word in self.wordlist]
        self.wrong_times_list = [self.corpus[word]['wrong'] for word in self.wordlist]
        self.case_sensitivity_list = [self.corpus[word]['case_sensitivity'] for word in self.wordlist]
        self.tag_list = [self.corpus[word]['tag'] for word in self.wordlist]

    def refresh(self):
        """
        如果 self.corpus 改动过(例如重新排序), 则应调用 self.refresh() 将包括 self.wordlist 在内的参数全部刷新一遍
        仅适用于不更换目前持有的 corpus, 而仅仅是改动过目前持有的 corpus 时
        即 sort 后可以 refresh, 但 divide 后不可以
        """
        self.__init__(self.corpus, language=self.language)  # self.corpus 和 self.language 是不变的

    def correct_rate_weights(self) -> list:
        """
        计算正确率权重: 直接取错误率作为权重, 即可使得正确率越低权重越大, 且范围处在 0-1
        要注意: 单词一次都没考过时 test_times 为 0, 为防止除数为 0 问题, 应给 test_times 加上一个小正数 1e-6
        单词一次都没考过时 test_times 为 0 时权重应设置为 0.5
        :return: 正确率权重(即错误率)
        """
        wrong_rates = [min(wrong_times / (test_times + 1e-6), 1.0) for wrong_times, test_times in
                       zip(self.wrong_times_list, self.test_times_list)]
        for i in range(len(self.correct_times_list)):
            # if self.correct_times_list[i] == 0:
            #     wrong_rates[i] = 0.5
            if self.test_times_list[i] == 0:
                wrong_rates[i] = 0.5
        return wrong_rates

    def test_times_weights(self) -> list:
        """
        抽查频率权重, 一个单词考察次数越相对其他单词越少, 则其权重越大, 权重范围在 0-1 区间
        若每个单词考察次数都相同, 则无所谓一个单词相对其他单词的考察次数多少, 则返回的权重列表每一个权重都为 0
        :return: 由每个单词对应的抽查频率权重组成的列表
        """
        # weights = [-np.log(test_time + 1) for test_time in self.test_times_list]
        weights = [-np.log(test_time + 1) for test_time in self.test_times_list]
        min_weight = min(weights)
        max_weight = max(weights)
        if max_weight == min_weight:
            return [0.0] * len(self.test_times_list)
        scaled_weights = [(w - min_weight) / (max_weight - min_weight) for w in weights]
        return scaled_weights

    def forget_curve_weights(self, k=0.5, a=5, c=3) -> list:
        """
        将单词本每个单词上次测试时间至今日相差天数映射为 "遗忘曲线权重", 这是个 0-1 之间的数, 如果单词还未考过, 则权重为 1.0
        :param k: 斜率参数，决定了"遗忘曲线权重"函数的增长速度, k 值越大，函数的增长越快
        :param a: 位置参数，决定了"遗忘曲线权重"函数的中心位置
        :param c: 将"遗忘曲线权重"函数最小值拉到 0, 同时也控制函数增长速度, 较小的 c 值会使函数更快地增长
        :return: 遗忘权重列表, 其每个元素都是个 float, 范围 0-1, 当从未考过这个单词时, 其对应的遗忘权重为 1.0(最大权重)
        """
        end_date = str(datetime.datetime.now().date())  # 取得今天的时间
        forget_weights = [calculate_forget_curve_weight(start_date=last_test_date, end_date=end_date, k=k, a=a, c=c)
                          for last_test_date in self.last_test_date_list]
        return forget_weights

    def difficulty_weights(self, length_weight=1, meaning_weight=4, k=3) -> list:
        """
        计算每个单词的 "困难分数", 并缩放为 0-1 之间的一个值作为 "困难度权重", 返回 list
        :param length_weight: 计算困难程度时考虑单词长度的权重
        :param meaning_weight: 计算困难程度时考虑中文意思数量的权重
        :param k: 缩放尺度, 用于把困难分数放大到一个值, 以扔到 scaled_sigmoid 方法中取得分布在 0-1 之间的 "困难度权重"
        :return: 每个单词的困难度 list, 困难度是 0-1 之间的一个数
        """
        return complexity_weight(self.wordlist, self.meanings_list, length_weight=length_weight,
                                 meaning_weight=meaning_weight, k=k)

    def calculate_weights(self, correct_rate=True, test_times=True, forget_curve=True, difficulty=True, cr=1.0, tt=1.0,
                          fc=1.0, di=1.0) -> list:
        """
        对每个单词根据给定要求考虑的情况(正确率, 考察次数, 遗忘曲线, 单词困难度)求得其对应的考察权重, 最终返回一个列表, 每个元素是对应单词的权重
        :param correct_rate: 布尔值, True 代表考虑听写正确率对抽查单词的影响
        :param test_times: 布尔值, True 代表考虑考察次数对抽查单词的影响
        :param forget_curve: 布尔值, True 代表考虑遗忘曲线对抽查单词的影响
        :param difficulty: 布尔值, True 代表考虑单词难度对抽查单词的影响
        :param cr: 浮点数, 为考虑 correct_rate 所占的权重
        :param tt: 浮点数, 为考虑 test_times 所占的权重
        :param fc: 浮点数, 为考虑 forget_curve 所占的权重
        :param di: 浮点数, 为考虑 difficulty 所占的权重
        :return: 考察权重列表, 其中每个元素为对应单词的考察权重
        """
        weights = np.array([0.0] * len(self.wordlist))
        if correct_rate:
            weights += np.array(self.correct_rate_weights()) * cr
        if test_times:
            weights += np.array(self.test_times_weights()) * tt
        if forget_curve:
            weights += np.array(self.forget_curve_weights()) * fc
        if difficulty:
            weights += np.array(self.difficulty_weights()) * di
        return list(weights)


if __name__ == '__main__':
    print(calculate_forget_curve_weight('2023-11-1'))
    print(calculate_forget_curve_weight(None))
    print(round((1 / (1 + 1e-6)), 3))

    #
    # corpus_weight_obj = CorpusWeight(corpus)
    # # print(corpus_weight_obj)
    # # print(corpus_weight_obj.corpus)
    # # print(corpus_weight_obj.wordlist)
    # # print(corpus_weight_obj.meanings_list)
    # # print(corpus_weight_obj.import_date_list)
    # print(corpus_weight_obj.last_test_date_list)
    # # print(corpus_weight_obj.test_times_list)
    # # print(corpus_weight_obj.correct_times_list)
    # # print(corpus_weight_obj.wrong_times_list)
    # # print(corpus_weight_obj.case_sensitivity_list)
    # # print(corpus_weight_obj.tag_list)
    # print(corpus_weight_obj.correct_rate_weights())
    # print(corpus_weight_obj.test_times_weights())
    # print(corpus_weight_obj.forget_curve_weights())
    # print(corpus_weight_obj.difficulty_weights())
    #
    # print('2023-10-23' < '2023-10-24')
    # print(corpus)
    # weight_list = [0, -1, -2]
    # print(calculate_probs(weight_list), sum(calculate_probs(weight_list)))
    # wordlist = ['burp', 'metropolitan', 'clip', 'chimera', 'interpolate', 'crunch', 'subject']
    # meanings = [['打嗝'],
    #             ['大都市的'],
    #             ['夹子', '夹紧', '裁剪'],
    #             ['嵌合体', '幻想'],
    #             ['插嘴', '内插'],
    #             ['碎裂声', '发出碎裂声', '至关重要的', '缺(钱)'],
    #             ['主语', '主题', '科目', '研究对象', '使屈服', '臣民']]
    # weight_list = complexity_weight(wordlist, meanings)
    # print(weight_list)
    # print(calculate_probs(weight_list), sum(calculate_probs(weight_list)))
    # print(-np.log([1, 2, 3, 4, 5]))
