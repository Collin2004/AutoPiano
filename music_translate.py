import time
import math




MAX_SPEED = 100
NOTE_SECTION_INTERVAL = 0.0
RIGHT_LEFT_INTERVAL = 0.05

SAME_NOTE_INTERVAL = 0.03

CHECK_ENABLE = False

_exit_flag = False
class music_trans():
    def __init__(self, music, beat = 60, note_per = 4, move = 0): # note_per 代表每小节的拍数
        self.music = music       

        self.beat_time = note_per * (60 / beat)  # 60 / beat即一拍的时值，beat_time即每小节的时值
        self.origin_beat = beat                  # origin_beat即初始速度
        self.play_list = []                      # 演奏列表

        self.current_t = 0                       # 当前时刻
        self.speed = MAX_SPEED                   # 最大速度

    

        self._count = 0

        

    def set_beat(self, beat, note_per = 4):
        self.beat_time = note_per * (60 / beat)

#######################################################
    def _reset_t(self):
        self.current_t = 0

    def _rest(self, beat):
        self.current_t += self.beat_time * beat

    def _rest_with_time(self, t):
        self.current_t += t
    def _play(self, tone, speed = MAX_SPEED):                                          # 按下写入，参数：音调，速度
        self.play_list.append([tone, 1, self.current_t, speed])     # 向演奏列表中写入电机编号，按下，时长，速度

    def _stop(self, tone):                                                             # 松开写入
        self.play_list.append([tone, 0, self.current_t, MAX_SPEED])
            
    
    def _play_pedal(self):                                                             #踏板按下
        self.play_list.append(["pedal", 1, self.current_t, MAX_SPEED])

    def _stop_pedal(self):                                                             #踏板松开
        self.play_list.append(["pedal", 0, self.current_t, MAX_SPEED])

######################################################################
    def cal_rest(self, l):
        for i in range(10):
            if l >= math.pow(2, i) and l < math.pow(2, i + 1):
                return math.pow(2,i)

    def music_to_play_table(self):
        last_tone = []
        rest_time = 0
        copy_index_start = None
        check_t = [[], []]                      # music应有的格式
        mmm = 0

        if not isinstance(self.music, list):    # 如果self.music不是list
            self.music = [self.music]           # 将其放入list

        track_idx = 0
        for music_item in self.music:           # 第一次取出右手数据，第二次取出左手数据，均为tuple
            track_idx += 1
            self._reset_t()                     # self.current_t = 0
            self.set_beat(self.origin_beat)     # 设置初始节拍
            self._rest_with_time(RIGHT_LEFT_INTERVAL) # 当前时刻增加一个左右手间隔
            rest_time = 0
            self.speed = 0
            i = 0
            copy_index_start = None
            while i < len(music_item):                    # 处理第i个小节
            # for i in range(len(music_item)):
            
                # 设置踏板
                if track_idx ==1 and i !=0 and i % 2 == 0: 
                    self._play_pedal()
                    self._rest_with_time(0.2)
                    self._stop_pedal()
                    self._rest_with_time(-0.2)

                if isinstance(music_item[i], tuple):      # 如果music_item[i]为tuple
                    for j in range(len(music_item[i])):   # music_item[i]的第j个最小单元（1/16音符),解析1/16节拍
                        chor = music_item[i][j]           # chor接收了第i小节的第j个1/16分音符

                        if "REST" in chor:                # 如果有休止符的声明
                            tmp = eval(chor)
                            rest_time = tmp["REST"]
                            continue
                        elif "NOP" in chor:               # 如果有     的声明
                            tmp = eval(chor)
                            self._rest(tmp["NOP"])        # self.current_t += self.beat_time * beat

                            continue
                        elif "BEAT" in chor:              # 如果有速度的声明
                            tmp = eval(chor)
                            self.set_beat(tmp["BEAT"])
                            continue
                        
                        elif "COPY_START" in chor:        # 如果有     的声明
                            copy_index_start = i+1
                            continue
                        elif "COPY_STOP" in chor:         # 如果有     的声明
                            if copy_index_start != None:      
                                if not CHECK_ENABLE:                      
                                    i = copy_index_start
                                    i -= 1
                                copy_index_start = None
                            continue
                        elif "SPEED" in chor:            # 如果有     的声明
                            tmp = eval(chor)
                            self.speed = tmp["SPEED"]
                            continue
                        elif "=" in chor:                # 如果有 '=' 
                            tmp = chor.split("=")        # 以'='为分隔符分割
                            t = eval(tmp[1])


                            chors_all = tmp[0].split(":")            # 以':'为分隔符分割
                            for tc in chors_all:
                                chors = tc.split(",")                # 以','为分隔符分割
                                for item in chors:
                                    self._play(item, self.speed)
                                self._rest(t)
                                for item in chors:
                                    self._stop(item)
                            continue                            

                        if chor != '-':                                # - 代表这个节拍无变化
                            chors = chor.split(",")                    # 以','为分隔符分割，分开单手同时按下的音调
                            for item in last_tone:                     # 抬起需要停止的音符
                                self._stop(item)

                            last_tone = []
                            ##########################
                            for m in range(len(chors)):             
                                chors[m] = chors[m].replace("&", ",")  # 把该音调中的'&'替换为','

                                if '{' in chors[m]:
                                    temp = eval(chors[m])
                                    for key in temp:
                                        if isinstance(temp[key], list):
                                            self._rest_with_time(temp[key][0])
                                            self._play(key, self.speed)
                                            self._rest(temp[key][1])
                                            self._rest_with_time(-temp[key][0])
                                            self._stop(key)
                                            self._rest(-temp[key][1])
                                        else: 
                                            self._play(key, self.speed)
                                            self._rest(temp[key])
                                            self._stop(key)
                                            self._rest(-temp[key])
                                else:
                                    self._play(chors[m], self.speed)
                                    last_tone.append(chors[m])
                        if rest_time == 0:
                            self._rest(1 / self.cal_rest(len(music_item[i])))
                        else:
                            self._rest(rest_time)

                    self._rest_with_time(NOTE_SECTION_INTERVAL)
                    check_t[mmm].append([i,round(self.current_t, 1)])
                else:
                    print("error", i, music_item[i])

                i = i + 1

            mmm += 1
        if CHECK_ENABLE:
            self._check_show(check_t[0], check_t[1])
        self.play_list_sort()

    def _check_show(self, r, l):
        if len(r) != len(l):
            print("right and left section not the same, right:{}, left:()".format(len(r),len(l)))
            return

        for i in range(len(r)):
            if abs(r[i][1] - l[i][1]) > 0.001:
                print("time not sync, section:{}, notes:{}".format(i, self.music[0][i]))

    def _sort_by_time(self, play_list):                   # 按时间排序
        _play_list = play_list.copy()                     # play_list复制给_play_list
        ret_list = []
        while _play_list != []:
            current_index = 0
            min_t = 100000
            for i in range(len(_play_list)):              # 取出整个演奏列表中最小的时值赋给min_t，对应操作的下标赋给current_index
                if _play_list[i][2] < min_t:                
                    min_t = _play_list[i][2]                
                    current_index = i                       
            ret_list.append(_play_list[current_index])    # ret_list存有排好顺序的操作
            del _play_list[current_index]                 # 从_play_list中删除时值最短的操作

        # 将同一时间操作的音符放在一个list中
        temp_list1 = []
        temp_list2 = []
        i = 0
        while i < len(ret_list):
            temp_list2 = [ret_list[i]]
            if i == len(ret_list) - 1:
                temp_list1.append(temp_list2)
                break

            k = i
            for j in range(i + 1, len(ret_list)):
                if math.fabs(ret_list[j][2] - ret_list[k][2]) < 0.0001:   # 如果时值近似相等
                    temp_list2.append(ret_list[j])                        # 将与之时值相等的音符添加到同一列表中
                    i += 1  
                else:
                    i += 1
                    break
            temp_list1.append(temp_list2)
        return temp_list1                                                 # 返回的是同一时间都在一个列表里的操作

    def play_list_sort(self):
        temp_list1 = self._sort_by_time(self.play_list)
        # 两个连续的相同音符需要单独处理，否则将不会抬起，只有一个声音
        for i in range(1, len(temp_list1)):                 # 抽取了同一时刻的列表
            t_ret = self._check_special(temp_list1[i])      # t_ret获取了存有相同音符索引的列表
            if t_ret != []:
                for l in range(len(temp_list1[i])):
                    if l in t_ret:                          # 把相同的处理分开了SAME_NOTE_INTERVAL时长
                        if temp_list1[i][l][1] == 1:
                            temp_list1[i][l][2] += SAME_NOTE_INTERVAL
                        else:
                            temp_list1[i][l][2] -= SAME_NOTE_INTERVAL
                    else:
                        temp_list1[i][l][2] += 0.0

        temp = []
        for item in temp_list1:
            for item2 in item:
                temp.append(item2)

        self.play_list = self._sort_by_time(temp)

    def _check_special(self, item):
        ret = []
        for i in range(len(item)):
            for j in range(i + 1, len(item)):
                if item[i][0] == item[j][0]:
                    ret.append(i)
                    ret.append(j)
        return ret
    def play_music(self):
        play_list = self.play_list

        for i in range(len(play_list)):
            print(play_list[i])