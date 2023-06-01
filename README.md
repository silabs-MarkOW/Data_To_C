# Data_To_C
Generate code to include binary image or arbitrary size arrays in .rodata or .data.

# Example Usage
<pre>
$ python3 data-to-c.py
Error: expecting single parameter, <base-filename>
Usage: data-to-c.py [ options ] <base-filename>
  options:
          --rodata=<size,name>     generate <size> bytes sized variable called
                                   <name> in .rodata
            --data=<size,name>     generate <size> bytes sized variable called
                                   <name> in .data
    --binary-image=<filename,name> place contents of <filename> in variable
                                   called <name> in .rodata
</pre>

## Include binary file as array
Useful for testing bootloader API.
<pre>
$ python3 data-to-c.py --binary-image=lzma.gbl,gbl_image data
</pre>
<pre>
$ cat data.h
#ifndef DATA_H
#define DATA_H

#include <stdint.h>

extern const uint32_t gbl_image[28648];

#endif
</pre>
<pre>
$ head data.c
#include "data.h"

const uint32_t gbl_image[28648] = {
  0x03a617eb,
  0x00000008,
  0x03000000,
  0x00000000,
  0xf40a0af4,
  0x0000001c,
  0x00000020,
</pre>

## Create 8 bytes in .data and 16 bytes in .rodata
<pre>
$ python3 data-to-c.py --data=8,eight_bytes --rodata=16,sixteen_bytes data
</pre>
<pre>
$ cat data.h
#ifndef DATA_H
#define DATA_H

#include <stdint.h>

extern const uint32_t sixteen_bytes[4];
extern uint32_t eight_bytes[2];

#endif
</pre>