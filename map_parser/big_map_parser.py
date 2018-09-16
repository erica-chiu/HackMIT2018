
from PIL import Image as PILImage
import numpy as np


def match(positives):
    buildings = []
    done = set()
    test = np.zeros(positives.shape)
    for i in range(positives.shape[0]):
        for j in range(positives.shape[1]):
            if positives[i][j] == 255:
                if (i,j) not in done:
                    buildings.append({(i,j)})
                    done.add((i,j))
                    queue = [(i,j)]
                    index = 0
                    while index < len(queue):
                        pi,pj = queue[index]
                        test[pi][pj] = (7*(len(buildings)+1))%256
                        neighbors = [(pi+1,pj),(pi-1,pj),(pi,pj+1),(pi,pj-1),(pi+1,pj+1),(pi+1,pj-1),(pi-1,pj+1),(pi-1,pj-1)]
                        neighbors = [(pi+1,pj),(pi-1,pj),(pi,pj+1),(pi,pj-1)]
                        for ti,tj in neighbors:
                            if 0<=ti<positives.shape[0] and 0<=tj<positives.shape[1]:
                                if positives[ti][tj]==255 and (ti,tj) not in done:
                                    done.add((ti,tj))
                                    buildings[-1].add((ti,tj))
                                    queue.append((ti,tj))

                        index += 1
    return buildings,test

def match2(positives):
    buildings = []
    matching = {}
    done = set()
    test = np.zeros(positives.shape)
    for i in range(positives.shape[0]):
        for j in range(positives.shape[1]):
            if positives[i][j] == 255:
                if (i,j) not in done:
                    buildings.append({(i,j)})
                    done.add((i,j))
                    queue = [(i,j)]
                    index = 0
                    while index < len(queue):
                        pi,pj = queue[index]
                        test[pi][pj] = (7*(len(buildings)+1))%256
                        neighbors = [(pi+1,pj),(pi-1,pj),(pi,pj+1),(pi,pj-1),(pi+1,pj+1),(pi+1,pj-1),(pi-1,pj+1),(pi-1,pj-1)]
                        for ti,tj in neighbors:
                            if 0<=ti<positives.shape[0] and 0<=tj<positives.shape[1]:
                                if positives[ti][tj]==255 and (ti,tj) not in done:
                                    done.add((ti,tj))
                                    buildings[-1].add((ti,tj))
                                    queue.append((ti,tj))

                        index += 1
                    for p in buildings[-1]:
                        matching[p] = buildings[-1]
    return matching,test


def make_clouds(buildings,black):
    letters = []
    for b in buildings:
        letters.append(set())
        beento = set(b)
        queue = list(b)
        index =0
        while index < len(queue):
            if len(queue[index])==2:
                pi,pj = queue[index]
                n=0
            else:
                pi,pj,n = queue[index]
            neighbors = [(pi + 1, pj), (pi - 1, pj), (pi, pj + 1),
                         (pi, pj - 1), (pi + 1, pj + 1), (pi + 1, pj - 1),
                         (pi - 1, pj + 1), (pi - 1, pj - 1)]
            for ti, tj in neighbors:
                if 0 <= ti < black.shape[0] and 0 <= tj < black.shape[1]:
                    if (ti, tj) not in beento:
                        beento.add((ti, tj))
                        if n == 5:
                            if black[ti][tj]:
                                letters[-1].add((ti,tj))
                        elif black[ti][tj]:
                            letters[-1].add((ti, tj))
                            queue.append((ti, tj,n+1))
                        else:
                            queue.append((ti,tj,n+1))
            index += 1
    return letters

def map_parse():
    with open('bigmap.png', 'rb') as img_handle:
        img = PILImage.open(img_handle)
        img = img.convert('RGB')
        img_data = np.array(img.getdata())
        yellow = np.all(np.equal(img_data,np.reshape(np.tile([255, 255, 153],len(img_data)),[len(img_data),3])),axis=1)
        yellow = 255*yellow
        # out = PILImage.new(mode='L', size=img.size)
        # out.putdata(yellow)
        # out.save('test.png')

        yellow = np.reshape(yellow, [img.size[1],img.size[0]])
        # out = PILImage.new(mode='L', size=img.size)
        # out.putdata(np.reshape(yellow,[-1]))
        # out.save('test_r.png')

        buildings,t = match(yellow)
        # out = PILImage.new(mode='L', size=img.size)
        # out.putdata(np.reshape(t,[-1]))
        # out.save('colorbuild.png')

        black = np.all(np.equal(img_data, np.reshape(
            np.tile([0, 0, 0], len(img_data)), [len(img_data), 3])),
                       axis=1)
        black = np.reshape(black,[img.size[1],img.size[0]])

        possible_letters = make_clouds(buildings,black)
        black = 255 * black
        letters,t2 = match2(black)

        # with open('areas_buildings.txt','w+') as f:
        #     f.write(str(buildings))
        #
        # final_letters = []
        #
        #
        # for lets in possible_letters:
        #     final_letters.append(set())
        #     for pl in lets:
        #         final_letters[-1] = final_letters[-1].union(letters[pl])
        #
        # print(len(final_letters),len(buildings))
        # for i in range(len(final_letters)):
        #     test_im = np.zeros([img.size[1], img.size[0]])
        #     for x,y in final_letters[i]:
        #         test_im[x][y] = 255
        #     if len(final_letters[i]) == 0:
        #         print('no categorization',i)
        #     for x,y in buildings[i]:
        #         test_im[x][y] = 100
        #     out = PILImage.new(mode='L', size=img.size)
        #     out.putdata(np.reshape(test_im, [-1]))
        #     out.save('namescolors'+str(i)+'.png')

        with open('areas_buildings.txt','r') as f:
            buildings = eval(f.readline())

        building_nums = ['N57','N57','N57','NE80','NE80','NE80','NE80','N51','NW62','N52',
                         '0','N52','NW62','0','N51','N51','N51','NW61','NW61','NW61',
                         'N42','N42','NE43','NE43','NW10','NW16','NW17','NW22','0','N4',
                         'NW22','NW22','N4','NW12','NW12','N10','N9','48','N16','48',
                         'N10', 'N10', '45', '48', '48', 'NW12', 'NW13', 'NW14', '44', '45',
                         '70', 'NW12', 'NW21', '42', '44', '44', 'NW30', '41', 'NW20', '42',
                         'WW15', 'NW20', '41A', 'NW20', 'NW15', 'NW14', 'NW15', 'NW20', 'NE25', 'NW30',
                         'NW21', '41A', '70', '41', '36', '41A', 'NW15', '36', '34', '38',
                         '39', '37', '38', '0', '35', '38', '39', 'NE20', 'W45', '26',
                         '34', '0', 'E19', '33', '68', '31', '24', 'W45', 'NE20', 'W31',
                         'W59','17A', '17A', '17A', '17A', '57', 'W33', 'W32', 'E19', '17',
                         'W59','W34', 'W31', '17B', '24', 'E28', '0', '17B', '68', 'E28',
                         'E28', '17B', '68', '68', 'E28', '0', 'E18', 'E28', '0', '9',
                         'E23/E25', '12', 'E18', 'E18', '9', '13', 'E17', '26', 'E38', 'W23',
                         '66', 'W20', '0', 'W87', 'W34', '7', 'E38', 'E39', '56', '7A',
                         '16', 'E38', 'W87', '7', 'W89', '56', 'W87', 'W20', '0', 'W23',
                         '10', '12A', '16', '66', '66', 'W89', 'W89', '12A', '0', '11',
                         'E39', 'W89', '8', 'E48', '12A', '10', '0', '18', '7', 'E15',
                         '3', '4', '4', '0', 'E48', 'W85', 'W85', 'W85', '18', 'E48',
                         'E48', '4', '18', '62', '64', 'W92','W85', 'E34', '54', 'E42',
                         'W85','W85', 'W85', 'W85', 'W85', '6', '54', 'E34', '5', '4A',
                         '18', '6A', 'E34', '4A', 'E33', '18', 'W16', '4A', '4A', '6A',
                         'E33', 'E23/E25', 'W13', 'E32', 'W85', '6A', 'W92', '0', 'W13', 'W13',
                         'W13', 'E32', '64','E42', 'E55', 'W16', 'E32', 'E42', '62', '64',
                         'E20', 'W15', '62', '64', 'E10', 'W85', 'W15', 'W53', 'W15', '68',
                         'W85', '4', '6B', 'E10', 'W15', 'W85', '6B', 'W85', 'W11', 'E40',
                         'W91', '6', 'W85', 'W85', 'E40', 'E40', '2', '1', '14N', '14N',
                         '14N', '14N', '0', '0', 'E53', '14N', '14N', '14E', '0', '14W',
                         'E51', '50', 'W1', 'W91', 'E2', 'W84', '14W', '14E', 'W51', 'E2',
                         '0', 'W84', 'E3', 'W70', '0', '0', '14S', 'W84', 'W71', 'W4',
                         '50', 'E56', '0', 'E52', 'W61', 'E56', 'W7', 'W5', 'W61', '14S',
                         'W51', '0', 'E60', 'W5', 'E56', 'E56', 'W4', 'W70', 'W70', 'W5',
                         '0', 'W70', '0', 'W7', 'E1', 'E60', 'W7', '0', 'W2', 'E51',
                         '0','E60', 'W2', 'W5', 'W2', 'W2', 'W61', 'W61', 'W61', 'W2',
                         'W2', 'W61', 'E51', 'E51', 'W8', 'W8','W8']


        map = [list(['0' for _ in range(img.size[0])]) for _ in range(img.size[1])]
        for i,b in enumerate(buildings):
            for x,y in b:
                map[x][y] = building_nums[i]

        with open('building_map.txt','w+') as f:
            f.write(str(map))








        # out = PILImage.new(mode='L', size=img.size)
        # out.putdata(np.reshape(t2, [-1]))
        # out.save('colorletters.png')









        # ones = 255*np.ones([30,30])
        # padding = np.pad(ones,[[30,img.size[1]-60],[30,img.size[0]-60]],'constant')
        # out = PILImage.new(mode='L', size=img.size)
        # out.putdata(np.reshape(padding, [-1]))
        # out.save('straight.png')

        # print(len(buildings))
        # print(buildings[1],buildings[2],yellow[301][329],yellow[302][329],yellow[300][329])


        # out = PILImage.new(mode='L', size=img.size)
        # out.putdata(black)
        # out.save('black.png')

        red = np.all(np.equal(img_data, np.reshape(
            np.tile([204, 153, 102], len(img_data)), [len(img_data), 3])),
                       axis=1)
        red = 255 * red
        # out = PILImage.new(mode='L', size=img.size)
        # out.putdata(red)
        # out.save('red.png')

        white = np.all(np.equal(img_data, np.reshape(
            np.tile([255, 255, 255], len(img_data)), [len(img_data), 3])),
                     axis=1)
        white = 255 * white
        # out = PILImage.new(mode='L', size=img.size)
        # out.putdata(white)
        # out.save('white.png')

    return {'outline':red,'buildings':yellow,'names':black,'final':map}




map_parse()
