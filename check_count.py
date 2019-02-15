'''检查文件个数'''

import os


def make_check_count():
    '''闭包，工厂函数'''
    file_count = 0
    file_list = []

    #统计path目录下文件个数
    def check_count(path):
        nonlocal file_count, file_list

        for i in os.listdir(path):
            cur_path = os.path.join(path, i)
            if os.path.isfile(cur_path):
                file_list.append(i)
                file_count += 1
            else:
                check_count(cur_path)
        return file_count,file_list

    return check_count


if __name__ == '__main__':

    path = input('请输入要检索的目录，例如:./数据/工业\n')
    while not os.path.isdir(path):
        path = input('<{}>不是有效目录，请输入要检索的目录，例如:./数据/工业\n'.format(path))

    check_count = make_check_count()
    count,list = check_count(path)
    print('目录 <{}> \n共发现 <{}> 个文件，文件列表如下：\n{}'.format(os.path.abspath(path), count, list))