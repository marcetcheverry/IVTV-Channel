#! /usr/bin/env python
# -*- coding: utf8 -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# ivtv-channel: tool to change the channel on an ivtv device.
# Copyright 2006, 2007 Marc E. <santusmarc_at_gmail.com>.
# http://www.jardinpresente.com.ar/svn/utiles/tags/scripts/ivtv-channel/
# http://ivtvdriver.org/index.php/Ivtv-channel
#
# Description:
# It works by comparing the frequencies from ivtvctl (or v4l2-ctl) and the table in 
# ivtv-tune. Currently tested with us_cable frequency table.
#
# Version: 0.6 $Id: ivtv-channel.py 108 2007-05-31 17:33:03Z marc $
#
# Usage:
# ivtv-channel (version|up|down|last|channel_no)
#
# Requirements:
# Python >= 2.4
# Ivtv utilities >= 0.4
# NOTE: As far as I know its compatible all the way back to 0.4, either way, it detects the major API change in 0.8 and works automatically accross all recent versions.

# Changelog:
# 5/31/07
# 0.6  - Automatically check and adapt to all ivtv versions, updated usage string, handle '0' inputs as invalid. Fix console inputs for >10 channels in the first instance. Also fix 0x channels in first instance. Add an 'enter' option to change channels more quickly. 
#
# 0.5.2.1 - Updated email address, web and wiki urls, fix parsing error
#
# 5/30/07
# 0.5.2 - Included GPL license (applies to all releases), cleaned up comments and code, 
#         layed down preliminary work for ivtv version checking and fixed Python version checking.
#
# 5/28/07
# 0.5.1 - Minor bugfixes, changed comments and easier support for legacy ivtv
#
# 5/25/07
# 0.5   - Updated to work with ivtv API 0.10 (Thanks to Daniel M.)
#
# 12/30/06 
# 0.4   - Simplified debugging controls, added option to specify a device file
#         to use, added an extra ivtv arguments option, fixed bug 
#         when the first channel is 0 and no second channel is pressed. Added
#         option to display version number. Added preliminary support for CC/VBI.
#
# 12/28/06
# 0.3.1 - Fixed a bug that did not let users to change to channels which
#         ended in a 0. Thanks David R.
#
# 0.3   - Added support for going back to the last channel, improved log
#	  messages, added command return error code checking (ivtv-utils).
#
# 0.2   - Minor improvements and standarization of logging
#
# 09/2006
# 0.1   - Initial release

# Lirc integration:
# The following is an example into how to integrate this script with LIRC.
# Execute irexec & to make it work.
#--------------------------------------------------
# File: ~/.lircrc (This works with the Hauppage 350 grey remote)
#--------------------------------------------------
# begin
#     button = Ch+
#     prog = irexec
#     config = python /path/to/ivtv-channel.py up
# end
# begin
# 	button = Ch-
# 	prog = irexec
#	config = python /path/to/ivtv-channel.py down
# end
# begin
# 	button = Prev.Ch
# 	prog = irexec
#	config = python /path/to/ivtv-channel.py last
# end
# begin
# 	button = OK
# 	prog = irexec
#	config = python /path/to/ivtv-channel.py enter
# end
# begin
# 	button = 0
#	prog = irexec
#	config = python /path/to/ivtv-channel.py 0 &
# end
# begin
# 	button = 1
#	prog = irexec
#	config = python /path/to/ivtv-channel.py 1 &
# end
# begin
# 	button = 2
#	prog = irexec
#	config = python /path/to/ivtv-channel.py 2 &
# end
# begin
# 	button = 3
#	prog = irexec
#	config = python /path/to/ivtv-channel.py 3 &
# end
# begin
# 	button = 4
#	prog = irexec
#	config = python /path/to/ivtv-channel.py 4 &
# end
# begin
# 	button = 5
#	prog = irexec
#	config = python /path/to/ivtv-channel.py 5 &
# end
# begin
# 	button = 6
#	prog = irexec
#	config = python /path/to/ivtv-channel.py 6 &
# end
# begin
# 	button = 7
#	prog = irexec
#	config = python /path/to/ivtv-channel.py 7 &
# end
# begin
# 	button = 8
#	prog = irexec
#	config = python /path/to/ivtv-channel.py 8 &
# end
# begin
# 	button = 9
#	prog = irexec
#	config = python /path/to/ivtv-channel.py 9 &
# end
#-------------------------------------------------- 

# Reporting Bugs:
# Please report all bugs and feature requests to <santusmarc_at_gmail.com> and make sure to
# include the following:
#
#  * Your .lircrc file (if it differs from my recommendation, if not, please double check it before reporting a bug)
#  * The distribution you are running, python version, ivtv version and version of this script (see version option)
#  * Details about what card/remote controler you are running, and the version of lirc and its source 
#    (i.e, official, or from your distribution)
#  * A full output of the problem with ivtv-channel verbosity variable set to True (see below).
#
# For Developers:
# This script does support changing to channels > 10 by using pickle and datetime
# to serialize timestamps into a /tmp file and comparing them. When two processes 
# of this script are run asynchronously (see the & in the .lircrc example) they manage 
# to check through a series of tests and timeouts if another button was pressed, or
# the alloted time has passed. Anyhow, all you need to know is that it works, and if 
# you want, you can change the waiting periods by editing the code, though I do not recommend
# it, as 3 seconds between each button press works fine.
#
# The code for getting the last button works by using pickle and a list of the last two channels
# tuned.
#
# The verbosity of the script can be changed through a variable at the beginning
# of the code.
# 
# I thought about using PyLirc, but I wanted to reduce dependencies to a minimum.
#
# TODO: 
# Implement VBI/CC support.
# Implement an option to get the currently tuned channel.
# Recomment and cleanup the code of so much typecasting

import sys, os, subprocess, datetime, pickle, time

# Please specify a device file to use with ivtv (the default should work fine in most circumstances)
device = "/dev/video0"

# Change it to True if you want the script to be verbose (output debugging information)
verbose = False

# Only for advanced users, this applies extra flags to the ivtv-tune and ivtctl commands 
# executed from this script
arguments = ""

version = "0.6"

def usage():
    """ Prints the usage of the application. """
    print "Usage: ivtv-tune (up|down|last|enter|channel number)"
    sys.exit(1)

def die(instance):
    """ Quit the script. """
    print "ivtv-channel[%s]: quitting" % str(instance)
    sys.exit(1)

def log(msg, instance, app=False):
    """ Print messages to the console with the instance number. """
    if app and msg: print "ivtv-channel[%d]: %s:" % (instance,app), msg
    elif msg:	print "ivtv-channel[%d]:" % (instance), msg

def ivtvversion(command="ivtvctl", args="--version"):
    """ Returns a list of the major minor version numbers of ivtv utilities in integers. """
    return map(int, subprocess.Popen("%s %s" % (str(command), str(args)), shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read().split()[2].split('.'))

def checkchannel(channel, list, instance):
    """ Check if the channel is in the frequency table. """
    # Allow things like 06 and 60
    if int(channel) != 0:
        if not dict([(v,k) for k,v in list.iteritems()]).has_key(channel):
    	    if verbose: log("Invalid channel (not in frequency table)", instance)
    	    sys.exit(1)
    else:
        if verbose: log("0 is not an allowed channel", instance)

def getchannel():
    """ Return an int with the currently tuned channel. """
    #TODO: Implement
    pass

def toggleCc(instance):
    """ Toggle Closed Captioning (VBI) """
    # TODO: Implement
    pass

def changeChannel(channel, switch, instance):
    """ Call ivtv-tune with the given channel number and switch (up/down/number. """
    if (switch == "up"): channel += 1
    elif (switch == "down"): channel -= 1
    elif (switch == "last"): 
	if verbose: log("Switching to last channel", instance)

	# See
    	if os.path.exists("/tmp/ivtv-channel.last"):
	    ctup = pickle.load(open("/tmp/ivtv-channel.last", "rb"))
	    if len(ctup) > 1:
		channel = ctup[0]
	    else:
		sys.exit(0)
	
    change = subprocess.Popen("ivtv-tune %s --device=%s -c %s " % (str(arguments), str(device), str(channel)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Add check for output
    if verbose: log("Tuned to channel %s" % (channel), instance)
    # Write the current channel
    ctup = []
    if os.path.exists("/tmp/ivtv-channel.last"):
	    if verbose: log("Found tuned channel list",instance)
	    ctup = pickle.load(open("/tmp/ivtv-channel.last", "rb"))
	    # Limit the list to two channels (last, current)
	    if len(ctup) >= 2:
	    	lasti = ctup[-1]
		ctup = []
		ctup.append(str(lasti))
		ctup.append(str(channel))
	    else:
	    	if verbose: log("Less than two channels in tuned list, adding second", instance)
		ctup.append(str(channel))
    else:
    	if verbose: log("Tuned channel list does not exist",instance)
    	ctup.append(str(channel))

    pickle.dump(ctup,open("/tmp/ivtv-channel.last", "wb"))
    if verbose: log("Wrote channel tuned list", instance)

    # Check again for our returncode, dont rely on the async Popen call.
    change.returncode = change.poll()
    if change.returncode not in (None, 0) or verbose: 
	log("".join(line.strip() for line in change.stderr if line), instance, "ivtv-tune")
	log("".join(line.strip() for line in change.stdout if line), instance, "ivtv-tune")
	if change.returncode not in (None, 0):
	    die(instance)

    if verbose: log("".join(line.strip() for line in change.stdout if line), instance,"ivtv-tune")

def main():
    # See if we are the first or second instance
    instance = 0
    if os.path.exists('/tmp/ivtv-channel.time'): instance = 1

    # Get our frequency table
    result = subprocess.Popen("ivtv-tune %s -l --device=%s" % (str(arguments), str(device)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Get our lines into a dict
    frequencytable = {}

    for line in result.stdout:
    	line = line.strip().split()
        frequencytable[line[1]] = line[0]

    # Check again for our returncode, dont rely on the async Popen call.
    result.returncode = result.poll()
    if result.returncode not in (None, 0) or verbose: 
	log("".join(line.strip() for line in result.stderr if line), instance, "ivtv-tune")
	if result.returncode not in (None, 0):
	    die(instance)

    # Get our current tuned frequency
    if legacyivtv is False:
        cfrequency = subprocess.Popen("v4l2-ctl %s -F --device=%s" % (str(arguments), str(device)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        cfrequency = subprocess.Popen("ivtvctl %s -R --device=%s" % (str(arguments), str(device)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check again for our returncode, dont rely on the async Popen call.
    cfrequency.returncode = cfrequency.poll()
    if cfrequency.returncode not in (None, 0) or verbose: 
        if legacyivtv is False:
            log("".join(line.strip() for line in cfrequency.stderr if line), instance, "v4l2-ctl")
        else:
            log("".join(line.strip() for line in cfrequency.stderr if line), instance, "ivtvctl")
	if cfrequency.returncode not in (None, 0):
	    die(instance)

    # Parse out the number and convert it to ivtv-tune's format (n/16 on us-cable, might be n*16 on others)
    try:
        if legacyivtv is False:
            freqnumber = int(cfrequency.stdout.readlines()[0].split(' ')[1].replace('\n', '').strip()) / 16.0
        else:
            freqnumber = int(cfrequency.stdout.readlines()[1].split('=')[1].replace('\n', '').strip()) / 16.0
    except IndexError:
        if legacyivtv is False:
            log("Fatal error parsing frequency table. If you are using a device other than the default (/dev/video0), please edit the script and specify it. If you can obtain a frequency table by executing 'v4l2-ctl -F', then please submit a bug report (see header of script).", instance)
        else:
            log("Fatal error parsing frequency table. If you are using a device other than the default (/dev/video0), please edit the script and specify it. If you can obtain a frequency table by executing 'ivtvctl -R', then please submit a bug report (see header of script).", instance)
        sys.exit(1)
    # Check our table with our formatted our frequency and return a channel int
    channel = int(frequencytable["%0.3f" % freqnumber])

    # Parse our arguments
    if (len(sys.argv) > 2 or len(sys.argv) < 2):
	usage()
    else:
        # Begin real operation with channels
        option = sys.argv[-1]
	if option not in ['up','down', 'last', 'version', 'cc']:
            # channel is the instance's integer
            # tchannel is a > 10 channel (second integer) used in instance 1 for checking
            channel = option
            tchannel = option
            option = "none"

	    # Check if the channel is in our frequency table
            # If this is the second instance, also load the previous channel, unless enter is pressed.
            if instance == 1:
                timestampfile = open('/tmp/ivtv-channel.time', 'rb')
                lastkey = pickle.load(timestampfile)
                if channel == 'enter':
                    tchannel = str(lastkey[1])
                    # Cant tune to 0
                    if int(tchannel) == 0:
                        if verbose: log("Can not tune to channel 0", instance)
                        sys.exit(0)
                else:
                    tchannel = str(lastkey[1]) + str(channel)
                    if int(tchannel) == 00:
                            sys.exit(0)
                # For things like 07
                if str(tchannel).startswith("0"):
                    tchannel = tchannel[1:]
            else:
                # First instance cant have 'enter'
                if channel == 'enter':
                    if verbose: log("Enter does nothing without a previous channel.", instance)
                    sys.exit(0)
                # For console usage, example "05" on first instance, then skip everything
                if channel.startswith("0") and int(channel) != 0:
                    if verbose: log("First instance channel from the console", instance)
                    tchannel = channel[1:]
                    checkchannel(tchannel,frequencytable, instance)
    	    	    changeChannel(tchannel, str(option), instance)
                    sys.exit(0)

            checkchannel(tchannel,frequencytable, instance)

	    # Handle channels with more than two characters, <10 per instance
            if channel == "enter" or int(channel) < 10:
		if verbose: log("Entering multi-button mode", instance)
	    	# Get our timestamp
	    	now = datetime.datetime.now()
	    	keynow = [now, channel]
	    	
	    	# Unexistant file (first keypress and instance)
	    	if instance == 0:
		    if verbose: log("Creating timed button press file", instance)
		    timestampfile = open('/tmp/ivtv-channel.time', 'wb')
		    pickle.dump(keynow,timestampfile)
	    	    timestampfile.close()
		    # Wait for another ivtv-channel process to press the second button and delete the file 
		    # if another instance did not (no second button)
		    # Within this period another instance should go to the else clause within
		    # this conditional scope
		    if verbose: log("Waiting for another button...", instance)
		    time.sleep(3)
		    # Check again if another instance deleted it, if not, change the channel and do so to 
		    # restart the process
                    # Dont change the channel if only 0 was received
                    if os.path.exists('/tmp/ivtv-channel.time'):
                        if int(channel) != 0:
                            if verbose: log("No second button, changing channel!", instance)
                            changeChannel(channel, str(option), instance)
                        else:
                            if verbose: log("Not tuning to invalid channel: 0", instance)
                        os.remove('/tmp/ivtv-channel.time')
                    else:
		    	if verbose: log("Another button was pressed by ivtv-channel[1]!", instance)
	    	# Second keypress
	    	else:
		    if verbose: log("This is the second button being pressed", instance)
		    
                    # The timestamp file is loaded before checking the channel to avoid a bug when 
                    # having 0 as the second keypress (the last int is only checked, doesnt match the
                    # frequency table, and dies at function checkchannel()
		    
                    # Was it less than 3 seconds ago? (first keypress?)
		    difference = now - lastkey[0]
		    if difference.seconds < 3:
                        # Enter keypress check
                        if channel == "enter":
                            if verbose: log("Enter pressed, using first channel", instance)
			if verbose: log("Keypresses were within 3 seconds! Changing to channel", instance)
		    else:
			if verbose: log("Too old, difference is " + str(difference.seconds), instance)
    	    	    changeChannel(tchannel, str(option), instance)
		    # Delete the file
		    os.remove('/tmp/ivtv-channel.time')
		    timestampfile.close()
            # First instance received something like '25' (>10), example: console use.
            else:
                changeChannel(channel, str(option), instance)

        elif option == "cc":
            toggleCc(instance)
        elif option == "version":
            log("Version: %s" % (str(version)), instance)
        else:
	    # Normal up/down
	    changeChannel(channel, str(option), instance)

if __name__ == '__main__':
    # Check python and ivtv versions
    if int(sys.version.split()[0].split('.')[1]) < 4:
        print "Python 2.4 is needed for this script, Python %s installed" % (sys.version.split()[0])
        sys.exit(1)

    # v4l2-ctl was added in 0.8.0, everything before that is legacy
    legacyivtv = False
    if ivtvversion()[1] < 8:
        legacyivtv = True

    main()
