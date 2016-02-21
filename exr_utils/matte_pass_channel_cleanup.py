#!/usr/bin/env python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Will flatten RGBA channels in a layer down to one channel.

"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import re
import os
import array
import Imath
import time

# third-party
import OpenEXR

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- GLOBALS --#

CHANNEL_MATCH = re.compile('([a-z0-9_]+)\.([rdgrnblue]+)', re.I)
ALPHA_MATCH = re.compile('([a-z0-9_]+)\.([a]+)', re.I)
HALF = Imath.Channel(Imath.PixelType(Imath.PixelType.HALF))

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

def matte_pass_channel_cleanup(in_path, out_path):
    """
    @params:
        in_path: Path to exr file.
        out_path: Path to write out the new exr file.
    """

    if os.path.exists(in_path) and OpenEXR.isOpenExrFile(in_path):
        channels_to_merge = defaultdict(list)
        base_channels = []

        # Read the file and header
        handle = OpenEXR.InputFile(in_path)
        header = handle.header()

        # Get the channels
        channels = header['channels']
        header['channels'] = {}
        new_channels = {}

        for channel_name, channel_data in channels.iteritems():
            match = CHANNEL_MATCH.match(channel_name)
            if match:
                layer, channel = match.groups()
                channels_to_merge[layer].append(channel)

            elif not ALPHA_MATCH.match(channel_name):
                base_channels.append(channel_name)

        for layer in base_channels:
            all_pixels = array.array( 'f', handle.channel(layer,
                 Imath.PixelType(Imath.PixelType.HALF))).tolist()
            new_channels[layer] = array.array('f', all_pixels).tostring()

        for layer, data in channels_to_merge.iteritems():
            new_pixels = []

            try:
                new_layer_name = layer.split('_')[1]
            except:
                new_layer_name = layer

            # new pixels
            new_pixels = array.array('f',
                    handle.channel('{0}.{1}'.format(layer, data[0])))
            new_channels['matte.{0}'.format(new_layer_name)] = array.array('f',
                                                         new_pixels).tostring()

        # write out new exr
        header['channels'] = dict([(c, HALF) for c in new_channels.keys()])
        out = OpenEXR.OutputFile(out_path, header)
        out.writePixels(new_channels)

if __name__ == "__main__":
    matte_pass_channel_cleanup()
