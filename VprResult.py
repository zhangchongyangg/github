#!/bin/env python
#encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')#这三行主要是解决输出中文乱码问题
truespeaker_score_file = "true.txt"#存放结果文件名
imposter_score_file = "imp.txt"#存放结果文件名
truespeaker_score=[]#定义一个list列表 对应 vector 数组
imposter_score=[]#定义一个list列表 对应 vector 数组
map_wavID_text={}#定义一个字典  对应C++ Map
map_verifyID_userID = {}#定义一个字典 对应C++ Map
SCORE=float(sys.argv[3])
#print ("SCORE = %" % SCORE)
def splitString(str,separator):
    substrs = []
    index1 = 0
    index2 = 0
    index2 = str.find(separator, index1)
    temp = ""
    while index2 < len(str):
        temp = str[index1:index2 - index1]
        index1 = index2 + 1
        index2 = str.find(separator, index1)
        if not temp:
            continue
        else:
            substrs.append(temp)
def load_vpr_map(file_path):
    try:
        f = open(file_path,"r")#打开文件，如果没有 会抛出异常
	#print(f)
    except:
        print file_path + " open failed!"
        return False
    for line in f.readlines():#获取到文件句柄后，一次把所有的内容按行获取出来，并存储到一个list中
        line = line.strip("\n").strip("\r")#去掉换行符
	#print(line)
        if not line:#如果没有获取到内容 就继续下一行
            continue
        #substrs = splitString(line, '\t')
        substrs = line.split("\t")#根据tab 进行分割字符串，并存放到一个 list中
        #print(substrs)
        if not substrs:
            print  "load vpr map failed! line info = " + line
            return False
        else:
            user_id = substrs[0]#获取list第一个
	    #print(user_id)
            #print substrs
            #print substrs[1].split("\t")
            #for i in substrs[1].split("\t"):
            for i in substrs[1:]:#[1:] 是python切片操作，获取从第二个开始 一直到最后一个元素
                #print i
                map_verifyID_userID[i] = user_id
                #print(map_verifyID_userID[i])
    f.close()#关闭文件句柄
    #print "over load_vpr_map " + file_path
    return True

def more_bigger(a, b):
    return  1 if a>b else 0#推导式，  如果 if 为 True， 那么就取前面的，如果为False 就取else后面的

def load_vpr_result(file_path):
    try:
        f = open(file_path,"r")
    except:
        print file_path + " open failed!"
        return False
    file = open("truespeaker_score_file","w")
    file2 = open("imposter.score","w")
    for line in f.readlines():
        line = line.strip("\n").strip("\r")
        tmp = line.split("\t")#切分转成list
        user_id = tmp[0]#获取list第一个元素
        verify_id = tmp[1]#获取第二个
        try:
            score = float(tmp[2])#获取第三个
        except:
            pass
        if verify_id not in map_verifyID_userID:# xx not in yy 意思是 xx 不在yy这个字典中，类似C++ key不在map中一样
            #print "vpr test result: verify id " + verify_id + " is not exist."
            continue
        else:
            if user_id == map_verifyID_userID[verify_id]:
                file.write("%s\t%s\t%s\n" %(score,user_id,verify_id))#写文件操作
                truespeaker_score.append(score)#list追加操作，在末尾追加元素
            else:
                file2.write("%s\t%s\t%s\n" %(score,user_id,verify_id))
                imposter_score.append(score)
    print "All the test cases is a total of %s" %(len(truespeaker_score) + len(imposter_score))
    file.close()
    file2.close()
    f.close()
    truespeaker_score.sort()#正序输出
    imposter_score.sort(reverse=True)#逆序输出
    return True


def load_asr_map(file_path):
    try:
        f = open(file_path, "r")
    except:
        print file_path + " open failed!"
        return False
    for line in f.readlines():
        line = line.strip("\n").strip("\r")
        tmp = line.split("\t")
        wav_id = tmp[0]
        text = tmp[1]
        map_wavID_text[wav_id] = text
    print  "All the asr test wav counts is a total of"  + str(len(map_wavID_text))
    f.close()
    return True

def load_asr_result(file_path):
    try:
        f = open(file_path, "r")
    except:
        print file_path + " open failed!"

    asr_right = 0
    asr_wrong = 0
    wav_id = ""
    wav_text = ""
    for line in f.readlines():
        line = line.strip("\n").strip("\r")
        tmp = line.split("\t")
        wav_id = tmp[0]
        wav_text = tmp[1]
        if wav_id not in map_wavID_text:
            print "asr test result: wav id " +  wav_id + " is not exist."
        else:
            if map_wavID_text[wav_id] == wav_text:
                asr_right += 1
            else:
                asr_wrong += 1

    print "SER = " + str((100.0*asr_wrong) / (asr_right + asr_wrong)) + "%"
    f.close()
    return True

def calcFAR_FRR():

    #print ("calcFAR_FRR_SCORE = %" % SCORE)
    FR_count = 0
    FA_count = 0
    for i in truespeaker_score:
	#print ("SCORE_FOR= %" % SCORE)
        if i < SCORE:
            FR_count += 1
        else:
            break
    for i in imposter_score:
        if i >= SCORE:
            FA_count += 1
        else:
            break
    print "当阈值为%.2f时,"%SCORE
    print "FAR = %.3f"% ((100.0*FA_count) / len(imposter_score)) + "%"
    print "FRR = %.3f"% ((100.0*FR_count) / len(truespeaker_score)) + "%"

def calc_far_frr_with_threshold(threshold):
    frr_count = 0
    far_count = 0
    for i in truespeaker_score:
        if (i < threshold):
            frr_count += 1
        else:
            break
    for i in imposter_score:
        if (i >= threshold):
            far_count += 1
        else:
            break
    far = (100.0*far_count) / len(imposter_score)
    frr = (100.0*frr_count) / len(truespeaker_score)
    return (far,frr)

def abs_double(d):
    return  d if d > 0 else -d

def calcEER():
    if (len(truespeaker_score) < 10 or len(imposter_score) < 10):
        print "data is too less to calc EER"
        return False


    min_trueSpk = min(truespeaker_score)
    max_impSpk = max(imposter_score)
    if (min_trueSpk > max_impSpk):
        print "EER = 0.00% ,Threshold = (" + str(max_impSpk) + ", " + str(min_trueSpk) + ")"
        return True
    vec_far_frr = []
    diff_far_frr = []
    for i  in truespeaker_score:
        (far,frr) = calc_far_frr_with_threshold(i)
        vec_far_frr.append((far, frr))
        diff_far_frr.append(abs_double(far - frr))
    minnum = diff_far_frr[0]
    index = 0
    count = 0
    for i in diff_far_frr[1:]:
        count += 1
        if (minnum > i):
            minnum = i
            index = count
    print("\r")
    print  "EER = %.3f" % vec_far_frr[index][0] + "%, Threshold = " + str(truespeaker_score[index])
    return True

if __name__ == '__main__':
    import sys
    if (len(sys.argv) != 4 and len(sys.argv) != 6):
        print "VPR/ASR performance statistic, calculate EER,FAR,FRR for VPR, calculate SER for ASR."
        print "Usage:" + sys.argv[0] +  " <vpr_map> <vpr_result> <asr_map> <asr_result>"
        print  "\tvpr_map : create by confuse_wav_tool"
        print  "\tvpr_result : create by vpr_test_tool"
        print  "\tasr_map : create by confuse_wav_tool"
        print "\tasr_result : create by asr_test_tool"
	print "\tthreshold: the score of threshole"
        sys.exit()
    print  "VPR Performance Statistic:"
    if not load_vpr_map(sys.argv[1]) or not load_vpr_result(sys.argv[2]):
        if (len(sys.argv) == 6):
            sys.exit()
    else:
        calcFAR_FRR()
        calcEER()
    if len(sys.argv) == 6:
        print "ASR Performance Statistic:"
        if not load_asr_map(sys.argv[3]) or not load_asr_result(sys.argv[4]):
            sys.exit()
