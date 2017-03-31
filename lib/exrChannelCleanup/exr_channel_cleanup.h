#ifndef INCLUDED_EXR_CHANNEL_CLEANUP_H
#define INCLUDED_EXR_CHANNEL_CLEANUP_H

//----------------------------------------------------------------------------
//
// Cleanup redundant RGBA channels.
//
//----------------------------------------------------------------------------

#include <iostream>
#include <string>

void exr_channel_cleanup(std::string inFileName, std::string outFileName, bool verbose);

#endif
