#!/usr/bin/python

import OpenEXR
import re
import os
import array
import Imath
import time

CHANNEL_MATCH = re.compile('([a-z0-9_]+)\.([rdgrnblue]+)', re.I)
ALPHA_MATCH = re.compile('([a-z0-9_]+)\.([a]+)', re.I)
HALF = Imath.Channel(Imath.PixelType(Imath.PixelType.HALF))

def matte_pass_channel_cleanup(exr_file = '/people/acarlisle/office_matte_01.office_1_camShape_converted.0101.exr'):
    start = time.time()

    if os.path.exists(exr_file) and OpenEXR.isOpenExrFile(exr_file):
        channels_to_merge = defaultdict(list)
        base_channels = []

        # Read the file and header
        handle = OpenEXR.InputFile(exr_file)
        header = handle.header()
        # Get the channels (is a dict)
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
            all_pixels = array.array( 'f', handle.channel(layer, Imath.PixelType(Imath.PixelType.HALF))).tolist()
            new_channels[layer] = array.array('f', all_pixels).tostring()

        for layer, data in channels_to_merge.iteritems():
            new_pixels = []

            # all_pixels = zip(*[array.array( 'f', handle.channel('{0}.{1}'.format(
            #     layer, channel), Imath.PixelType(Imath.PixelType.HALF))).tolist() for channel in data])
            # for pixel in all_pixels:
            #     new_pixels.append(sum(pixel)/len(pixel))
            try:
                new_layer_name = layer.split('_')[1]
            except:
                new_layer_name = layer

            new_pixels = array.array('f', handle.channel('{0}.{1}'.format(layer, data[0])))
            new_channels['matte.{0}'.format(new_layer_name)] = array.array(
                'f', new_pixels).tostring()

        header['channels'] = dict([(c, HALF) for c in new_channels.keys()])
        out = OpenEXR.OutputFile('/home/acarlisle/test_code/test_aaron_five.exr', header)
        out.writePixels(new_channels)

if __name__ == "__main__":
    matte_pass_channel_cleanup()



