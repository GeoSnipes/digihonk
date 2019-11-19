from random import randint
import ESPSerial 
from time import time, sleep
import re

serconn = ESPSerial.ESPConnect(ESPSerial.commPort)

MYID = randint(1,100)
stoptime = time()
counter = 0
my_direction = 8

collision = {
    '1': ['4', '5', '7', '8', '9', '10', '11'],
    '2': ['4', '5', '6', '7', '10', '11'],
    '3': ['7', '11', '12'],
    '4': ['1', '2', '7', '8', '10', '11', '12'],
    '5': ['1', '2', '7', '8', '9', '10'],
    '6': ['2', '10'],
    '7': ['1', '2', '3', '4', '5', '10', '11'],
    '8': ['1', '4', '5', '10', '11', '12'],
    '9': ['1', '5'],
    '10': ['1', '2', '4', '5', '6', '7', '8'],
    '11': ['1', '2', '3', '4', '7', '8'],
    '12': ['4', '8']
    }

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
        input: inter_SSIDS = ['1||DGHonk-1.1.1256489.1.2.---||11||-52||18:9C:27:34:42:60','4||Hennhouse||11||-89||10:93:97:78:EA:40']
                            id:  counter    time stopped   mode   direction  signal stregth  mac address
        output: car_ids = {'1':[    '1',    '1256489',      '1',      '2'       '-52',         '18:9C:27:34:42:60']}
                           
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
                car_ids[dghonk_stat[0]] = tuple(dghonk_stat[1:5]+split_spec[3:5])
        else:
            car_ids[dghonk_stat[0]] = tuple(dghonk_stat[1:5]+split_spec[3:5])
    
    if len(errorhonk) > 0:
        print(f"Error DGHonk SSID's:\n{errorhonk}")
    return car_ids

def mode2_scanssid():
    """ Find all ssids in area
            
        rtype: list
    """
    new_broadcast(mode='2', flush=False)
    return get_dghonks()

def mode4_immoving():
    """ Broadcast that I'm moving
            
        rtype: None
    """
    new_broadcast(mode='4', next_move=MYID, flush=False)
    sleep(5)
    new_broadcast(mode='6', flush=False)


def mode5_monitornexttomove(go_after):
    """ Monitor next inline until out of intersection
            
        rtype: None
    """
    for mon in go_after:
        signal_strength = []
        for _ in range(2):
            while True:
                honks = create_inter_dict(get_dghonks())
                if mon in honks:
                    signal_strength.append(int(honks[mon][4]))
                else:
                    sleep(.5)
                    break

def mode7_findallmoving(inter_list):
    global MYID
    global my_direction
    global stoptime
    moving = []
    will_collide = []
    turn_intents= {str(my_direction): (str(MYID), stoptime)}
    for car in inter_list:
        intent = inter_list[car][3]
        turn_intents[intent] = car

    for intent in turn_intents.keys():
        collision_count = len(set(collision[intent]).intersection(set(turn_intents.keys())))
        if collision_count > 0:
            will_collide.append(turn_intents[intent])
        else:
            moving.append(turn_intents[intent]) 
    
    return moving, will_collide

def mode7_findallmoving(inter_list, v2):
    global MYID
    global my_direction
    global stoptime
    moving = []
    will_collide = []
    shouldwait = []
    turn_intents= {str(my_direction): (str(MYID), stoptime)}
    for car in inter_list:
        intent = inter_list[car][3]
        turn_intents[intent] = (car, int(inter_list[car][1]))

    sorted_intents = sorted(turn_intents.items(), key=lambda x: int(x[1][1]))
    moving.append(sorted_intents[0][1][0])
    intent = sorted_intents[0][0]
    will_collide.extend(collision[intent])

    for intent, id_time in sorted_intents:
        if (intent not in will_collide) and (intent != sorted_intents[0][0]):
            moving.append(id_time[0])
            will_collide.extend(collision[intent])
        
    shouldwait = set(inter_list.keys()).difference(set(moving))
    return moving, shouldwait

'''CAR_ID.COUNTER.TIME_STOPPED.MODE.DIRECTION.MISC'''
'''MODES
1-STARTUP
2-Scanning
4-IMMOving
5-MonitoringNextToMove
6-PassedIntersection
7-Findmoving
'''
honk_list = ['1||DGHonk-1.1.1256489.1..---||11||-52||18:9C:27:34:42:60','2||DGHonk-2.2.741688.3..---||11||-68||58:20:B1:88:78:A8',\
    '3||DGHonk-3.1.8648659.2..---||11||-84||D4:B9:2F:9B:D1:25','4||DGHonk-4.3.84916864...---||11||-93||4E:7A:8A:96:D7:D2',\
    '4||Hennhouse||11||-89||10:93:97:78:EA:40','5||Heathers wi fi||11||-90||3C:7A:8A:96:D7:D2']

if __name__ == '__main__':
    # MYID = get_MYID().strip()
    new_broadcast(mode='1', flush=False)
    while True:
        # honk_list = run_mode2()
        if len(honk_list) != 0:
            inter_list = create_inter_dict(honk_list)
            if len(inter_list) > 0:
                mov, col = mode7_findallmoving(inter_list, True)
                if str(MYID) in  mov:
                    break
                else:
                    mode5_monitornexttomove(col)

    mode4_immoving()


serconn.close_connect()
