# -*- coding: utf-8 -*-

import os
import numpy as np
import cv2.cv2 as cv
from matplotlib import pyplot as plt
import heapq
import math

imgcol = 4
imgrow = 5

isEquels = False

#二值化处理
def thresh_binary(img):
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (9, 9), 0)
    # OTSU's binaryzation
    (ret3, th3) = cv.threshold(blur,50, 255, cv.THRESH_OTSU)
    kernel = cv.getStructuringElement(cv.MORPH_RECT,(5, 5))
    opening = cv.morphologyEx(th3, cv.MORPH_OPEN, kernel)
    #看看有几个非零像素
    # cv.namedWindow("Image",0)
    # cv.imshow("Image", opening)
    return opening

# sum the black pixel numbers in each cols
def hist_col(img):
    list=[]
    row, col = img.shape
    for i in xrange(col):
        list.append((img[:, i] < 200).sum())
    return list

#纵向切图的坐标
def cut_col(img,l):
    minlist = []
    np_list = np.array(l)
    
    row, col = img.shape
    avg = col/(imgcol+1)
    if(cv.countNonZero(img) < col*row/2): #黑底子白字
        a = max(l)
        i = 20
        while i < col - 1:
            if i >= col - 11:
                if np_list[i] > a - 10 and np_list[i] <= np_list[i+1:col].min():
                    minlist.append(i)
                    break
                if i == col - 1:
                    minlist.append(i)
                    break
            else:
                if np_list[i] > a - 10 and np_list[i] <= np_list[i:i+5].min():
                    if len(minlist) == 0:
                        minlist.append(i)
                    else:
                        x = 0
                        y = 1
                        while i+x < col-10 and np_list[i+x] >= a-10:
                            x += 3
                        while np_list[i-y] >= a-10:
                            y += 1
                        minlist.append(i+x/2-y/2) 
                    i += avg
            i += 1
        return (minlist,row)
    else:  #白底黑字
        i = 20
        a = min(l)
        while i < col - 1:
            if i >= col - 11:
                if np_list[i] < a +10 and np_list[i] <= np_list[i+1:col].min():
                    minlist.append(i)
                    break
                if i == col - 1:
                    minlist.append(i)
                    break
            else:
                if np_list[i] < a + 10 and np_list[i] <= np_list[i:i+5].min():
                    if len(minlist) == 0:
                        minlist.append(i)
                    else:
                        x = 0
                        y = 1
                        while i+x < col-10 and np_list[i+x] <= a+10:
                            x += 3
                        while np_list[i-y] <= a+10:
                            y += 1
                        minlist.append(i+x/2-y/2) 
                    i += avg
            i += 1
        return (minlist,row)

#切竖着的图并接着处理
def cut_img(img,minlist,row,filename):
    colpics = []

    for j in xrange(len(minlist)-1):
        # cv.namedWindow(str(j),0)
        # cv.imshow("F:\\test\\lie\\"+filename+str(j)+"lie.jpg", img[0:row, minlist[j]:minlist[j+1]])
        if minlist[j+1] - minlist[j] >= minlist[-1]/imgcol * 1.8:
            cha = minlist[j+1] - minlist[j] 
            chu = cha/(minlist[-1]/imgcol*1.0)
            ss = sishewuru(chu)
            zhong = cha / ss
            if isEquels:
                cv.imwrite("F:\\test\\lie\\"+filename+"-"+str(j)+"lie.jpg", img[0:row, minlist[j]:minlist[j+1]].copy())
            else:
                #处理等距字段
                for i in xrange(ss):
                    colpics.append(img[minlist[j]+i*zhong:minlist[j]+(i+1)*zhong])
                    cv.imwrite("F:\\test\\lie\\"+filename+"-"+str(j)+"~"+str(i)+"-"+"lie.jpg", img[0:row, minlist[j]+i*zhong:minlist[j]+(i+1)*zhong].copy())
        else:
            cv.imwrite("F:\\test\\lie\\"+filename+"-"+str(j)+"lie.jpg", img[0:row, minlist[j]:minlist[j+1]].copy())
            colpics.append(img[0:row, minlist[j]:minlist[j+1]])
    return colpics

#横着的坐标算一下
def hist_row(img):
    img = thresh_binary(img.copy())
    list=[]
    row, col = img.shape
    for i in xrange(row):
        list.append((img[i, :] < 200).sum())
    return cut_row(img, list)

#四舍五入
def sishewuru(swr):
    if swr - int(swr) >= 0.5:
        return int(swr)+1
    else:
        return int(swr)


# 定点横着的坐标
def cut_row(img, row_list):
    print (row_list)
    
    minlist = []
    # single_images_with_rect = []
    row, col = img.shape
    np_list = np.array(row_list)
    
    avg = row/(imgrow)
    i = 0
    if(cv.countNonZero(img) < col*row/2): #黑底子白字
        a = max(row_list)
        while i < row:
            if i >= row - 20:
                if np_list[i] > a - 5 and np_list[i] <= np_list[i+1:row].min():
                    minlist.append(row)
                    break
                if i == row - 1:
                    minlist.append(i)
                    break 
            elif np_list[i] >= a-3 and np_list[i] <= np_list[i:i+15].min():
                if len(minlist) == 0:
                    minlist.append(i)
                else:
                    x = 0
                    y = 1
                    while np_list[i+x] >= a-3 and i+x < row-10:
                        x += 5
                    while np_list[i-y] >= a-3:
                        y += 1
                    minlist.append(i+x/2-y/2) 
                i += avg
            i += 1   
    else:
        a = min(row_list)
        while i < row:
            aa = np_list[i]
            if i >= row - 20:
                if np_list[i] < a + 5 and np_list[i] <= np_list[i+1:row].min():
                    minlist.append(row)
                    break
                if i == row - 1:
                    minlist.append(i)
                    break 
            elif np_list[i] <= a+3 and np_list[i] <= np_list[i:i+15].min():
                if len(minlist) == 0:
                    minlist.append(i)
                else:
                    x = 0
                    y = 1
                    while np_list[i+x] <= a+3 and i+x < row-10:
                        x += 5
                    while np_list[i-y] <= a+3:
                        y += 3
                    minlist.append(i+x/2-y/2) 
                i += avg
            i += 1
    
    if row - minlist[-1] > 0.4*avg:
        minlist.append(row)
    print minlist
    return (minlist,col)

#切横着的图
def single_cut(img,minlist,col,name):
    rowpics = []
    for j in xrange(len(minlist)-1):
        # uu = minlist[j] if j == 0 else minlist[+20]
        if minlist[j+1] - minlist[j] >= minlist[-1]/imgrow * 1.8:
            cha = minlist[j+1] - minlist[j]
            chu = cha/(minlist[-1]/imgrow*1.0)
            ss = int(round(chu))
            zhong = cha / ss
            if isEquels:
                cv.imwrite("F:\\test\\danzi\\"+name+"-"+str(j)+".jpg", img[minlist[j]:minlist[j+1],0:col].copy())
            else:
                for i in xrange(ss):
                    cv.imwrite("F:\\test\\danzi\\"+name+"-"+str(j)+"~"+str(i)+".jpg", img[minlist[j] +i*zhong:minlist[j] + (i+1)*zhong,0:col].copy())
        else:
            cv.imwrite("F:\\test\\danzi\\"+name+"-"+str(j)+".jpg", img[minlist[j]:minlist[j+1],0:col].copy())

#切二级图
def qietu1(filestr):
    for root, dirs, files in os.walk(filestr):
        for file in files:
            filename = os.path.join(root,file)
            img1 = cv.imread(filename)
            mlis = hist_row(img1)
            single_cut(img1,mlis[0],mlis[1],file.split(".")[0])

            # row,col,_ = img.shape
            # ehight = row/imgrow
            # for i in xrange(imgrow-1):
            #     ii = img[i*ehight:(i+1)*ehight,0:col]
            #     cv.imwrite("F:\\test\\danzi\\"+file.split(".")[0]+"-"+str(i)+'.jpg', ii.copy())

#切一级图
def qietu(filestr):
    dir = filestr
    for root, dirs, files in os.walk(dir):
        for file in files:
            filename = os.path.join(root,file)
            print filename
            img = cv.imread(filename)
            # cv.namedWindow(filename,0)
            # cv.imshow(filename, img)
            a = thresh_binary(img)
            lists = hist_col(a)
            l = cut_col(a,lists)
            colpics = cut_img(img,l[0],l[1],file.split(".")[0])
    
        cv.waitKey(0)
        cv.destroyAllWindows()

if __name__=='__main__':
    # qietu(r'F:/test/src2')
    qietu1(r'F:/test/lie')
    print "完成"
    