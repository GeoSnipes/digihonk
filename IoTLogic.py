from random import randint
import ESPSerial 
from time import time

serconn = ESPSerial.ESPConnect(ESPSerial.commPort)

MYID = randint(1,100)
stoptime = time()
counter = 0

def new_broadcast(timenow=stoptime, mode='',next_move='',misc='', flush=True):
    global MYID
    global counter
    counter += 1
    
    new_ssid = '.'.join([str(MYID), str(counter), str(int(timenow)),str(mode),str(next_move),str(misc)])

    serconn.update_beacon_ssid(new_ssid)
    if flush:
        serconn.flush_serial_inout()
    else:
        print(serconn.read_from_esp(.4))

def get_dghonks(wait=1):
    serconn.update_beacon_ssid("1:")
    return serconn.read_from_esp(wait)

def get_MYID():
    serconn.update_beacon_ssid("2:")
    return serconn.read_from_esp()

def create_inter_dict(inter_SSIDS, car_ids = {}):
    entries = []
    errorhonk = []
    #Check and combine stats to ensure unique car ids
    for wifissid in inter_SSIDS.strip().split('\n')[1:]:
        split_spec = wifissid.strip().split('||')
        if not split_spec[1].startswith('DGHonk-'):
            # print(wifissid)
            continue
        ssid = split_spec[1]
        dghonk_stat = ssid.lstrip('DGHonk-').rstrip('---').split('.')
        # car_stat = [int(i) for i in car_stat]
        if len(dghonk_stat) != 6:
            errorhonk.append(wifissid)
            continue
        if dghonk_stat[0] in car_ids:
            if int(dghonk_stat[1]) > int(car_ids[dghonk_stat[0]][0]):
                car_ids[dghonk_stat[0]] = tuple(dghonk_stat[1:3]+split_spec[3:5])
        else:
            car_ids[dghonk_stat[0]] = tuple(dghonk_stat[1:3]+split_spec[3:5])
    
    if len(errorhonk) > 0:
        print(f"Error DGHonk SSID's:\n{errorhonk}")
    return car_ids

def find_next_inline(dghonks):
    sorted_dghonks = sorted(dghonks.items(), key=lambda x: int(x[1][1]))
    nextmove = [sorted_dghonks[0][0]]
    for honk in sorted_dghonks[1:]:
        if honk[0] == nextmove[0]:
            nextID.append(honk[0])
        else:
            break

    print(sorted_dghonks)
    print(nextmove)
    return min(nextmove)

def run_mode2():
    new_broadcast(mode='2', flush=False)
    return get_dghonks()

def run_mode3(dghonks):
    global MYID
    nextID = find_next_inline(dghonks)
    if str(MYID) != nextID:
        run_mode4()
    else:
        new_broadcast(mode='3', next_move=nextID, flush=False)

    return nextID

def run_mode4():
    new_broadcast(mode='4', next_move=MYID, flush=False)

def run_mode5():
    accgyro=[]
    return
    serconn.update_beacon_ssid('3:')
    upd = serconn.read_from_esp(.3)
    while upd != None:
        accgyro.append(upd)
        upd = serconn.read_from_esp(.3)


'''CAR_ID.COUNTER.TIME_STOPPED.MODE.CAR_ID MOVENEXT.MISC'''
'''MODES
1-STARTUP
2-Scanning
3-SuggestingNEXTTOMOVE
4-IMMOving
5-MonitoringNextToMove
6-PassedIntersection
'''
honk_list = '1||DGHonk-1.1.1256489.1..---||11||-52||18:9C:27:34:42:60\n2||DGHonk-2.2.741688.3..---||11||-68||58:20:B1:88:78:A8\n'+\
    '3||DGHonk-3.1.8648659.2..---||11||-84||D4:B9:2F:9B:D1:25\n4||DGHonk-3.3.84916864...---||11||-93||4E:7A:8A:96:D7:D2\n'+\
    '4||Hennhouse||11||-89||10:93:97:78:EA:40\n5||Heathers wi fi||11||-90||3C:7A:8A:96:D7:D2\n'

if __name__ == '__main__':
    # MYID = get_MYID().strip()
    # new_broadcast(mode='1', flush=False)
    while True:
        # honk_list = run_mode2()
        print(MYID)
        print(honk_list)
        if len(honk_list) != 0:
            inter_list = create_inter_dict(honk_list)
            if len(inter_list) > 0:
                nextID = run_mode3(inter_list)
                if str(MYID) != nextID:
                    run_mode5()
            else:
                run_mode4()
        else:
            run_mode4()

        break


serconn.close_connect()
