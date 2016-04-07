StrangeThings - File extension type vs. "magic" detected type cross checker
-----------------------------------------------------------------------------

"Strange things are afoot at the Circle K..."  -Ted 'Theodore' Logan

StrangeThings was written as part of a response to a "CrytpoLocker" ransomware
infection.  We wanted to try and find files that had been encrypted.  Without
reliable way to identify encrypted files, a script that instead tried to verify
extension vs. magic (in file id) made sense.

How accurate is this method?  It depends.  If your /usr/share/magic file is
fresh and you are scanning drives with fairly typical files, it is pretty
decent.  If you have invented your own binary document format then StrangeThings
won't have a clue.  (Unless you add it to your system's magic file.)

The target use for strangethings.py is a UNIX-like fileserver or a test
system with a suspect drive connected.  UNIX saving Windows...


Requirements:

 * Python 2.6 or higher
 * Linux/Unix systems, though it could be ported...
 * Requires python-magic

INSTALLATION
------------

 * Install the python-magic package from https://github.com/ahupp/python-magic
 * Decide where you want to store the script and cd to the dir
 * Grab a copy of the latest .tgz

   curl -kL https://github.com/Citon/strangethings/tarball/master > strangethings.tgz  

 * Unpack the archive:

   tar xvzf strangethings.tgz

 * Copy the strangethings.py script into ~/bin or somewhere else in your
   path.
 * Make it executable.  Example: If in ~/bin

   chmod 755 ~/bin/strangethings.py

 * Copy the included strangethings.conf-SAMPLE to strangething.conf (or
   whatever you want to call it) and place it somewhere like /etc.

 * Edit your strangethings.conf as needed.  You can modify:

  * equivlists - This section lets you define a list of acceptable "MAGICTYPE"
                 detected MIME types for a given "SUFFIXTYPE" MIME type.
                 (The script outputs lines as FILENAME,SUFFIXTYPE,MAGICTYPE)
 		 See EQUIVALENT MIME TYPES for more information.
 
  * prefixlists - This section lets you define named lists of suffixes that
                  you can then select using the -s SUFFIXLIST option.  The
                  example includes a list for "cryptolocker" which includes
                  all prefixes known to be hit by the October 2013 version
                  of CryptoLocker.

 * excludelists - This section lets you define lists of directory components
                  to skip. This is most useful for things like /proc or
                  the special ~snapshot directory in a NetApp.
 
USAGE
-----

  * Using default suffixes and scanning /home

  strangethings.py /home

  * Scanning /docs using the config file /etc/strangethings.conf and saving
    the CSV output to /var/tmp/docsscan1.csv

  strangethings.py -c /etc/strangethings.conf /docs > /var/tmp/docsscan1.csv

  * Scanning /media/JeffDrive but only looking for files that match our
    "windowsbin" prefix list in ~/mystrangethings.conf :

  strangethings.py -c ~/mystrangethings.conf -s windowsbin /media/JeffDrive

  * Scanning /na01/homes but only looking for files that match our
    "docs" prefix list in /etc/strange.conf and skipping the
    NetApp snapshots.  (Assumes an exclidelist entry of netapp = ~snapshot)

  strangethings.py -c /etc/strange.conf -s docs -e netapp /na01/homes


EQUIVALENT MIME TYPES
---------------------

Depending on your specific magic lists you may find many files being reported
as not matching that have types you consider equivalent.  For example,
a .css (Cascading Style Sheet) file may be detected as text/html by libmagic.

You can add lines to the equivlists section of your configuration file to set
mappings between the type tied to an extension and the possible libmagic
detected types you want to accept for that extension.



LICENSE
-------

See LICENSE.txt for license information.


