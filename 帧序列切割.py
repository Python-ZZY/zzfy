#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2020/11/18 12:51 
# @Author : ywy
# @Platform:

from tkinter.filedialog import *
import windnd
from tkinter.messagebox import showerror,showinfo
from PIL import Image
def splitimage(src, rownum, colnum):
    src =src.strip()
    rownum = int(rownum)
    colnum = int(colnum)
    img = Image.open(src)
    w, h = img.size
    if rownum <= h and colnum <= w:
        print('Original image info: %sx%s, %s, %s' % (w, h, img.format, img.mode))
        print('开始处理图片切割, 请稍候...')

        s = os.path.split(src)
        fn = s[1].split('.')
        basename = fn[0]
        ext = fn[-1]
        dstpath=basename
        if not  os.path.exists(dstpath):
            os.makedirs(dstpath)
        num = 0
        rowheight = h // rownum
        colwidth = w // colnum
        for r in range(rownum):
            for c in range(colnum):
                box = (c * colwidth, r * rowheight, (c + 1) * colwidth, (r + 1) * rowheight)
                img.crop(box).save(os.path.join(dstpath, f'{basename}{num+1}.{ext}'), ext)
                num = num + 1
        print('图片切割完毕，共生成 %s 张小图片。' % num)
        return f'图片切割完毕，共生成 {num} 张小图片存放在当前程序目录{dstpath}文件夹下'

    else:
        print('不合法的行列切割参数！')
        return '不合法的行列切割参数！'

root_1 = Tk()
rownum = StringVar()
colnum = StringVar()
rownum.set("1")
colnum.set("13")
z = StringVar()
root_1.title('图片切割')

count = Label(root_1, text='切割行数')
count.grid(row=0, column=0)
enter_1 = Entry(root_1, state='normal', textvariable=rownum,bd=2,width=50)
enter_1.grid(row=0, column=1)

count = Label(root_1, text='切割列数')
count.grid(row=1, column=0)
enter_2 = Entry(root_1, state='normal', textvariable=colnum,bd=2,width=50)
enter_2.grid(row=1, column=1)

def dragged_files(files):
    src =files[0].decode('gbk')
    rownum = enter_1.get()
    colnum = enter_2.get()
    print(src,rownum,colnum)
    if rownum and colnum:
        showinfo('提示',splitimage(src,rownum,colnum))
    else:
        showerror('错误提示','切割行数和切割列数必须有值')


count = Label(root_1, text='拖拽你的图片到窗口')
count.grid(row=2, column=0)
windnd.hook_dropfiles(root_1,func=dragged_files)

root_1.mainloop()

