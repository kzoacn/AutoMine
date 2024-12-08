import time
import mouseOperation
import random

import imageProcess
import cv2
import numpy
import time
import copy

SMALL_TIME = 0.05
MEDIUM_TIME = 1

class BoomMine:
    __inited = False
    blocks_x, blocks_y = -1, -1
    width, height = -1, -1
    img_cv, img = -1, -1
    blocks_img = [[-1 for i in range(blocks_y)] for i in range(blocks_x)]
    blocks_num = [[-3 for i in range(blocks_y)] for i in range(blocks_x)]
    blocks_is_mine = [[0 for i in range(blocks_y)] for i in range(blocks_x)]
    steps = 0

    is_new_start = True

    next_steps = []

    @staticmethod
    def rgb_to_bgr(rgb):
        return rgb[2], rgb[1], rgb[0]

    @staticmethod
    def equal(arr1, arr2):
        if arr1[0] == arr2[0] and arr1[1] == arr2[1] and arr1[2] == arr2[2]:
            return True
        return False

    def is_in_form(self, location):
        x, y = location[0], location[1]
        if x < self.left or x > self.right or y < self.top or y > self.bottom:
            return False
        return True

    def iterate_blocks_image(self, func):
        if self.__inited:
            for y in range(self.blocks_y):
                for x in range(self.blocks_x):
                    # args are: self, [0]singleBlockImage, [1]location(as an array)
                    func(self, self.blocks_img[x][y], (x, y))

    def iterate_blocks_number(self, func):
        if self.__inited:
            for y in range(self.blocks_y):
                for x in range(self.blocks_x):
                    # args are: self, [0]singleBlockNumber, [1]location(as an array)
                    func(self, self.blocks_num[x][y], (x, y))

    def round_color(self,c,lst=[0,128,192,255]):
        ans = 0
        mn = 9999
        for x in lst:
            if abs(c-x) < mn:
                mn = abs(c-x)
                ans = x
        return ans 
    def round_c(self,c):
        #print(list(c))
        #print('begin')
        cc = list(c)
        #print(cc)
        new_c = [self.round_color(cc[0]),self.round_color(cc[1]),self.round_color(cc[2])]
        return new_c
    def analyze_block(self, block, location):
        x, y = location[0], location[1]
        now_num = self.blocks_num[x][y]

        # if 1:
        if not now_num == -2 and not 0 < now_num < 9:

            block = imageProcess.pil_to_cv(block)
            block_color = block[8, 8]
            
            block_color = self.round_c(numpy.asarray(block_color))
            # -1:Not opened
            # -2:Opened but blank
            # -3:Un initialized
            gray1 = self.rgb_to_bgr((192, 192, 192))
            # Opened
            if self.equal(block_color, gray1):
                if not self.equal(self.round_c(numpy.asarray(block[8, 1])), self.rgb_to_bgr((255, 255, 255))):
                    self.blocks_num[x][y] = -2
                    self.is_started = True
                else:
                    self.blocks_num[x][y] = -1

            elif self.equal(block_color, self.rgb_to_bgr((0, 0, 255))):
                self.blocks_num[x][y] = 1

            elif self.equal(block_color, self.rgb_to_bgr((0, 128, 0))):
                self.blocks_num[x][y] = 2

            elif self.equal(block_color, self.rgb_to_bgr((255, 0, 0))):
                self.blocks_num[x][y] = 3

            elif self.equal(block_color, self.rgb_to_bgr((0, 0, 128))):
                self.blocks_num[x][y] = 4

            elif self.equal(block_color, self.rgb_to_bgr((128, 0, 0))):
                self.blocks_num[x][y] = 5

            elif self.equal(block_color, self.rgb_to_bgr((0, 128, 128))):
                self.blocks_num[x][y] = 6

            elif self.equal(block_color, self.rgb_to_bgr((0, 0, 0))):
                if self.equal(self.round_c(numpy.asarray(block[6, 6])), self.rgb_to_bgr((255, 255, 255))):
                    # Is mine
                    self.blocks_num[x][y] = 9
                elif self.equal(self.round_c(numpy.asarray(block[5, 8])), self.rgb_to_bgr((255, 0, 0))):
                    # Is flag
                    self.blocks_num[x][y] = 0
                else:
                    self.blocks_num[x][y] = 7

            elif self.equal(block_color, self.rgb_to_bgr((128, 128, 128))):
                self.blocks_num[x][y] = 8
            else:
                self.blocks_num[x][y] = -3
                self.is_mine_form = False

            if self.blocks_num[x][y] == -3 or not self.blocks_num[x][y] == -1:
                self.is_new_start = False
            
            #print(x,y,block_color,self.blocks_num[x][y])

    def detect_mine(self, block, location):

        def generate_kernel(k, k_width, k_height, block_location):
            ls = []
            loc_x, loc_y = block_location[0], block_location[1]
            for now_y in range(k_height):
                for now_x in range(k_width):

                    if k[now_y][now_x]:
                        rel_x, rel_y = now_x - 1, now_y - 1
                        ls.append((loc_y + rel_y, loc_x + rel_x))
            return ls

        def count_unopen_blocks(blocks):
            count = 0
            for single_block in blocks:
                if self.blocks_num[single_block[1]][single_block[0]] == -1:
                    count += 1
            return count

        def mark_as_mine(blocks):
            for single_block in blocks:
                if self.blocks_num[single_block[1]][single_block[0]] == -1:
                    self.blocks_is_mine[single_block[1]][single_block[0]] = 1

        x, y = location[0], location[1]

        if self.blocks_num[x][y] > 0:

            kernel_width, kernel_height = 3, 3

            # Kernel mode:[Row][Col]
            kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]

            # Left border
            if x == 0:
                for i in range(kernel_height):
                    kernel[i][0] = 0

            # Right border
            if x == self.blocks_x - 1:
                for i in range(kernel_height):
                    kernel[i][kernel_width - 1] = 0

            # Top border
            if y == 0:
                for i in range(kernel_width):
                    kernel[0][i] = 0

            # Bottom border
            if y == self.blocks_y - 1:
                for i in range(kernel_width):
                    kernel[kernel_height - 1][i] = 0

            # Generate the search map
            to_visit = generate_kernel(kernel, kernel_width, kernel_height, location)

            unopen_blocks = count_unopen_blocks(to_visit)
            if unopen_blocks == self.blocks_num[x][y]:
                mark_as_mine(to_visit)

    def detect_to_click_block(self, block, location):

        def generate_kernel(k, k_width, k_height, block_location):
            ls = []
            loc_x, loc_y = block_location[0], block_location[1]
            for now_y in range(k_height):
                for now_x in range(k_width):

                    if k[now_y][now_x]:
                        rel_x, rel_y = now_x - 1, now_y - 1
                        ls.append((loc_y + rel_y, loc_x + rel_x))
            return ls

        def count_mines(blocks):
            count = 0
            for single_block in blocks:
                if self.blocks_is_mine[single_block[1]][single_block[0]] == 1:
                    count += 1
            return count

        def mark_to_click_block(blocks):
            for single_block in blocks:

                # Not Mine
                if not self.blocks_is_mine[single_block[1]][single_block[0]] == 1:

                    # Click-able
                    if self.blocks_num[single_block[1]][single_block[0]] == -1:

                        # Source Syntax: [y][x] - Converted
                        if not (single_block[1], single_block[0]) in self.next_steps:
                            self.next_steps.append((single_block[1], single_block[0]))

        x, y = location[0], location[1]

        if block > 0:

            kernel_width, kernel_height = 3, 3

            # Kernel mode:[Row][Col]
            kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]

            # Left border
            if x == 0:
                for i in range(kernel_height):
                    kernel[i][0] = 0

            # Right border
            if x == self.blocks_x - 1:
                for i in range(kernel_height):
                    kernel[i][kernel_width - 1] = 0

            # Top border
            if y == 0:
                for i in range(kernel_width):
                    kernel[0][i] = 0

            # Bottom border
            if y == self.blocks_y - 1:
                for i in range(kernel_width):
                    kernel[kernel_height - 1][i] = 0

            # Generate the search map
            to_visit = generate_kernel(kernel, kernel_width, kernel_height, location)

            mines_count = count_mines(to_visit)

            if mines_count == block:
                mark_to_click_block(to_visit)

    def rel_loc_to_real(self, block_rel_location):
        return self.left + 16 * block_rel_location[0] + 8, self.top + 16 * block_rel_location[1] + 8

    def __init__(self):
        self.next_steps = []
        self.left = 0
        self.top = 0
        self.right = 0
        self.bottom = 0
        self.continue_random_click = False
        self.is_mine_form = True
        self.is_started = False
        self.have_solve = False
        if self.process_once():
            self.__inited = True

    def show_map(self):
        if self.__inited:
            for y in range(self.blocks_y):
                line = ""
                for x in range(self.blocks_x):
                    if self.blocks_num[x][y] == -1:
                        line += "  "
                    else:
                        line += str(self.blocks_num[x][y]) + " "
                print(line)

    def show_mine(self):
        if self.__inited:
            for y in range(self.blocks_y):
                line = ""
                for x in range(self.blocks_x):
                    if self.blocks_is_mine[x][y] == 0:
                        line += "  "
                    else:
                        line += str(self.blocks_is_mine[x][y]) + " "
                print(line)



    def is_valid(self,nums,selected_pairs):

        offset_pairs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

        def enum_nearby(x,y):
            lst = []
            for offset in offset_pairs:
                new_x = x + offset[0]
                new_y = y + offset[1]
                if new_x < 0 or new_x >= self.blocks_x or new_y < 0 or new_y >= self.blocks_y:
                    continue
                lst.append((new_x,new_y))
            return lst

        for p in selected_pairs:
            x,y = p
            num = nums[x][y]
            if 0 < num < 9:
                unknown = 0 
                know_mine = 0
                not_mine = 0
                for near in enum_nearby(x,y):
                    nx,ny = near
                    if nums[nx][ny] == -1:
                        unknown += 1
                    elif nums[nx][ny] == 0:
                        know_mine += 1
                    elif nums[nx][ny] == -10: # know not mine
                        not_mine += 1
                if not (know_mine <= num <= know_mine + unknown):
                    return False
        return True

    def search(self):
        if len(self.blocks_num) == 0:
            return []
        pairs=[]
        for x in range(self.blocks_x):
            for y in range(self.blocks_y):
                pairs.append((x,y))
        offset_pairs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

        def enum_nearby(x,y):
            lst = []
            for offset in offset_pairs:
                new_x = x + offset[0]
                new_y = y + offset[1]
                if new_x < 0 or new_x >= self.blocks_x or new_y < 0 or new_y >= self.blocks_y:
                    continue
                lst.append((new_x,new_y))
            return lst

        to_click_list = []


        shapes =[]
        shapes.append([(0,0),(0,1),(0,2),(0,3)])
        shapes.append([(0,0),(1,0),(2,0),(3,0)])

        def get_shape(x,y,shape):
            lst = []
            for p in shape:
                dx,dy = p
                if x+dx < 0 or x+dx >= self.blocks_x or y+dy < 0 or y+dy >= self.blocks_y:
                    continue
                if self.blocks_num[x+dx][y+dy] != -1:
                    continue
                lst.append((x+dx,y+dy))
            return lst

        for p in pairs:
            x,y = p
            for shape in shapes:
                #cloned = self.blocks_num.copy()
                cloned = copy.deepcopy(self.blocks_num)
                enum_pairs = get_shape(x,y,shape)
                #enum all subset of enum_pairs
                
                selected_pairs = enum_pairs
                for p in enum_pairs:
                    selected_pairs = selected_pairs + enum_nearby(p[0],p[1])
                selected_pairs = list(set(selected_pairs))
                count = len([p for p in selected_pairs if 0 < self.blocks_num[p[0]][p[1]] < 9])
                if count <= 2:
                    continue
                # to do accelerate here
                
                possible_mine = {}
                possible_empty = {}

                valid_sets = []

                for i in range(1 << len(enum_pairs)):
                    
                    for j in range(len(enum_pairs)):
                        if i & (1 << j):
                            cloned[enum_pairs[j][0]][enum_pairs[j][1]] = -10
                        else:
                            cloned[enum_pairs[j][0]][enum_pairs[j][1]] = 0
                    if self.is_valid(cloned,selected_pairs):
                        valid_sets.append(cloned)
                        for j in range(len(enum_pairs)):
                            if i & (1 << j):
                                possible_empty[enum_pairs[j]] = 1
                            else:
                                possible_mine[enum_pairs[j]] = 1
                for j in selected_pairs:
                    if j in possible_empty and j not in possible_mine:
                        to_click_list.append(('click',j[0],j[1]))
                    if j in possible_mine and j not in possible_empty:
                        to_click_list.append(('mine',j[0],j[1]))
                if len(to_click_list) > 0:
                    print('search')
                    print('start',x,y)
                    print('shape',shape)
                    print('selected',selected_pairs)
                    print(to_click_list)
                    """
                    for sets in valid_sets:
                        for xx in range(self.blocks_x):
                            for yy in range(self.blocks_y):
                                print(sets[xx][yy],end=' ')
                            print()
                        print('-----------------')
                    """
                    return to_click_list

        return to_click_list
 

    def process_once(self):

        self.steps+=1
        print('steps:',self.steps)

        # Initialize
        result = imageProcess.get_frame()
        if result == -1:
            print("Minesweeper Arbiter Window Not Detected!")
            return False
        self.img, self.blocks_img, form_size, img_size, form_location = result

        self.blocks_num = [[-1 for i in range(self.blocks_y)] for i in range(self.blocks_x)]
        self.blocks_is_mine = [[0 for i in range(self.blocks_y)] for i in range(self.blocks_x)]
        self.next_steps = []
        self.is_new_start = True
        self.is_mine_form = True

        self.blocks_x, self.blocks_y = form_size[0], form_size[1]
        self.width, self.height = img_size[0], img_size[1]
        self.img_cv = imageProcess.pil_to_cv(self.img)
        self.left, self.top, self.right, self.bottom = form_location

        # Analyze the number of blocks
        self.iterate_blocks_image(BoomMine.analyze_block)

        # Mark all mines
        #self.iterate_blocks_number(BoomMine.detect_mine)

        # Calculate where to click
        #self.iterate_blocks_number(BoomMine.detect_to_click_block)


        pairs=[]
        for x in range(self.blocks_x):
            for y in range(self.blocks_y):
                pairs.append((x,y))
        offset_pairs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

        def enum_nearby(x,y):
            lst = []
            for offset in offset_pairs:
                new_x = x + offset[0]
                new_y = y + offset[1]
                if new_x < 0 or new_x >= self.blocks_x or new_y < 0 or new_y >= self.blocks_y:
                    continue
                lst.append((new_x,new_y))
            return lst



        to_click_list = []
        #click and mark
        for p in pairs:
            if len(self.blocks_num) == 0:
                continue
            x,y = p
            num = self.blocks_num[x][y]
            if 0 < num < 9:
                unknown = 0 
                know_mine = 0
                for near in enum_nearby(x,y):
                    nx,ny = near
                    if self.blocks_num[nx][ny] == -1:
                        unknown += 1
                    elif self.blocks_num[nx][ny] == 0:
                        know_mine += 1
                if unknown == 0:
                    continue
                if unknown == num - know_mine:
                    # all mine
                    for near in enum_nearby(x,y):
                        nx,ny = near
                        if self.blocks_num[nx][ny] == -1:
                            to_click_list.append(('mine',nx,ny))
                            #print(x,y,' -> ','mine',nx,ny,num,unknown,know_mine)
                            #print(enum_nearby(x,y)) 
                if know_mine == num:
                    for near in enum_nearby(x,y):
                        nx,ny = near
                        if self.blocks_num[nx][ny] == -1:
                            to_click_list.append(('click',nx,ny))      
                            #print(x,y,' -> ','click',nx,ny,num,unknown,know_mine)
                            #print(enum_nearby(x,y)) 
        
        to_click_list = list(set(to_click_list))

        if len(to_click_list) == 0:
            print('search')
            to_click_list = self.search()
            if self.steps > 20:
                time.sleep(MEDIUM_TIME)
            else:
                time.sleep(SMALL_TIME)

        
        for to_click in to_click_list:
            oper , x , y = to_click
            print(oper,x,y)
            on_screen_location = self.rel_loc_to_real((x,y))
            if not self.is_in_form(mouseOperation.get_mouse_point()):
                print('not in form')
                break
            mouseOperation.mouse_move(on_screen_location[0], on_screen_location[1])
            if oper == 'click':
                mouseOperation.mouse_click()
            else:
                mouseOperation.mouse_right_click()
            time.sleep(SMALL_TIME)

        #print(self.blocks_num)

        self.have_solve = False
        if len(to_click_list) > 0:
            self.have_solve = True

        if not self.have_solve and self.is_mine_form:
            print('random')

            rand_location = (random.randint(0, self.blocks_x - 1), random.randint(0, self.blocks_y - 1))
            rand_x, rand_y = rand_location[0], rand_location[1]
            iter_times = 0

            if len(self.blocks_is_mine) > 0:

                while not self.blocks_num[rand_x][rand_y] == -1 and iter_times < 10000:
                    rand_location = (random.randint(0, self.blocks_x - 1), random.randint(0, self.blocks_y - 1))
                    rand_x, rand_y = rand_location[0], rand_location[1]
                    iter_times += 1

            screen_location = self.rel_loc_to_real((rand_location[0], rand_location[1]))
            if self.is_in_form(mouseOperation.get_mouse_point()):
                mouseOperation.mouse_move(screen_location[0], screen_location[1])
                mouseOperation.mouse_click()
            else:
                self.is_mine_form = False
            if self.steps > 20:
                time.sleep(MEDIUM_TIME)

        cv2.imshow("Sweeper Screenshot", self.img_cv)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
        return True


miner = BoomMine()

while 1:
    miner.process_once()
    try:
        time.sleep(SMALL_TIME)
    except:
        pass
# miner.show_map()
# print(miner.next_steps)
