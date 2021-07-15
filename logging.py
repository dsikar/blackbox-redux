# Logging utility functions
import subprocess
import conf

# TODO make this a class
# for now use global variables

# LED States, solid or blinking
curr_state = 'SOLID'
prev_state = 'BLINKING'
state = 'SOLID'
run_cmd = False

def writelog(entry, logfile) :
    """
    writelog - write log entry to log file
    to usb drive is exists, otherwise to /tmp,
    setting LED to blinking or solid to reflect
    the action.
    Input
        entry: string, log entry
        logfile: string, log file
    Output
        none
    """
    # where to log
    logdrive = ''
    # LED blinking command
    cmd = ''
    out = subprocess.check_output(['ls', '/media/pi'])
    if len(out) > 0 :
        logdrive = '/media/pi/' + out
        logdrive = logdrive.rstrip('\n')
        logdrive += '/'
        state = 'BLINKING'
    else :
        logdrive = '/tmp/'
        state = 'SOLID'

    if(prev_state != state) :
        run_cmd = True
        if state == 'SOLID' :
            cmd = 'echo none > /sys/class/leds/led0/trigger'
        else : # BLINKING
            cmd = 'echo heartbeat > /sys/class/leds/led0/trigger'
        prev_state = state

    if run_cmd == True :
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print("output: ", output)
        print("error: ". error)
        run_cmd = False

    logdrive += logfile

    if conf.DEBUG == False :
        fout = open(logdrive, 'a')
        fout.write(entry)
        fout.close()