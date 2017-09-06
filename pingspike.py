import balloontip as bt
import time
import pyping
from configobj import ConfigObj

config = ConfigObj('config.ini')
if len(config) is 0:
    print "config.ini not found, exiting..."
    exit()

counter = 0 # used to keep track of consecutive ping failures
isUp = True

while True:
    try:
        response = pyping.ping(config['targetAddress'])
    except:
        print "Host unreachable."
        time.sleep(10)
        continue
    # time formatting for console output
    timeString = time.strftime("%H:%M:%S", time.localtime())
    time.sleep(5)


    if response.ret_code is not 0 or response.avg_rtt is None:
        # ping timed out, so write to console and inc counter
        counter += 1
        if isUp:
            if counter < config['maxCounter']:
                print "TIMEOUT #" + str(counter) + " at " + timeString
                if config.as_bool('timeoutNotify'):
                    bt.balloon_tip('Ping Spike', 'Response timed out.')
            else:
                isUp = False
                print "INTERNET DOWN! Multiple timeouts at: " + timeString
                if config.as_bool('downNotify'):
                    bt.balloon_tip('Ping Spike', 'Internet down!')

    # notify if ping is high, but not timed out
    elif float(response.avg_rtt) >= config.as_float('avgPing'):
        print "HIGH PING: " + response.avg_rtt + " at " + timeString
        if config.as_bool('spikeNotify'):
            bt.balloon_tip('Ping Spike', 'Average ping is ' + response.avg_rtt)

    else:
        if not isUp:
            counter -= 1
            if counter is 0:
                print "INTERNET BACK! No timeout at: " + timeString
                isUp = True
        else:
            counter = 0
