from random import randint
import ESPSerial 
from time import time, sleep
import re
from argparse import ArgumentParser

MYID = randint(1,100)
MYSSID = ''
timer_start = 9999999999
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
def gettime(cnv_time=None):
    precision = (10**3)
    
    if cnv_time != None:
        return cnv_time/precision

    timenow = time()
    timenow = int(timenow*(precision))/(10.0**7)
    timenow = str(timenow).split('.')[1]
    timenow += '0'*(7-len(timenow))
    return int(timenow)
def new_broadcast(mode, misc='', flush=False):
    """Construct broadcast ssid the  arduino is to use

    Parameters
    ----------
    timenow : int, optional
        time for broadcast (default is current time)
    mode : str
        from mode types, mode to broadcast
    misc : str, opional
        for future code (default is empty)
    flush : bool, optional
        if not needed, you can flush the input output buffer of m5stick
    """

    global MYID
    global counter
    global my_direction 
    global timer_start
    global MYSSID
    counter += 1

    serconn.flush_serial_inout()

    if mode != '0':
        new_ssid = '.'.join([str(MYID), str(counter), str(int(timer_start)),str(mode),str(my_direction),str(misc)])
        MYSSID = 'DGHonk-'+new_ssid
    else:
        new_ssid = '---'

    serconn.update_beacon_ssid(new_ssid)
    if not flush:
        serconn.flush_serial_inout()
    else:
        print(new_ssid, end='\t\t\t')
        print(serconn.read_from_esp(.4))


def get_dghonks(wait=.4, entire=True):
    """Retrieve list of all wifi signals

    Parameters
    ----------
    wait : int, optional
        time to wait before trying to read ssid results from m5stick (default is 1 second)
    entire : bool, optional
        retrieve entire list of results instead of one line of result (default is True)
    
    Returns
    -------
    list
        a list of each ssid found
    """
    numnet = -1
    honk_list = []

    serconn.update_beacon_ssid("1:")
    ssids = serconn.read_from_esp(wait, entire).split('\n')
    
    numnet = int(re.search(r'\d{1,2}', ssids[0].strip()).group())
    while numnet + 1 < len(ssids):
        ssids.extend(serconn.read_from_esp(entire=False).split('\n'))
    for ssid in ssids[1:]:
        honk_list.append(ssid.strip())

    return honk_list

def get_MYID():
    """Retrieve MAC address of arduino

    Returns
    -------
    str
        mac address
    """
    serconn.update_beacon_ssid("2:")
    return serconn.read_from_esp()

def create_inter_dict(inter_SSIDS, show_sig=False):
    """Convert list of ssid signals to a dictionary with key id and value stats 

    Parameters
    ----------
    inter_SSIDS : list
        list of wifi ssids found
    car_ids : dict, optional
        pre populated dictionary of car stats by unique id (default is empty dicitonary)
    
    Return
    ------
    dict
        car stats by id

    E.G.
                          num||id.counter.time stopped.mode.direction.misc||channel||signal stregth||mac address
    input: inter_SSIDS = ['1||DGHonk-1.3.1256489.1.2.||11||-52||18:9C:27:34:42:60', '4||Hennhouse||11||-89||10:93:97:78:EA:40']
                            
    output: car_ids = {'1':[    '1',    '1256489',      '1',      '2'       '-52',         '18:9C:27:34:42:60']}
    """

    errorhonk = []
    car_ids={}
    
    inter_SSIDS.append(f'0||{MYSSID}||11||-1||00:00:00:00:00:00')

    #Check and combine stats to ensure unique car ids
    for wifissid in inter_SSIDS:
        split_spec = wifissid.strip().split('||')

        # Ignore ssids that do not follow DGHonk protocol
        if not split_spec[1].startswith('DGHonk-'):
            continue
        ssid = split_spec[1]
        dghonk_stat = ssid.lstrip('DGHonk-').split('.')
        
        # Record ssid not formatted correctly
        if len(dghonk_stat) != 6:
            errorhonk.append(wifissid)
            continue

        # Create dictionary
        if dghonk_stat[0] in car_ids:
            if int(dghonk_stat[1]) > int(car_ids[dghonk_stat[0]][0]):
                car_ids[dghonk_stat[0]] = tuple(dghonk_stat[1:5]+split_spec[3:5])
        else:
            car_ids[dghonk_stat[0]] = tuple(dghonk_stat[1:5]+split_spec[3:5])
    
    # if len(errorhonk) > 0:
    #     print(f"Error DGHonk SSID's:\n{errorhonk}")
    if show_sig:
        for cid, stat in car_ids.items():
            print(f'{cid}: {stat}')
    return car_ids

def mode2_scanssid():
    """Find all ssids' in the area

    Returns
    -------
    list
        all ssids
    """
    new_broadcast(mode='2')
    return get_dghonks()

def mode4_immoving():
    """Update ssids with status of moving porgress
    """
    new_broadcast(mode='4')
    serconn.update_beacon_ssid('dgh:2')
    '''Read from arduino button press to signify passed intersection'''
    print(f'[INFO] Waiting on notfication passed intersection.')
    while True: 
        stop_dgh = serconn.read_from_esp()
        if stop_dgh == 'dgh:0':
            break
    new_broadcast(mode='6')



def mode5_monitornexttomove(go_after):
    """Construct broadcast ssid the  arduino is to use

    Parameters
    ----------
    go_after: list
        list of cars to monitor until they are out of intersection
    """
    try:
        new_broadcast(mode='5')
        for mon in go_after:
            signal_strength = []
            for _ in range(2):
                while True:
                    honks = create_inter_dict(get_dghonks())
                    if mon in honks:
                        signal_strength.append(int(honks[mon][4]))
                        if honks[mon][2] == '6':
                            break
                    else:
                        break
    except KeyboardInterrupt:
        new_broadcast(mode='0')
        serconn.__exit__
        quit()

def mode7_findallmoving(inter_list, model1=False):
    """Construct iterator of cars that can move and those that cannot

    Parameters
    ----------
    inte_list : dict
        dghonk ssids
    
    Return
    ------
    list, list
        cars allowed to move, cars not allowed due to collision risk
    """

    global MYID
    global my_direction
    global timer_start

    new_broadcast(mode='7')

    all_cars = set()
    moving = []
    will_collide = set()
    shouldwait = []

    # Add myself to turn intention list
    # turn_intents= {str(my_direction): (str(MYID), timer_start)}
    turn_intents = {}
    # Add remaining cars to turn intention
    for car in inter_list:
        if inter_list[car][2] == '6':
            continue
        intent = inter_list[car][3]
        turn_intents[intent] = (car, int(inter_list[car][1]))
    # print(turn_intents)
    sorted_intents = sorted(turn_intents.items(), key=lambda x: int(x[1][1]))
    
    # Add each car to allowed to move and create a set of directions that will collide
    for intent, id_time in sorted_intents:
        all_cars.add(id_time[0])
    for intent, id_time in sorted_intents:
        if (intent not in will_collide):
            moving.append(id_time[0])
            will_collide.update(collision[intent])
        if model1:
            break

    # Collect all car is not able to turn
    shouldwait = all_cars.difference(set(moving))
    return moving, shouldwait


'''MODES
1-STARTUP
2-Scanning
4-IMMOving
5-MonitoringNextToMove
6-PassedIntersection
7-Findmoving
'''
honk_list = [\
    '1||DGHonk-1.1.1575354939.1.3.||11||-52||18:9C:27:34:42:60',\
    '2||DGHonk-2.2.1575355939.3.6.||11||-68||58:20:B1:88:78:A8',\
    '3||DGHonk-3.1.1572355969.2.12.||11||-84||D4:B9:2F:9B:D1:25',\
    '4||DGHonk-4.3.1575355839.2.7.||11||-93||4E:7A:8A:96:D7:D2',\
    '4||Hennhouse||11||-89||10:93:97:78:EA:40',\
    '5||Heathers wi fi||11||-90||3C:7A:8A:96:D7:D2']

if __name__ == '__main__':
    dgh_timers = []

    parser = ArgumentParser()
    parser.add_argument('-p', dest='port', action='store', help='Supply port (WIN only)', default= 'COM23')
    parser.add_argument('-d', dest='dir', action='store', help='Supply direction intent', default=8)
    parser.add_argument('-i', dest='id', action='store', help='Set id to use', default=MYID)
    results = parser.parse_args()

    ESPSerial.commPort  = results.port
    my_direction = int(results.dir)
    MYID = results.id
    with ESPSerial.ESPConnect(results.port) as serconn:
        serconn.update_beacon_ssid('dgh:0')
        while True:
            print(f'[INFO] DGH startup. MYID: {MYID}\t\tDirection:{my_direction}')
            new_broadcast(mode='0')
            print(f'[INFO] Waiting on notification at intersection.')
            while True: 
                start_dgh = serconn.read_from_esp()
                if start_dgh == 'dgh:1':
                    break
            timer_start = gettime()
            while True:
                print(f'[INFO] Scanning for DGHonks.')
                honk_list = mode2_scanssid()
                print(f'[INFO] Finding collisions.')
                inter_list = create_inter_dict(honk_list, show_sig=False)
                if len(inter_list) > 1:
                    mov, col = mode7_findallmoving(inter_list)
                    print(f'[INFO] Allowed to move: {mov}\nMust wait: {col}')
                    if str(MYID) in  mov:
                        break
                    else:
                        mode5_monitornexttomove(mov)
                        continue
                break
            print(f'[INFO] Permission to go received. {MYID} will go.')
            mode4_immoving()
            print(f'[INFO] Passed intersection notification received.')
            new_broadcast(mode='0')
            sleep(2)
            break
        
