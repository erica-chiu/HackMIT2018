
with open('rooms.json','r') as f:
    rooms = f.readline()
    final = rooms
    for idx,i in enumerate(rooms):
        if i=="'":
            final = final[:idx] + '"'+final[idx+1:]

with open('rooms2.json','w+') as f:
    f.write(final)
