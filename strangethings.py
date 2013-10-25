#!/usr/bin/python

# strangethings.py - Strange Things Are Afoot At The Circle K.
#                    Scan a file structure for files with an extension
#                    that does not match the results of a libmagic "file"
#                    test.  Does not prove a file is bad, just that the
#                    filename and what is inside appear not to match.

# Copyright(c) 2013, Citon Computer Corporation
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of CITON COMPUTER CORPORATION nor the names of
#    its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Author: Paul Hirsch

# Imports
import sys, os, errno, re, optparse, mimetypes

# Requires the python-magic package from https://github.com/ahupp/python-magic
import magic


# Set to 1 for extra status...
DEBUG = 0

# Since type matching is not a science, much less a perfect one, you can
# use the typegroups dict to create lists of MIME types that should be
# treated as equivalent.  The key for each should be the type related to
# the suffix and the value should be a list of acceptable equivalents.
# Example:  "text/css": ["text/html", "text/plain"]
equivtypes = {
    "text/css": ["text/html"],
    "text/html": ["text/plain"]
    }


def scanner(suffixlist, scandir):
    """
    Scan for any files with a suffix in the suffixlist under scandir.  Matches
    are fed to a magic file check then reverse lookup.
    """
    
    # Build a regex from the suffixlist
    fileretext = "^.+\.(" + '|'.join(suffixlist) + ")\s*$"
    
    (DEBUG) and (sys.stderr.write("DEBUG: Suffix match pattern: %s\n" % fileretext))

    filere = re.compile(fileretext)

    # Walk the directory
    for base, dirs, files in os.walk(scandir):
        # Filter for files we care about
        for filename in files:
            if filere.search(filename):
                # Match!
                (DEBUG) and (sys.stderr.write("DEBUG: FOUND %s/%s\n" % (base, filename)))

                # But is it for real?  Check using the full path
                fullpath = os.path.normpath(os.sep.join((base,filename)))
                (sufitype, magitype) = magiccheck(fullpath)

                if sufitype == True:
                    (DEBUG) and (sys.stderr.write("DEBUG: PASSED %s/%s,%s\n" % (base, filename, magitype)))
                else:
                    sys.stdout.write("\"%s\",%s,%s\n" % (fullpath,sufitype,magitype))



def magiccheck(filename):
    """
    Perform a magic file test on filename then compare the magic results to
    the extension on the file.  Returns True and the MIME type if magic
    matches, else returns the supposed MIME type and the detected MIME type.
    """

    try:
        # Collect magic MIME type
        magitype = magic.from_file(filename, mime=True)
        
        # Strip additional parameters (; and after)
        magitype = magitype.split(';')[0]

    except OSError as exc:
        if exc.errno == errno.ENOENT:
            sys.stderr.write("WARNING: File disappeared.  Skipping: %s\n" % filename)
            return (TRUE,"null")
        else:
            raise

    # Figure out the file's suffix
    sufi = "." + filename.split(".")[-1]

    # Now the real magic: Is the file's suffix in the list of valid suffixes
    # for the MIME type?
    if sufi in mimetypes.guess_all_extensions(magitype):
        return (True, magitype)

    # Do a MIME lookup on the extension
    if mimetypes.types_map.has_key(sufi):
        sufitype = mimetypes.types_map[sufi]
    else:
        sufitype = "unknown"

    # Run through our equivtypes table to see if this is an equivalent
    # (acceptable) mismatch
    if (equivtypes.has_key(sufitype) and (magitype in equivtypes[sufitype])):
        return (True, magitype)
    
    # No dice - Return mismatch
    return (sufitype,magitype)



def main():

    # Process command line options
    progname = os.path.basename(__file__)
    parser = optparse.OptionParser(usage="%s [-s SUFFIXLIST] DIRECTORY" % progname)
    parser.add_option("-s", "--suffixlist", dest="suffixraw", help="Specify list of suffixes to scan (separated by comma)", metavar="SUFFIXLIST")
    (options, args) = parser.parse_args()

    if options.suffixraw:
        # Translate a CSV list to a python list
        suffixtemp = options.suffixraw.lower().split(",")

    else:
        # Set a default suffix list based solely on what we can supposedly
        # parse
        suffixtemp = mimetypes.types_map.keys()

    # Post process the suffixlist - The Mime libs assume a . at the beginning.
    # We strip the dot
    suffixlist = []
    for item in suffixtemp:
        if item[0] == ".":
            # Ditch the dot
            item = item[1:]

        suffixlist.append(item)

    # There best be a directory defined...
    if len(args) != 1:
        parser.error("DIRECTORY not defined.  What am I supposed to scan?")
    else:
        scandir = args[0]

    # Check for existence of the directory we are scanning
    if not (os.path.exists(scandir) and os.path.isdir(scandir)):
        sys.exit("BAD DIRECTORY '%s'", scandir)

    
    # Scan it
    sys.stderr.write("Starting scan of %s\n" % scandir)
    sys.stdout.write("FILENAME,SUFFIX_TYPE,MAGIC_TYPE\n")
    scanner(suffixlist, scandir)
    sys.stderr.write("Completed scan of %s\n" % scandir)
    
    exit(0)


if __name__ == '__main__':
    main()

