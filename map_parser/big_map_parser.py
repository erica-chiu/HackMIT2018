
from PIL import Image as PILImage
import numpy as np


def match(positives):
    buildings = []
    done = set()
    for i in range(positives.shape[0]):
        for j in range(positives.shape[1]):
            if positives[i][j] == 255:
                if (i,j) not in done:
                    buildings.append({(i,j)})
                    done.add((i,j))
                    queue = [(i,j)]
                    index = 0
                    while index < len(queue):
                        pi,pj = queue[i]
                        if pi+1 < positives.shape[0]:
                            if positives[pi+1][pj] == 255 and (pi+1,pj) not in done:
                                done.add((pi+1,pj))
                                buildings[-1].add((pi+1,pj))
                        if pi-1 >= 0:
                            if positives[pi-1][pj] == 255 and (pi-1,pj) not in done:
                                done.add((pi-1,pj))
                                buildings[-1].add((pi-1,pj))
                        if pj+1 < positives.shape[1]:
                            if positives[pi][pj+1] == 255 and (pi,pj+1) not in done:
                                done.add((pi,pj+1))
                                buildings[-1].add((pi,pj+1))
                        if pj-1 >=0:
                            if positives[pi][pj-1] == 255 and (pi,pj-1) not in done:
                                done.add((pi,pj-1))
                                buildings[-1].add((pi,pj-1))
                        index += 1


def map_parse():
    with open('bigmap.png', 'rb') as img_handle:
        img = PILImage.open(img_handle)
        img = img.convert('RGB')
        img_data = np.array(img.getdata())
        yellow = np.all(np.equal(img_data,np.reshape(np.tile([255, 255, 153],len(img_data)),[len(img_data),3])),axis=1)
        yellow = 255*yellow
        out = PILImage.new(mode='L', size=img.size)
        out.putdata(yellow)
        out.save('test.png')

        yellow = np.reshape(yellow,img.size)

        buildings = match(yellow)

        black = np.all(np.equal(img_data, np.reshape(
            np.tile([0, 0, 0], len(img_data)), [len(img_data), 3])),
                        axis=1)
        black = 255 * black
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

    return {'outline':red,'buildings':yellow,'names':black}




map_parse()
