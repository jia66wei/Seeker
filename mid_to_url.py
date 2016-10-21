#-*-coding:utf8-*-
'''
@author:jiawei4
@use:WB mid与短链互转
@date:2016-05-26
@参考网络
'''
import sys

class ConversionTool:
    def __init__(self, ab="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        self.alphabet = ab

    def base62_encode(self, num):
        """Encode a number in Base X

        `num`: The number to encode
        `alphabet`: The alphabet to use for encoding
        """
        if (num == 0):
            return self.alphabet[0]
        arr = []
        base = len(self.alphabet)
        while num:
            rem = num % base
            num = num // base
            arr.append(self.alphabet[rem])
        arr.reverse()
        return ''.join(arr)

    def base62_decode(self, string):
        """Decode a Base X encoded string into the number

        Arguments:
        - `string`: The encoded string
        - `alphabet`: The alphabet to use for encoding
        """
        base = len(self.alphabet)
        strlen = len(string)
        num = 0

        idx = 0
        for char in string:
            power = (strlen - (idx + 1))
            num += self.alphabet.index(char) * (base ** power)
            idx += 1

        return num


    def mid_to_url(self, midint):
        '''
        >>> mid_to_url(3501756485200075)
        'z0JH2lOMb'
        >>> mid_to_url(3501703397689247)
        'z0Ijpwgk7'
        >>> mid_to_url(3501701648871479)
        'z0IgABdSn'
        >>> mid_to_url(3500330408906190)
        'z08AUBmUe'
        >>> mid_to_url(3500247231472384)
        'z06qL6b28'
        >>> mid_to_url(3491700092079471)
        'yCtxn8IXR'
        >>> mid_to_url(3486913690606804)
        'yAt1n2xRa'
        '''
        midint = str(midint)[::-1]
        size = len(midint) / 7 if len(midint) % 7 == 0 else len(midint) / 7 + 1
        result = []
        for i in range(size):
            s = midint[i * 7: (i + 1) * 7][::-1]
            s = self.base62_encode(int(s))
            s_len = len(s)
            if i < size - 1 and len(s) < 4:
                s = '0' * (4 - s_len) + s
            result.append(s)
        result.reverse()
        return ''.join(result)
    				
    def url_to_mid(self, url):
        '''
        >>> url_to_mid('z0JH2lOMb')
        3501756485200075L
        >>> url_to_mid('z0Ijpwgk7')
        3501703397689247L
        >>> url_to_mid('z0IgABdSn')
        3501701648871479L
        >>> url_to_mid('z08AUBmUe')
        3500330408906190L
        >>> url_to_mid('z06qL6b28')
        3500247231472384L
        >>> url_to_mid('yCtxn8IXR')
        3491700092079471L
        >>> url_to_mid('yAt1n2xRa')
        3486913690606804L
        '''
        url = str(url)[::-1]
        size = len(url) / 4 if len(url) % 4 == 0 else len(url) / 4 + 1
        result = []
        for i in range(size):
            s = url[i * 4: (i + 1) * 4][::-1]
            s = str(self.base62_decode(str(s)))
            s_len = len(s)
            if i < size - 1 and s_len < 7:
                s = (7 - s_len) * '0' + s
            result.append(s)
        result.reverse()
        return int(''.join(result))


if __name__ == '__main__':
    tool = ConversionTool()
    mid = 3986633055194449
    print tool.mid_to_url(mid)
    url = 'DtVX5uDVD'
    print tool.url_to_mid(url)
