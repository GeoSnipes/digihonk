from random import randint
import ESPSerial 
from time import time, sleep
import re

serconn = ESPSerial.ESPConnect(ESPSerial.commPort)

MYID = randint(1,100)
stoptime = time()
counter = 0

def new_broadcast(timenow=stoptime, mode='',next_move='',misc='', flush=True):
    """ Construct broadcast ssid the  arduino is to use
            
        param defL: linux, folder where mount points are found (default- /dev/)
        rtype: string
    """
    global MYID
    global counter
    counter += 1
    
    new_ssid = '.'.join([str(MYID), str(counter), str(int(timenow)),str(mode),str(next_move),str(misc)])

    serconn.update_beacon_ssid(new_ssid)
    if flush:
        serconn.flush_serial_inout()
    else:
        print(serconn.read_from_esp(.4))

def get_dghonks(wait=1, entire=True):
    """ Retrieve list of DGHonk signals
            
        param wait: time to wait before getting input from arduino (default- 1 sec)
        param entire: get entire list instead of single line
        rtype: list
    """
    numnet = -1
    honk_list = []

    serconn.update_beacon_ssid("1:")
    ssids = serconn.read_from_esp(wait, entire).split('\n')
    
    numnet = int(re.findall(ssids[0].strip(), r'(\d{1,2})$'))
    while numnet + 1 != len(ssids):
        ssids.extend(serconn.read_from_esp(entire=False).split('\n'))
    for ssid in ssids[1:]:
        honk_list.append(ssid.strip())

    return honk_list

def get_MYID():
    """ Retrieve MAC address of arduino
            
        rtype: string
    """
    serconn.update_beacon_ssid("2:")
    return serconn.read_from_esp()

def create_inter_dict(inter_SSIDS, car_ids = {}):
    """ Convert list of ssid signals to dictionary with key id and value stats 

        EG-
        input: inter_SSIDS = ['1||DGHonk-1.1.1256489.1..---||11||-52||18:9C:27:34:42:60','4||Hennhouse||11||-89||10:93:97:78:EA:40']
                            id:  counter    time stopped   mode   signal stregth  mac address
        output: car_ids = {'1':[    '1',    '1256489',      '1',    '-52',         '18:9C:27:34:42:60']}
                           
        param inter_SSIDS: list of ssids
        param car_ids: previous dictionary of ssids (default- dict())
        rtype: dictionary
    """
    errorhonk = []
    #Check and combine stats to ensure unique car ids
    for wifissid in inter_SSIDS:
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
                car_ids[dghonk_stat[0]] = tuple(dghonk_stat[1:4]+split_spec[3:5])
        else:
            car_ids[dghonk_stat[0]] = tuple(dghonk_stat[1:4]+split_spec[3:5])
    
    if len(errorhonk) > 0:
        print(f"Error DGHonk SSID's:\n{errorhonk}")
    return car_ids

def find_next_inline(dghonks):
    """ Sort dictionary by arrival time
            
        rtype: string
    """
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


def mode2_scanssid():
    """ Find all ssids in area
            
        rtype: list
    """
    new_broadcast(mode='2', flush=False)
    return get_dghonks()

def mode3_tellnexttomove(dghonks):
    """ Broadcast new suggested to move
            
        rtype: string
    """
    global MYID
    nextID = find_next_inline(dghonks)
    if str(MYID) != nextID:
        new_broadcast(mode='3', next_move=nextID, flush=False)
        mode5_monitornexttomove(nextID)
    return nextID

def mode4_immoving():
    """ Broadcast that I'm moving
            
        rtype: None
    """
    new_broadcast(mode='4', next_move=MYID, flush=False)
    sleep(5)
    new_broadcast(mode='6', flush=False)


def mode5_monitornexttomove(nextID):
    """ Monitor next inline until out of intersection
            
        rtype: None
    """
    signal_strength = []
    for _ in range(2):
        while True:
            honks = create_inter_dict(get_dghonks())
            if nextID in honks:
                signal_strength.append(int(honks[nextID][3]))
            else:
                sleep(1)
                break



'''CAR_ID.COUNTER.TIME_STOPPED.MODE.CAR_ID MOVENEXT.MISC'''
'''MODES
1-STARTUP
2-Scanning
3-SuggestingNEXTTOMOVE
4-IMMOving
5-MonitoringNextToMove
6-PassedIntersection
'''
honk_list = ['1||DGHonk-1.1.1256489.1..---||11||-52||18:9C:27:34:42:60','2||DGHonk-2.2.741688.3..---||11||-68||58:20:B1:88:78:A8',\
    '3||DGHonk-3.1.8648659.2..---||11||-84||D4:B9:2F:9B:D1:25','4||DGHonk-4.3.84916864...---||11||-93||4E:7A:8A:96:D7:D2',\
    '4||Hennhouse||11||-89||10:93:97:78:EA:40','5||Heathers wi fi||11||-90||3C:7A:8A:96:D7:D2']

if __name__ == '__main__':
    # MYID = get_MYID().strip()
    new_broadcast(mode='1', flush=False)
    while True:
        # honk_list = run_mode2()
        if len(honk_list) == 0:
            inter_list = create_inter_dict(honk_list)
            if len(inter_list) > 0:
                nextID = mode3_tellnexttomove(inter_list)
                if str(MYID) != nextID:
                    continue
            
        mode4_immoving()

        break


serconn.close_connect()
