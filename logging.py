# Logging utility functions

# TODO make this a class
# for now use global variables

# LED States, solid or blinking
curr_state = 'SOLID'
prev_state = 'BLINKING'
state = 'SOLID'

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
    logdrive = ''
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
        if state == 'SOLID' :

        else : # BLINKING
            
    logdrive += logfile
    fout = open(logdrive, 'a')
    fout.write(entry)
    fout.close()