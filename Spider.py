import requests
from hashlib import md5
from urllib.parse import urlencode
from requests import codes
import os
from multiprocessing.pool import Pool


def get_page(offset):
    base_url = 'https://www.toutiao.com/search_content/?'
    parameter = {
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '3',
        'from': 'gallery'
    }
    #使用字典的形式来构造参数，有一个好处就是可以方便的更改其中参数，增强代码的健壮性
    url = base_url+urlencode(parameter)  #get请求是直接将参数带在链接里去请求的
    response = requests.get(url)  #get请求一般使用requests库，requests使用起来比较便利，而已requests功能比较强大
    # 每个容易出现程序错误的地方，最好加异常处理，这样程序不会轻易挂掉
    try:
        if codes.ok == response.status_code:
            print('获取源码成功')
            return response.json()
    except requests.ConnectionError:
        print("请求失败")
        return None


def get_image(json):
    if json.get('data'):
        data = json.get('data')
        # data是一个列表的形式，里面的一个元素就是一个数据表，所以需要遍历
        for item in data:
            title = item.get('title') #json形式提取数据比较方便，不用xpath或者正则就能方便准确的提取所需要的数据
            image_list = item.get('image_list')
            for image in image_list:
                image_url = 'https:' + image.get('url')
                yield {
                    'title': title,
                    'image': image_url
                }
                #每一个链接和一个title就返回一个生成器，类似json格式，这样在下一步处理中也很便利


def save_image(item):
    file_path = 'image' + os.path.sep + item.get('title')
    #os.path.sep是文件路径中的分隔符，因为windows和linux中的分隔符是不同的，这样就可以在win上开发libux上跑了
    if not os.path.exists(file_path): #因为上一个函数是返回一个链接一个生成器，而一个文件下有多张图片，所以需要加一个判断，因为若是文件夹已存在，创建就会出错
        os.makedirs(file_path)
    url = item.get('image').replace('list', 'origin') #将小图构造成原图，一般可以通过修改像素就能实现
    try:
        response = requests.get(url)
        if codes.ok == response.status_code:
            file_name = file_path + os.path.sep + '{file_name}.{file_suffix}'.format(file_name=md5(response.content).hexdigest(),file_suffix='jpg')
            # 根据返回的字节随机生成一串16进制的数字来命名图片，可以避免重复
            with open(file_name, 'wb') as f:
                f.write(response.content) #图片文件类型就是字节类型，所以以字节的形式写入
                print('写入图片成功')
    except requests.ConnectionError:
        print('Failed to Save Image，item %s' % item)


def main(offset):
    json = get_page(offset)
    for item in get_image(json):
        save_image(item)


Group_start = 0
Group_end = 8 #循环执行8次，也就是翻8次页

if __name__ == '__main__':
    pool = Pool()
    groups = ([x*20 for x in range(Group_start, Group_end+1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
