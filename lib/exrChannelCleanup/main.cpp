//----------------------------------------------------------------------------
//
// Cleanup redundant RGBA channels.
//
//----------------------------------------------------------------------------

#include "exr_channel_cleanup.h"
#include <iostream>
#include <exception>
#include <string>
#include <cstdlib>
#include <cstring>

using namespace std;

namespace
{

    void
	usageMessage (const char argv0[], bool verbose = false)
	{
		cerr << "usage: " << argv0 << " [options] infile outfile" << endl;
		if (verbose)
		{
			cerr << "\n"
					"# ------ EXR CHANNEL CLEANUP TOOL ------ #\n"
					"\n"
					"Reads in a converted OpenEXR image from infile and\n"
					"cleans up the channels inside each layer of the EXR \n"
					"image and saves the result in outfile.\n"
					"\n"
					"If an outfile is not specified, it will overwrite the\n"
					"infile EXR image.\n"
					"\n"
					"Options:\n"
					"-v       verbose mode\n"
					"-h       help\n";
			cerr << endl;
		} exit(1); // Exit While Loop
    }
}

int
main(int argc, char** argv)
{
	string inFile = "";
	string outFile = "";
	bool verbose = false;

	//
	// Parse the command line.
	//

	if (argc < 2)
		usageMessage (argv[0], true);

	int i = 1;
	while (i < argc)
	{
		if (!strcmp(argv[i], "-v")) {
			//
			// Verbose Mode
			//
			verbose = true;
			i += 1;
		}
		if (!strcmp(argv[i], "-h")) {
			//
			// Print Help Message
			//
			usageMessage(argv[0], true);
		}
		else
		{
			//
			// Image File Name
			//
			if (inFile == "")
				inFile = argv[i];
			else
				outFile = argv[i];
			i += 1;
		}
	}

	if (inFile == "")
		usageMessage (argv[0]);

	//
	// Overwrite inFile if no outFile specified
	//

	if (outFile == "")
		outFile = inFile;

	//
	// Load inFile and Start Cleanup
	//

	int exitStatus = 0;
	try
	{
		exr_channel_cleanup(inFile, outFile, verbose);
	}
	catch (const exception& e)
	{
		cerr << e.what() << endl;
		exitStatus = 1;
	}

	return exitStatus;
}
