//----------------------------------------------------------------------------
//
// Cleanup redundant RGBA channels.
//
//----------------------------------------------------------------------------

#include "exr_channel_cleanup.h"
#include "image.h"
#include <ImfOutputFile.h>
#include <ImfInputFile.h>
#include <ImfChannelList.h>
#include <boost/regex.hpp>
#include <string>
#include <map>

using namespace Imf;
using namespace Imath;
using namespace std;

void
exr_channel_cleanup(string inFileName, string outFileName, bool verbose)
{
	Header header;
	Image image;
        FrameBuffer outFb;

	boost::regex RED_CHANNEL_MATCH("([a-zA-Z0-9_]+).([Rred]+)");
	boost::regex RGBA_CHANNEL_MATCH("([RGBA])");

	// channel lists
	ChannelList new_channels;
	ChannelList alpha_channels;

	// Find the size of the dataWindow
	Box2i d;
	{
		InputFile in (inFileName.c_str());
		header = in.header();
		d = header.dataWindow();
	}

		image.resize(d);
		header.dataWindow() = d;

	// blow away channels;, we'll rebuild them
	header.channels() = ChannelList();
	
	// Read the input image files
	{
		InputFile in (inFileName.c_str());

		if (verbose)
		{
			cout << "reading file " << inFileName << endl;
		}

		FrameBuffer inFb;
		string tempOutChanName;
		string channelPeriodDelimiter = ".";
		string channelUnderscoreDelimiter = "mat_";

		for (ChannelList::ConstIterator j = in.header().channels().begin();
		     j != in.header().channels().end();
		     ++j)
		{
			const Channel &inChannel = j.channel();

			string tempInChanName = j.name();
			const char* inChanName = tempInChanName.c_str();

			// custom channel name
			string channelToken = tempInChanName.substr(0, tempInChanName.find(channelPeriodDelimiter));

			// remove mat_
			if (strstr(channelToken.c_str(), channelUnderscoreDelimiter.c_str()))
			{
				channelToken = channelToken.substr(4);
			}

			tempOutChanName = "matte." + channelToken;
			const char* outChanName = tempOutChanName.c_str();

			if (boost::regex_match(inChanName, RED_CHANNEL_MATCH))
			{
				image.addChannel (tempOutChanName, inChannel.type);
				image.channel(outChanName);

				header.channels().insert (outChanName, inChannel);

				inFb.insert (inChanName, image.channel(outChanName).slice());
				outFb.insert (outChanName, image.channel(outChanName).slice());

			}

			if (boost::regex_match(inChanName, RGBA_CHANNEL_MATCH))
			{
				image.addChannel(inChanName, inChannel.type);
				image.channel(inChanName);

				header.channels().insert(inChanName, inChannel);

				inFb.insert(inChanName, image.channel(inChanName).slice());
				outFb.insert(inChanName, image.channel(inChanName).slice());
			}
		}

		in.setFrameBuffer (inFb);
		in.readPixels (in.header().dataWindow().min.y, in.header().dataWindow().max.y);
	}

	// Write the output image file
	{
		OutputFile out (outFileName.c_str(), header);

		if (verbose)
		{
			cout << "writing file " << outFileName << endl;
		}

		out.setFrameBuffer(outFb);
		out.writePixels(header.dataWindow().max.y - header.dataWindow().min.y + 1);
	}
}
