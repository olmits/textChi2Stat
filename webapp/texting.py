import string
import collections
import os
import json
import time
from operator import itemgetter
from random import choice
from itertools import product
from scipy.stats import chisquare as chichi

from webapp.logger import function_logger


text_to_test = {
    'en': "One Hundred Years of Solitude is the story of seven generations of the Buendía Family in the town of Macondo.",
    'fr': "Cent Ans de solitude relate l'histoire de la famille Buendia sur six générations, dans le village imaginaire de Macondo.",
    'es': "El libro narra la historia de la familia Buendía a lo largo de siete generaciones en el pueblo ficticio de Macondo.",
    'de': "Der Roman Hundert Jahre Einsamkeit begleitet sechs Generationen der Familie Buendía und hundert Jahre wirklichen Lebens in der zwar fiktiven Welt von Macondo."
}


class TextProceedStrategy:

    def __init__(self, text: str, num: int):
        self.text = text
        self.num = num
        self.res = dict()

    @function_logger
    def __text_to_words(self) -> list:
        clear_words = self.text.translate(str.maketrans('', '', string.punctuation + string.digits))
        words = clear_words.split()
        return words

    @function_logger
    def _letters_scrabble(self):
        chunks = list()
        for word in self.__text_to_words():
            if len(word) < self.num:
                continue
            step = self.num - 1
            for i in range(0, len(word)-step):
                chunks.append(word[i:i + self.num].lower())
        self.res.update(collections.Counter(chunks))
        self._calc_chunks_frequency(self.res)

    @staticmethod
    @function_logger
    def _calc_chunks_frequency(res: dict):
        denominator = sum(res.values())
        for key, value in res.items():
            res[key] = value / denominator


class CalculateXi2Strategy(TextProceedStrategy):

    def __init__(self, text: str, num: int, iso2: str):
        super().__init__(text, num)
        self._letters_scrabble()
        self.iso2 = iso2
        self.observed_values = list()
        self.expected_values = list()

    @function_logger
    def _get_expected_array(self):
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(APP_ROOT, 'expected.json'), 'r', encoding='utf-8', errors='surrogateescape') as f:
            data = json.load(f)
            d = data[self.iso2][str(self.num)]
            for k, v in self.res.items():
                expected_frequency = d.get(k)
                if expected_frequency is None:
                    continue
                self.observed_values.append(v)
                self.expected_values.append(expected_frequency)
    '''
    Running time: --- 0.9035568237304688 seconds ---
    '''

    @function_logger
    def calculate_xi2(self):
        self._get_expected_array()
        chi2, p_value = chichi(self.observed_values, self.expected_values)
        return round(chi2, 4), round(p_value, 4)


if __name__ == '__main__':
    start_time = time.time()

    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    APP_TMP = os.path.join(APP_ROOT, 'tmp')

    raw_data = {}
    raw_vars = product(text_to_test.keys(), ['2','3'])

    for iso, num in raw_vars:
        if iso not in raw_data.keys():
            raw_data[iso] = {}
        with open(os.path.join(APP_TMP, iso + '.txt'), 'r', encoding='utf-8', errors='surrogateescape') as f:
            data = f.read()
            setup_base = TextProceedStrategy(data, int(num))
            setup_base._letters_scrabble()
            raw_data[iso][num] = {k: v for k, v in setup_base.res.items()}
    with open('expected.json', 'w') as exp_file:
        json.dump(raw_data, exp_file)

    rnd_iso = choice(list(text_to_test.keys()))
    rnd_num = choice(['2', '3'])
    mx_key_en = max(
        raw_data[rnd_iso][rnd_num].items(),
        key=itemgetter(1)
    )[0]
    print(rnd_iso, mx_key_en, raw_data[rnd_iso][rnd_num][mx_key_en])

    print("--- %s seconds ---" % (time.time() - start_time))
