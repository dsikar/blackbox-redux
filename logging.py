# Logging utility functions
import subprocess
import conf

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
    cnmd = ''
    out = subprocess.check_output(['ls', '/media/pi'])

    if len(out) > 0 :
        logdrive = '/media/pi/' + out
        logdrive = logdrive.rstrip('\n')
        logdrive += '/'
        conf.state = 'BLINKING'
    else :
        logdrive = '/tmp/'
        conf.state = 'SOLID'

    if(conf.prev_state != conf.state) :
        conf.run_cmd = True
        if conf.state == 'SOLID' :
            conf.cmd = 'echo none > /sys/class/leds/led0/trigger'
        else : # BLINKING
            conf.cmd = 'echo heartbeat > /sys/class/leds/led0/trigger'
        conf.prev_state = conf.state

    if conf.run_cmd == True :
        cmd = conf.cmd
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print("output: ", output)
        print("error: ". error)
        conf.run_cmd = False

    logdrive += logfile

    if conf.DEBUG == False :
        fout = open(logdrive, 'a')
        fout.write(entry)
        fout.close()