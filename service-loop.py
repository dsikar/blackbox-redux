import subprocess
import shlex
import time
import datetime
import readID as readIDVar
import logging as lg

poll_list = [ True, True ]

point_poll_sucess = True;

def hex_to_int( value ) :

  return int( value, 16 )


def decode_point_info_reply( packet_to_decode ) : 

    global point_poll_sucess
    
    point_poll_sucess = True

    length = len( packet_to_decode )

    shorter = packet_to_decode[:length - 3]

    varlist = map(hex_to_int, shorter .split(','));

    print( "\nPoint Information Reply Packet" )

    point_number = varlist[ 18 ];

    print ( "state       " + str(  varlist[ 12 ] ) + "     Zero = success")


    if ( varlist[ 12 ] == 0) : 
       print ( "LOOP :  " + str(  varlist[ 16 ] ) + " POINT " +  str(  varlist[ 18 ] ))
    
       print ( "Flags       " + str(  varlist[ 13 ] ) )
       print ( "Node        " + str(  varlist[ 14 ] ) )
       print ( "Channel     " + str(  varlist[ 15 ] ) )
       print ( "Chan addr   " + str(  varlist[ 16 ] ) + "    this is the loop number" )
       print ( "Pnt cat     " + str(  varlist[ 17 ] ) )
       print ( "Pnt addr    " + str(  varlist[ 18 ] ) )
       print ( "log part1   " + str(  varlist[ 19 ] ) )
       print ( "log part2   " + str(  varlist[ 20 ] ) )
       print ( "Device type " + str(  varlist[ 21 ] ) )
       print ( "Attribs     " + str(  varlist[ 22 ] ) )
       print ( "group pt1   " + str(  varlist[ 23 ] ) )
       print ( "group pt3   " + str(  varlist[ 24 ] ) )
       print ( "Area type   " + str(  varlist[ 25 ] ) )
       print ( "Area nmbr   " + str(  varlist[ 26 ] ) )
       print ( "Sector      " + str(  varlist[ 27 ] ) + "    254 if not sector")
       print ( "Loop type   " + str(  varlist[ 28 ] ) + "      1 is MX")
       print ( "raw dev id  " + str(  varlist[ 29 ] ))
       print ( "----" )
    else:
       point_poll_sucess = False
    
    #print( "Full packet reply : " + packet_to_decode )



def decode_reply_packet( packet_to_decode ) :

    length = len( packet_to_decode )

    shorter = packet_to_decode[:length - 3]

    varlist = map(hex_to_int, shorter .split(','));

    if ( str( varlist[ 11 ] == 149 )) : 
      decode_point_info_reply( packet_to_decode ) 
    else :
      print ( "Reply Packet Type " + str( varlist[ 11 ] ) )


def FormRequestPacket( loop, point, startpacket ) :

    # print( "Original MSG : " + startpacket )

    varlist = map(int, startpacket .split(','));

    length = len( varlist )
    
    result = "error"

    display = 0
    # to be on the safe side
    # check the packet type.
    if ( varlist[ 11 ] == 148 ) : 
        varlist[ 16 ] = point
        print( "Request Point : " + str( point ) )
        varlist[ 14 ] = loop
        print( "Request Loop  : " + str( loop ) )

        if ( display == 1 ) :
           print ( "Point Information Request : Node      " + str(  varlist[ 12 ] ) )
           print ( "Point Information Request : channel   " + str(  varlist[ 13 ] )  + "   MXSpeak 6 12 is main processor")
           print ( "Point Information Request : chan addr " + str(  varlist[ 14 ] )  + "   Channel 12, channel addr 1 = loop A")
           print ( "Point Information Request : pnt cat   " + str(  varlist[ 15 ] )  + "   0 - real points")
           print ( "Point Information Request : pnt addr  " + str(  varlist[ 16 ] ) )
           print ( "Point Information Request : log a   " + str(  varlist[ 17 ] ) )
           print ( "Point Information Request : log b   " + str(  varlist[ 18 ] ) )
           print ( "Point Information Request : dev cat " + str(  varlist[ 19 ] ) )

        else: 
           print ( "Packet Type " + str(  varlist[ 11 ] ) )

        # remove existing checksum
        varlist.pop( length -1 )
        # remove start of packet info
        varlist.pop( 0 )

        result = str ("1" )
        checksum = 0
        for el in varlist :
          checksum += el
          result += "," + str(el);

        checksum = checksum % 256

        varlist.append( checksum  )

        #print( "Calculated checksum: " + str(checksum))

        result += "," + str(checksum)

        #print( "New MSG : " + result )

    return result 


delaybetweenpolls = 0.2
min_time_between_polls = 5

pid = readIDVar.readID();
pid = pid.strip()
entry = "Logging Panel PI id: " + str(pid) + '\nTODO scan devices, decode packets\n'
print(entry)
f = open('packet.txt')
packets = f.readlines()

logfile = str(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
logfile += '_BlackBox.log'
# todo, adapt for Windows
print(entry)
# lg.writelog(entry, logfile)


# whether we should poll this device.
# form a list of 250 addresses
# set to TRUE, will be set to false if panel indicates point not there.
poll_list = [ False, True, True ]
for x in range(248):
  poll_list.append( True )


point_address = 1
loop = 1
max_point_address = 250

while(True):

    for packet in packets :
        startTime = datetime.datetime.now();


        if (poll_list[ point_address ] == True) : 
            content =  packet #+ '\r\n' #.strip()

            #print "Packet in jobs list : \n"+content
            
            packettosend = FormRequestPacket( loop, point_address , content)

            action = "python packetizer/pointinfotest.py " + packettosend 
            #print(action)
            payload = subprocess.check_output(shlex.split(action));
            if len(payload) > 1: #for some reason printing an empty payload still constitutes to greater than 0, so we use 1 instead
                lg.writelog(payload,logfile)
                # TODO adjust to windows 7/10
                print("Reply from Panel")
                #print(payload)
                if (len(payload) > 10) :
                  decode_reply_packet(payload) 
                  if( point_poll_sucess == False) :
                    poll_list[ point_address ] = False
                #print "Payload response to serviced packet : \n"+payload; 
            else:
                #print("this is the payload" + str(payload))
                print "No device recorded for this point",

            time.sleep(delaybetweenpolls) 

        point_address += 1
        if (point_address > max_point_address):         
          point_address = 1
          #print( poll_list )
          x = poll_list.count( True )
          print( "Number of devices replying to poll " + str( x ) ) 
          # if very few devices, we need to chill the poll time,
          if (( x * delaybetweenpolls ) < ( min_time_between_polls )) :
              delaybetweenpolls = min_time_between_polls / x
              print( "Updated poll time : " + str( delaybetweenpolls ) )
                   
          
