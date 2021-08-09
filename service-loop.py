import subprocess
import shlex
import time
import datetime
import readID as readIDVar


import config
import constants



poll_list = [ True, True ]

point_poll_sucess = True;

ptp_sequence = 6


def writelog(entry, logfile) :
    """
    writelog - write log entry to log file
    to usb drive is exists, otherwise to /tmp
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
    else :
        logdrive = '/tmp/'
    logdrive += logfile
    fout = open(logdrive, 'a')
    fout.write(entry)
    fout.close()

def hex_to_int( value ) :

  return int( value, 16 )


def DecodeDeviceType( device_type_id ) :

  DeviceTypeText = "Unknown"
  
  if ( device_type_id == constants.DEVICE_ID_855_PH ) : 
    DeviceTypeText = "855PH"
  elif ( device_type_id == constants.DEVICE_ID_855_P ) : 
    DeviceTypeText = "855P"
  elif ( device_type_id == constants.DEVICE_ID_855_H ) : 
    DeviceTypeText = "855H"      
  elif ( device_type_id == constants.DEVICE_ID_855_PC ) : 
    DeviceTypeText = "855PC"   
  elif ( device_type_id == 253 ) : 
    DeviceTypeText = "Empty" 
  else :
    DeviceTypeText = "--"
  
  
  return DeviceTypeText


def decode_point_info_reply( packet_to_decode ) : 

    global point_poll_sucess
    
    point_poll_sucess = True

    length = len( packet_to_decode )

    # remove checksum from end
    shorter = packet_to_decode[:length - 3]

    varlist = map(hex_to_int, shorter .split(','));
    
    # remove SOH and sequence number
    varlist.pop(0)
    varlist.pop(0)
    
    print( "\nPoint Information Reply Packet" )

    point_number = varlist[ constants.POINT_REPLY_POINT_ADDRESS_OFFSET ];

    print ( "state       " + str(  varlist[ constants.POINT_REPLY_HIGH_LEVEL_STATUS_OFFSET ] ) + "     Zero = success")
     
    # Dump packet
    #for element in range( len( varlist ) ) :
    #  print ( "[ " + str( element ) + " ]  : " + str( varlist[ element ] ) )


    if ( varlist[ constants.POINT_REPLY_HIGH_LEVEL_STATUS_OFFSET ] == 0 ) : 
       print ( "LOOP :  " + str( varlist[ constants.POINT_REPLY_CHANNEL_ADDRR_OFFSET ] ) + " POINT " +  str( varlist[ constants.POINT_REPLY_POINT_ADDRESS_OFFSET ] ))

       print ( "Flags       " + str( varlist[ constants.POINT_REPLY_FLAGS_OFFSET ] ) )
       print ( "Node        " + str( varlist[ constants.POINT_REPLY_NODE_OFFSET ] ) )
       print ( "Channel     " + str( varlist[ constants.POINT_REPLY_CHANNEL_OFFSET ] ) )
       print ( "Chan addr   " + str( varlist[ constants.POINT_REPLY_CHANNEL_ADDRR_OFFSET ] ) + "    this is the loop number" )
       print ( "Pnt cat     " + str( varlist[ constants.POINT_REPLY_POINT_CATEGORY_OFFSET ] ) )
       print ( "Pnt addr    " + str( varlist[ constants.POINT_REPLY_POINT_ADDRESS_OFFSET ] ) )
       print ( "log part1   " + str( varlist[ constants.POINT_REPLY_LOG_ADDR_PART_1_OFFSET ] ) )
       print ( "log part2   " + str( varlist[ constants.POINT_REPLY_LOG_ADDR_PART_2_OFFSET ] ) )
       
       DeviceTypeAsString = DecodeDeviceType( varlist[ constants.POINT_REPLY_DEVICE_TYPE_OFFSET ] )
       print ( "Device type " + str( varlist[ constants.POINT_REPLY_DEVICE_TYPE_OFFSET ] ) + "    " + DeviceTypeAsString )
       print ( "Attribs     " + str( varlist[ constants.POINT_REPLY_ATTRIBS_OFFSET ] ) )
       print ( "group pt1   " + str( varlist[ constants.POINT_REPLY_GROUP_PT1_OFFSET ] ) )
       print ( "group pt3   " + str( varlist[ constants.POINT_REPLY_GROUP_PT2_OFFSET ] ) )
       print ( "Area type   " + str( varlist[ constants.POINT_REPLY_AREA_TYPE_OFFSET ] ) )
       print ( "Area nmbr   " + str( varlist[ 24 ] ) )
       print ( "Sector      " + str( varlist[ 25 ] ) + "    254 if not sector")
       print ( "Loop type   " + str( varlist[ 26 ] ) + "      1 is MX")
       print ( "raw dev id  " + str( varlist[ 27 ] ) )

       print ( "----" )
    else:
       point_poll_sucess = False
    
    #print( "Full packet reply : " + packet_to_decode )

    
    
def decode_panel_info_reply( packet_to_decode ) :     
    
    global point_poll_sucess
    
    point_poll_sucess = True

    length = len( packet_to_decode )

    # remove checksum from end
    shorter = packet_to_decode[:length - 3]

    varlist = map(hex_to_int, shorter .split(','));
    
    # remove SOH and sequence number
    varlist.pop(0)
    varlist.pop(0)

    print( "\nPanel Information" )
       
    
    # get rid of the header
    varlist.pop(0)
    varlist.pop(0)
    varlist.pop(0)
    varlist.pop(0)
    varlist.pop(0)
    varlist.pop(0)
    varlist.pop(0)
    varlist.pop(0)
    varlist.pop(0)
    
      
    print( "Time Date (secs): " + str(varlist[0]) + " " + str(varlist[1]) + " " + str(varlist[2]) + " " + str( varlist[3]) )
    print( "panel Version   : " + str(varlist[4]) + " " + str(varlist[5]) + " " + str(varlist[6]))
    print( "Days Left Auto  : " + str(varlist[7]) + " "+  str(varlist[8]) )
    print( "Market Channel  : " + str(varlist[9]) )
    print( "Flags           : " + str(varlist[10]) + " " + str(varlist[11]))
    print( "equipment       : " + str(varlist[12]) + " " + str(varlist[13]))
    print( "compat          : " + str(varlist[14]) + " " + str(varlist[15]))
    print( "MXSpeak         : " + str(varlist[16]) + "    - 0 MXspeak 5, 1 MXSpeak 6 " )
      
    print ( "\n" )       
    
def send_packet_after_panel_info( send_packet_after_panel_info ) :

    # Packet type is 209

    # without PTP framing
    # without checksum
    #
 
   
    # length
    # destination node             = 0 local
    # channel                      = 0
    # destination channel address  = 0
    # destination task             - 1 local
    # source channel               = 0
    # source task                  = 0
    # marker                       = any thing - 123
    # packet ID                    = 209
    #
    # DATA
    # ----
    # Control type       = 3 - request project details
    # addtional features = 0

    #               L  D C A D T S  M  PK  c a
    SamplePacket = "11,0,0,0,1,0,0,123,209,3,0"
    

    global ptp_sequence

    varlist = map(int, SamplePacket .split(','));

    length = len( varlist )
    
    packet_to_send = "error"

  
    # Start with SOH and low level sequence number.
    packet_to_send = "1" # + str ( ptp_sequence )

    # Add the PTP sequence number to the packet.
    varlist.insert(0, ptp_sequence)

    ptp_sequence += 1
    if ptp_sequence > 8 : 
     ptp_sequence = 5
    
    checksum = 0
    for el in varlist:
      checksum += el
      packet_to_send += "," + str(el);

    checksum = checksum % 256

    varlist.append( checksum )

    packet_to_send += "," + str(checksum)

    print( "Constructed Packet to Checker connect req info : \n" + packet_to_send )
    
    
    action = "python packetizer/pointinfotest.py " + packet_to_send 


    payload = subprocess.check_output(shlex.split(action));

    if len(payload) > 1: #for some reason printing an empty payload still constitutes to greater than 0, so we use 1 instead
        # writelog(payload,logfile)
        # TODO adjust to windows 7/10
        print("Reply from Panel, Length " + str( len( payload ) ) )
        #print(payload)
        
        if (len(payload) > 10) :
          decode_reply_packet_mxspeak_5(payload) 

        
        print "Payload response to connect info request : \n"+payload; 
    else:
        #print("this is the payload" + str(payload))
        print "No reply",
  
    

    return payload 


def decode_reply_packet_mxspeak_5( packet_to_decode ) :

    length = len( packet_to_decode )

    shorter = packet_to_decode[:length - 3]

    varlist = map(hex_to_int, shorter .split(','));
    
    # remove PTP header info
    varlist.pop(0)
    varlist.pop(0)
    
    
    packet_entry = "Packet to decode : "
    for el in varlist:
      packet_entry +=  str(el) + ","


    print( "Packet to decode : - " + packet_entry )
    
    
    # --------------------
    print ( "\nReply Packet Type (MX5) : " + str( varlist[ constants.OFFSET_FOR_PACKET_TYPE_MXSPEAK_5 ] ) )


    if ( str( varlist[ constants.OFFSET_FOR_PACKET_TYPE_MXSPEAK_5 ] == constants.PACKET_ID_PANEL_INFORMATION )) : 
      decode_panel_info_reply( packet_to_decode ) 
      send_packet_after_panel_info( packet_to_decode )
    else :
      print ( "yyy Reply Packet Type " + str( varlist[ constants.OFFSET_FOR_PACKET_TYPE_MXSPEAK_5 ] ) )




def decode_reply_packet( packet_to_decode ) :

    length = len( packet_to_decode )

    shorter = packet_to_decode[:length - 3]

    varlist = map(hex_to_int, shorter .split(','));

    # remove PTP header info
    varlist.pop(0)
    varlist.pop(0)
    
    # --------------------
    print ( "Reply Packet Type : " + str( varlist[ constants.OFFSET_FOR_PACKET_TYPE_MXSPEAK_6 ] ) )


    if ( str( varlist[ constants.OFFSET_FOR_PACKET_TYPE_MXSPEAK_6 ] == constants.PACKET_ID_POINT_INFO_REPLY )) : 
      decode_point_info_reply( packet_to_decode ) 
    else :
      print ( "Reply Packet Type " + str( varlist[ constants.OFFSET_FOR_PACKET_TYPE_MXSPEAK_6 ] ) )


def FormRequestPacket( loop, point  ) :

    # without PTP framing
    # without checksum
    #
    SamplePacket = "58,228,0,0,0,4,253,146,0,148,0,12,1,0,1,0,254,0,0,1,3,0,0,3,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,127,0,10"

    # With SOH, sequence and checksum
    #          "1,5,58,228,0,0,0,4,253,146,0,148,0,12,1,0,1,0,254,0,0,1,3,0,0,3,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,127,0,10,199"


    global ptp_sequence

    varlist = map(int, SamplePacket .split(','));

    detail_display = 0
    
    
    # to be on the safe side
    # check the packet type.
    
    if ( varlist[ constants.OFFSET_FOR_PACKET_TYPE_MXSPEAK_6 ] == constants.PACKET_ID_POINT_INFO_REQUEST ) : 
        varlist[ constants.POINT_INFO_REQUEST_POINT_OFFSET ] = point
        varlist[ constants.POINT_INFO_REQUEST_LOOP_OFFSET ]  = loop
        
        if ( config.DISPLAY_POINT_REQUEST_PACKETS_OVERVIEW == 1 ) :
            print( "\nRequest -  Loop : " + str( loop ) + ",  Point : " + str( point ) )            

            if ( config.DISPLAY_POINT_REQUEST_PACKETS_DETAIL == 1 ) :
               print ( "Point Information Request : Node      " + str(  varlist[ constants.POINT_INFO_REQUEST_NODE_OFFSET ] ) )
               print ( "Point Information Request : channel   " + str(  varlist[ constants.POINT_INFO_REQUEST_CHANNEL_OFFSET ] )  + "   MXSpeak 6 12 is main processor")
               print ( "Point Information Request : chan addr " + str(  varlist[ constants.POINT_INFO_REQUEST_LOOP_OFFSET ] )  + "   Channel 12, channel addr 1 = loop A")
               print ( "Point Information Request : pnt cat   " + str(  varlist[ constants.POINT_INFO_REQUEST_POINT_CATEGORY_OFFSET ] )  + "   0 - real points")
               print ( "Point Information Request : pnt addr  " + str(  varlist[ constants.POINT_INFO_REQUEST_POINT_OFFSET ] ) )
               print ( "Point Information Request : log pt 1  " + str(  varlist[ constants.POINT_INFO_REQUEST_LOGICAL_ADDR_PT1_OFFSET ] ) )
               print ( "Point Information Request : log pt 2  " + str(  varlist[ constants.POINT_INFO_REQUEST_LOGICAL_ADDR_PT2_OFFSET ] ) )
               print ( "Point Information Request : dev cat   " + str(  varlist[ constants.POINT_INFO_REQUEST_DEVICE_CATEGORY_OFFSET ] ) )

            else: 
               # If here something went wrong.  This function is only for point info request packets.
               print ( "Packet Type " + str(  varlist[ constants.OFFSET_FOR_PACKET_TYPE_MXSPEAK_6 ] ) )


        # Start with SOH and low level sequence number.
        result = "1" # + str ( ptp_sequence )

        # Add the PTP sequence number to the packet.
        varlist.insert(0, ptp_sequence)
 
        ptp_sequence += 1
        if ptp_sequence > 8 : 
         ptp_sequence = 5
        
        checksum = 0
        for el in varlist:

          checksum += el
          result += "," + str(el);

        checksum = checksum % 256

        varlist.append( checksum )


        #print( "Calculated checksum: " + str(checksum))

        result += "," + str(checksum)


    #print( "Constructed Packet to send : \n" + result )

    return result 


def PointInformationScan(   ) :

    # initial dealy between polls while we work out what is there.
    delaybetweenpolls = 0.5


    # 'poll_list' is a store indicating whether we should poll this device, start at TRUE.
    # One store for all loop.  points in loop 1, then loop 2....
    # Indexed by point number, we set '0' as False, this is unused.

    poll_list = [ False ]
    for loop in range( constants.MAX_LOOP_TO_SCAN ) :
        for x in range( constants.MAX_ADDRESSES_PER_LOOP ):
          poll_list.append( True )

    # Declare loop variables, with start values
    point_address = 1
    current_loop  = 1


    while(True):

        startTime = datetime.datetime.now();

        poll_list_index = ((current_loop - 1) * constants.MAX_ADDRESSES_PER_LOOP) + point_address
        
        if ( poll_list[ poll_list_index ] == True ) : 

            #print "Packet in jobs list : \n"+content
            
            # TO DO
            # Not ideal, but adjust the packet for the loop and point address
            packettosend = FormRequestPacket( current_loop, point_address )
            
            #print(  packettosend  )

            action = "python packetizer/pointinfotest.py " + packettosend 
            #print(action)
            payload = subprocess.check_output(shlex.split(action));
            if len(payload) > 1: #for some reason printing an empty payload still constitutes to greater than 0, so we use 1 instead
                # writelog(payload,logfile)
                # TODO adjust to windows 7/10
                print("Reply from Panel, Length " + str( len( payload ) ) )
                #print(payload)
                if (len(payload) > 10) :
                  decode_reply_packet(payload) 
                  if( point_poll_sucess == False) :
                    poll_list[ poll_list_index ] = False
                #print "Payload response to serviced packet : \n"+payload; 
            else:
                #print("this is the payload" + str(payload))
                print "No device recorded for this point",

            time.sleep(delaybetweenpolls) 

        point_address += 1
        
        # If we have got to the end of a loop.
        # start again at the start of the next loop.
        if (point_address >constants.MAX_ADDRESSES_PER_LOOP):         
            point_address = 1

            current_loop += 1
            if (current_loop > constants.MAX_LOOP_TO_SCAN): 
                current_loop = 1

                x = poll_list.count( True )
                print( "Number of devices replying to poll " + str( x ) ) 
                # if very few devices, we need to chill the poll time,
                if (( x * delaybetweenpolls ) < ( min_time_between_polls )) :
                    delaybetweenpolls = min_time_between_polls / x
                    print( "Updated poll time : " + str( delaybetweenpolls ) )
                   
              


def FormCheckerRequestPacket(   ) :

    # Packet type is 26
    # Destination configuration manager = ID 3

    # without PTP framing
    # without checksum
    #
    
    # length
    # destination node             = 0 local
    # channel                      = 0
    # destination channel address  = 0
    # destination task             - 1 local
    # source channel               = 0
    # source task                  = 0
    # marker                       = any thing - 123
    # packet ID                    = 26

    
    #SamplePacket = "16,228,0,0,0,4,253,26,0,12,1,0,1,0,254,0"
    
    #               L D C A D T S  M   PK
    SamplePacket = "9,0,0,0,1,0,0,123,26"

 
    global ptp_sequence

    varlist = map(int, SamplePacket .split(','));

    length = len( varlist )
    
    result = "error"

  
    # Start with SOH and low level sequence number.
    result = "1" # + str ( ptp_sequence )

    # Add the PTP sequence number to the packet.
    varlist.insert(0, ptp_sequence)

    ptp_sequence += 1
    if ptp_sequence > 8 : 
     ptp_sequence = 5
    
    checksum = 0
    for el in varlist:
      checksum += el
      result += "," + str(el);

    checksum = checksum % 256

    varlist.append( checksum )

    result += "," + str(checksum)

    print( "Constructed Packet to send : \n" + result )

    return result 

def CheckerScanMode( ) :

    print( "CHECKER MODE" )

    print( "\nRequest panel info\n")
    RegistrationRequest =  FormCheckerRequestPacket(  ) 
  

    action = "python packetizer/pointinfotest.py " + RegistrationRequest 


    payload = subprocess.check_output(shlex.split(action));
    if len(payload) > 1: #for some reason printing an empty payload still constitutes to greater than 0, so we use 1 instead
        # writelog(payload,logfile)
        # TODO adjust to windows 7/10

        print(payload)
        
        if (len(payload) > 10) :
          decode_reply_packet_mxspeak_5(payload) 
        #  if( point_poll_sucess == False) :
        #    poll_list[ poll_list_index ] = False

    else:
        #print("this is the payload" + str(payload))
        print "No device recorded for this point",
  
  
    if len(payload) == 2:
  
        RegistrationRequest =  FormCheckerRequestPacket(  ) 

        action = "python packetizer/pointinfotest.py " + RegistrationRequest 

        payload = subprocess.check_output(shlex.split(action));
        if len(payload) > 1: #for some reason printing an empty payload still constitutes to greater than 0, so we use 1 instead

            #print(payload)
            
            if (len(payload) > 10) :
              decode_reply_packet_mxspeak_5(payload)(payload) 
         
              
            #  if( point_poll_sucess == False) :
            #    poll_list[ poll_list_index ] = False
            
            print "Payload response to serviced packet : \n"+payload; 
        else:
            #print("this is the payload" + str(payload))
            print "No device recorded for this point",

#
# START OF MAIN
#



delaybetweenpolls = 0.2
min_time_between_polls = 5


pid = readIDVar.readID();
pid = pid.strip()
entry = "Logging Panel Points PI id: " + str(pid) + '\n\n'
print(entry)


logfile = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
logfile += '_BlackBox.log'
# todo, adapt for Windows
print(entry)
# writelog(entry, logfile)


if (config.MODE_IS == config.POINT_INFO_SCAN) : 
  PointInformationScan()


if (config.MODE_IS == config.CHECKER_MODE) : 
  CheckerScanMode()
               


          
