# coding=utf-8

import sys
from translate import Translator


def main():
    if sys.argc < 2 or sys.argc > 3:
        print("参数数量错误。")
        return
    else:
        translator = Translator()
        if sys.argc == 2:
            in_file = sys.argv[1]
            out_file = '.'.join(in_file.split('.')[:-1]) + '.py'
            translator.translate(in_file, out_file)
        else:
            in_file = sys.argv[1]
            out_file = sys.argv[2]
            translator.translate(in_file, out_file)


if __name__ == '__main__':
    main()
