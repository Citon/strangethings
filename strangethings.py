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

# Check if we're running Python 2.x, if so set default encoding to UTF-8
# and load the correct configparser module depending on Python version.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
    import ConfigParser
else:
    import configparser

# Requires the python-magic package from https://github.com/ahupp/python-magic
import magic


# Set to 1 for extra status...
DEBUG = 0


def scanner(suffixlist, equivtypes, scandir, excludedirs):
    """
    Scan for any files with a suffix in the suffixlist under scandir.  Matches
    are fed to a magic file check then reverse lookup.  If the MIME type defined
    for the suffix of the file is in the equivtypes dict, the list of equivtypes
    defined for the given MIME type are also considered good.
    """
    
    # Build a regex from the suffixlist
    fileretext = "^.+\.(" + '|'.join(suffixlist) + ")\s*$"
    
    (DEBUG) and (sys.stderr.write("DEBUG: Suffix match pattern: %s\n" % fileretext))

    filere = re.compile(fileretext)

    exclude = set(excludedirs)

    # Walk the directory
    for base, dirs, files in os.walk(scandir, topdown=True):
        # Don't scan directories which are in the exclusion list
        dirs[:] = [d for d in dirs if d not in exclude]
        # Filter for files we care about
        for filename in files:
            if filere.search(filename):
                # Match!
                (DEBUG) and (sys.stderr.write("DEBUG: FOUND %s/%s\n" % (base, filename)))

                # But is it for real?  Check using the full path
                fullpath = os.path.normpath(os.sep.join((base,filename)))
                (sufitype, magitype) = magiccheck(equivtypes, fullpath)

                if sufitype == True:
                    (DEBUG) and (sys.stderr.write("DEBUG: PASSED %s/%s,%s\n" % (base, filename, magitype)))
                else:
                    sys.stdout.write("\"%s\",%s,%s\n" % (fullpath,sufitype,magitype))



def magiccheck(equivtypes, filename):
    """
    Perform a magic file test on filename then compare the magic results to
    the extension on the file.  Returns True and the MIME type if magic
    matches, else returns the supposed MIME type and the detected MIME type.
    Uses the equivtypes dict to allow for multiple magic MIME type results
    to map to a specific extension and still be considered a match.
    """

    try:
        # Collect magic MIME type
        magitype = magic.from_file(filename, mime=True)
        
        # Strip additional parameters (; and after)
        magitype = magitype.split(';')[0]

    except UnicodeDecodeError:
        sys.stderr.write("WARNING: File could not be scanned by magic.  Skipping: %s\n" % filename)
        return (True,"null")

    except OSError as exc:
        if exc.errno == errno.ENOENT:
            sys.stderr.write("WARNING: File disappeared.  Skipping: %s\n" % filename)
            return (True,"null")
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
    parser = optparse.OptionParser(usage="%s [-c CONFFILE] [-s SUFFIXLIST] [-e EXCLUDEDIRS] DIRECTORY" % progname)
    parser.add_option("-c", "--config", dest="conffile", help="Specify configuration file", metavar="FILE")
    parser.add_option("-s", "--suffixlist", dest="suffixlist", help="Choose alternate suffix list from configuration file", metavar="SUFFIXLIST")
    parser.add_option("-e", "--excludedirs", dest="excludedirs", help="Choose list of directoriers to exclude", metavar="EXCLUDEDIRS")

    (options, args) = parser.parse_args()

    # Create an empty equivtypes and excludedirs dict
    equivtypes = {}
    excludedirs = {}

    # Set the default suffixlist to match all known suffixes for our MIME lib
    suffixlists = { "default": []}
    for key in mimetypes.types_map.keys():
        if key[0] == ".":
            key = key[1:]
        suffixlists['default'].append(key)

    # Parse the config file
    if options.conffile:
        # See if you can open this supposed "config file"
        if not os.path.isfile(options.conffile):
            sys.exit("FATAL: Configuration file not found")

        config = ConfigParser.RawConfigParser()
        try:
            config.read(options.conffile)
        except OSError as exc:
            sys.exit("FATAL: Configuration file error: %s\n" % exc)

        if config.has_section('equivtypes'):
            for (ltype, rtypes) in config.items('equivtypes'):
                # Turn CSV lists into arrays and tuck them into our equivlists
                equivtypes[ltype] = rtypes.split(',')

        if config.has_section('suffixlists'):
            for (lname, lval) in config.items('suffixlists'):
                suffixlists[lname] = lval.split(',')

        if config.has_section('excludedirs'):
            for (lsource, ldir) in config.items('excludedirs'):
                excludedirs[lsource] = ldir.split(',')
                
    # There best be a directory defined...
    if len(args) != 1:
        parser.error("DIRECTORY not defined.  What am I supposed to scan?")
    else:
        scandir = args[0]

    # Check for existence of the directory we are scanning
    if not (os.path.exists(scandir) and os.path.isdir(scandir)):
        sys.exit("FATAL: BAD DIRECTORY '%s'\n", scandir)

    # Allow selecting an alternate suffix list
    if options.suffixlist:
        if suffixlists.has_key(options.suffixlist):
            suffixlist = suffixlists[options.suffixlist]
        else:
            sys.exit("FATAL: Specified suffix list %s not defined\n" % options.suffixlist)
    else:
        suffixlist = suffixlists["default"]
    
    # Allow to exclude a list of directories from the search
    if options.excludedirs:
        if excludedirs.has_key(options.excludedirs):
            excludedirs = excludedirs[options.excludedirs]
        else:
            sys.exit("FATAL: Specified directory exclusion list %s not defined\n" % options.excludedirs)
    
    # Scan it
    sys.stderr.write("Starting scan of %s\n" % scandir)
    sys.stdout.write("FILENAME,SUFFIX_TYPE,MAGIC_TYPE\n")
    scanner(suffixlist, equivtypes, scandir)
    sys.stderr.write("Completed scan of %s\n" % scandir)
    
    exit(0)


if __name__ == '__main__':
    main()


