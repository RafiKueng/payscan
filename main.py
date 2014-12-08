# -*- coding: utf-8 -*-
"""
Created on Sat Dec  6 16:57:01 2014

@author: rafik
"""

import numpy as np
import cv2
import cv2.cv as cv

from PIL import Image
import sys

import pyocr
import pyocr.builders

#import pyperclip

cap = cv2.VideoCapture(1)



tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
tool = tools[0]
print("Will use tool '%s'" % (tool.get_name()))
# Ex: Will use tool 'tesseract'

langs = tool.get_available_languages()
print("Available languages: %s" % ", ".join(langs))

if 'eng' in langs:
    lang = 'eng'
else:
    lang = langs[0]

print("Will use lang '%s'" % (lang))

builder = pyocr.builders.TextBuilder()
builder.tesseract_configs.append('bank')



print "init"
print "test"



def getText(frame):

    img = Image.fromarray(frame)

    txt = tool.image_to_string(img,
                           lang=lang,
                           builder=builder)
    
#    word_boxes = tool.image_to_string(img,
#                                      lang=lang,
#                                      builder=pyocr.builders.WordBoxBuilder())
#
#    line_and_word_boxes = tool.image_to_string(
#            img, lang=lang,
#            builder=pyocr.builders.LineBoxBuilder())
#    
#    # Digits - Only Tesseract
#    digits = tool.image_to_string(img,
#                                  lang=lang,
#                                  builder=pyocr.tesseract.DigitBuilder())
                                  
#    return (txt, word_boxes, line_and_word_boxes, digits)
    return txt

def cleanText(a):
    texts = [_.replace(' ','') for _ in a.split('\n')]
    if len(texts)==1:
        return texts[0]
    if len(texts)==0:
        return ''
    tl = [(len(_), _) for _ in texts]
    if len(tl)==0:
        return ''
    l, t = max(tl)
    #print 'tl:', tl

    return str(t)


saved = []
for i in range(52):
    saved.append({'?':3})
saved[13]['>'] = 99
saved[41]['+'] = 99
saved[51]['>'] = 99

        
def intelSave(a):

    offs1 = -1
    offs2 = -1
    offs3 = -1

    l = len(a)
    
    ch = [' ']*52

    p = a.find('>')
    if p>=0:
        if p < len(a)-1:
            offs1 = 13-p
        else:
            offs1 = 51-p


    p = a.find('>',p+1)
    if p>=0:
        if p < len(a)-1:
            pass #some error, second < should be at end            
            #offs2 = 13-p
        else:
            offs2 = 51-p


    p = a.find('+')
    if p>=0:
        offs3 = 41-p
    
    offs = max(offs1, offs2, offs3)
    
    if offs>=0:
        for i in range(0,l):
            try:
                saved[i+offs][a[i]] += 1
                ch[i+offs] = a[i]
            except KeyError:
                saved[i+offs][a[i]] = 1
                ch[i+offs] = a[i]
        
    
    
    
    
    res = []
    rat = []
    for i in range(52):
        srt = sorted(saved[i].items(), key=lambda x: x[1], reverse=True)
#        print 'srt:', srt
        res.append(srt[0][0])
        try:
            r = 1.0 * srt[1][1] / srt[0][1] # ratio between counts of accepted to next possible solution
            if srt[0][0]=='?':
                r = 1.0
        except IndexError:
            r = 1.0
        rat.append(r)
        
    res = ''.join(res)
    ch = ''.join(ch)
    
    
#    print '-----\nres:'
#    print a
#    if p>=0:
#        print ' '*p + '^'
#    else:
#        print 'XXX'
#    print res
#    print ch
#    print 'offsets:', offs1, offs2, offs3
#    print '-----'

    return (res, rat)


def pruefziffer(zahl):
    
    key = [0,9,4,6,8,2,7,1,3,5]
    
    nd = len(str(zahl))
    ueb = 0
    
    for e in reversed(range(nd)):
        z = zahl // 10**e
        ueb = key[(z+ueb)%10]
        
    return (10-ueb)%10
        


def main():    
    i=0
    aa = 43
    bb = 2
    cc = 3

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        #print i
        
        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY,aa,bb)
        blur = cv2.GaussianBlur(thresh,(cc,cc),0)        
        img = blur    


        #blur = cv2.GaussianBlur(gray,(5,5),0)
        #ret3,th3 = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        #img = th3

    
        # Display the resulting frame
        cv2.imshow('frame',img)
        if i%1==0:
            a = getText(img)
#            print 'ocr:', a[0]
#            print 'ocr:', a[1]
#            print 'ocr:', a[2]
            a = cleanText(a)
            res, ret = intelSave(a)

            stat = ['_','_','_','-','_']

            try:
                p1 = pruefziffer(int(res[0:12]))
                p2 = int(res[12])
                pz = p1==p2
                stat[2] = 'X'
            except ValueError:
                pz = False
                pass

            if max(ret)<0.50:
                py = True
                stat[1] = 'X'
            else:
                py = False
                
            if res.find('?')>=0:
                px = False
            else:
                px = True
                stat[0] = 'X'

            if res == '0100000100602>993899481455697700005092815+010275154>':
                stat[4]='X'

                
            print '(a:%02i b:%02i c:%02i)' % (aa,bb,cc),
#            print 'stat:',''.join(stat),
#            print a
#            print ' >> ', ' '.join([' %s  ' % _ for _ in res])
#            print ' >> ', ' '.join(['%3.2f' % _ for _ in ret])
                
            print res, 
            print ''.join(['^' if v>=0.5 else ' ' for v in ret]), ''.join(stat)
        
        if px and py and pz:
            break
        
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('a'):
            aa += 2
        elif key == ord('z'):
            aa -= 2
        elif key == ord('s'):
            bb += 1
        elif key == ord('x'):
            bb -= 1
        elif key == ord('d'):
            cc += 2
        elif key == ord('c'):
            cc -= 2
            
        
    
        i +=1
    
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
    for i in range(52):
        print sorted(saved[i].items(), key=lambda x: x[1], reverse=True)
    
    rres = res[0:42] + ' ' + res[42:]    
    
    print 'the result is (correct? %s):' % stat[4]
    print rres
    print 'copied tot clipboard'
    import pyperclip    
    pyperclip.copy(rres)


if __name__ == '__main__':
    main()