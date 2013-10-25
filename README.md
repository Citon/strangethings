StrangeThings - File extension vs. magic cross checker
-----------------------------------------------------------------------------

"Strange things are afoot at the Circle K..."  This was written as part
of a response to a "CrytpoLocker" ransomware infection.  We wanted to try
and find files that had been encrypted.  Without a signature to go on to
find encrypted files, a script that instead tried to verify extension vs.
magic (in file id) made sense.

The target use for strangethings.py is a UNIX-like fileserver or a test
system with a suspect drive connected.  UNIX helping save Windows...


Requirements:

 * Only tested on Linux/Unix systems so far
 * Requires python-magic


INSTALLATION
------------

 * Install the python-magic package from https://github.com/ahupp/python-magic
 * Decide where you want to store the script and cd to the dir
 * Grab a copy of the latest .tgz

   curl -kL https://github.com/Citon/strangethings/tarball/master \
   	 > strangethings.tgz  

 * Unpack the archive:

   tar xvzf strangethings.tgz

 * Copy the strangethings.py script into ~/bin or somewhere else in your
   path.
 * Make it executable.  Example: If in ~/bin

   chmod 755 ~/bin/strangethings.py


USAGE
-----

 * (Optional) Decide on a list of extensions (suffixes) of files you want
   to include.
 * Run it!  A few examples:
  * Using default suffixes and scanning /home

  strangethings.py /home

  * Scanning /docs and saving the CSV output to /var/tmp/docsscan1.csv

  strangethings.py /docs > /var/tmp/docsscan1.csv

  * Scanning /media/JeffDrive but only looking for files ending in .dll or .exe

  strangethings.py -s dll,exe /media/JeffDrive



EQUIVALENT MIME TYPES
---------------------

Depending on your specific magic lists you may find many files being reported
as not matching that have types you consider equivalent.  For example,
a .css (Cascading Style Sheet) file may be detected as text/html by libmagic.
You can edit the "equivtypes" dictionary inside strangethings.py to add
mappings between the type tied to an extension and the possible libmagic
detected types you want to accept for that extension.

See the strangethings.py source for more information.


LICENSE
-------

See LICENSE.txt for license information.

