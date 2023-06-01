import sys
import getopt
import shutil
import numpy

long_opts = ['version']
options = {}
option_types = {}
option_params = {}
option_desc = {'version':'show version from git info'}

def add_option(name, datatype=None, default=None, params=None, desc=None) :
    option = name
    if None != datatype :
        option += '='
        if None == params :
            raise RuntimeError('option "%s" missing params'%(name))
        else :
            option_params[name] = params
    long_opts.append(option)
    if None != default :
        if type(default) != datatype :
            raise RuntimeError('type(%s) != %s'%(default.__str__(),str(datatype)))
        options[name] = default
    option_types[name] = datatype
    if None != desc :
        option_desc[name] = desc
    
add_option('rodata',(int,str),params="<size,name>",desc="generate <size> bytes sized variable called <name> in .rodata")
add_option('data',(int,str),params="<size,name>",desc="generate <size> bytes sized variable called <name> in .data")
add_option('binary-image',(str,str),params="<filename,name>",desc="place contents of <filename> in variable called <name> in .rodata")

def format(s,width) :
    length = len(s)
    if length <= width : return [s]
    lines = []
    tokens = s.split()
    current = tokens.pop(0)
    while len(tokens) :
        if len(current) + 1 + len(tokens[0]) > width :
            lines.append(current)
            current = tokens.pop(0)
        else :
            current += ' ' + tokens.pop(0)
    lines.append(current)
    return lines

def exit_help(msg = None) :
    width = shutil.get_terminal_size((80, 20))[0]
    if None != msg :
        print('Error: %s'%(msg))
    print('Usage: %s [ options ] <base-filename>\n  options:'%(sys.argv[0]))
    optlen = 0
    paramlen = 0
    for option in long_opts :
        if '=' == option[-1] :
            name = option[:-1]
        else :
            name = option
        params = option_params.get(name)
        if None != params and len(params) > paramlen : paramlen = len(params)
        if len(option) > optlen : optlen = len(option)
    fmt = '    %%%ds%%-%ds %%s'%(optlen+2,paramlen)
    for option in long_opts :
        if '=' == option[-1] :
            name = option[:-1]
        else :
            name = option
            option += ' '
        desc = option_desc.get(name)
        if None == desc : desc = ''
        desc = format(desc,width-len(fmt%('','','')))
        params = option_params.get(name)
        if None == params : params = ''
        print(fmt%('--'+option,params,desc[0]))
        for d in desc[1:] :
            print(fmt%('','',d))
    quit()
    
opts,params = getopt.getopt(sys.argv[1:],'hv',long_opts)
for opt,param in opts :
    if '-h' == opt :
        exit_help()
    elif '-v' == opt or '--version' == opt :
        print(s2b_get_version())
        quit()
    else :
        for option in long_opts :
            if '=' == option[-1] :
                name = option[:-1]
                if '--'+name == opt :
                    datatype = option_types[name]
                    if tuple == type(datatype) :
                        tokens = param.split(',')
                        if len(tokens) != len(datatype) :
                            exit_help('tuple length mismatch parsing "%s" parameters.  Expecting %s, got %s'%(opt,datatype.__str__(),tokens.__str__()))
                        option = ()
                        for i in range(len(tokens)) :
                            option += (datatype[i](tokens[i]),)
                        options[name] = option
                    else :
                        options[name] = datatype(param)
if len(params) != 1 :
    exit_help('expecting single parameter, <base-filename>')

class Data_Source :
    def __init__(s,param) :
        if int == type(param) :
            s.data = numpy.random.bytes(size)
        elif str == type(param) :
            fh = open(filename,'rb')
            s.data = fh.read()
            fh.close()
        else :
            raise RuntimeError(type(param))
        rem = len(s.data) & 3
        if 0 == rem :
            s.type = "uint32_t"
            s.step = 4
        elif 2 & rem :
            s.type = "uint16_t"
            s.step = 2
        else :
            s.type = "uint8_t"
            s.step = 1
    def set_type(s,ctype) :
        raise RuntimeError('Not impemented')
    def get_type(s) :
        return s.type
    def get_items(s) :
        item_count = len(s.data) // s.step
        items = []
        format = '0x%%0%dx'%(s.step<<1)
        for i in range(item_count) :
            bin = s.data[s.step*i:s.step*(i+1)]
            num = int.from_bytes(bin,'little')
            items.append(format%(num))
        return items
            
basename = params[0]
c_content = ''
h_content = ''

option = options.get('binary-image')
if None != option :
    filename,varname = option
    ds = Data_Source(filename)
    items = ds.get_items()
    decl = 'const %s %s[%d]'%(ds.get_type(),varname,len(items))
    h_content += 'extern %s;\n'%(decl)
    c_content += '%s = {\n  %s\n};\n\n'%(decl,',\n  '.join(items))
    
option = options.get('rodata')
if None != option :
    size,varname = option
    ds = Data_Source(size)
    items = ds.get_items()
    decl = 'const %s %s[%d]'%(ds.get_type(),varname,len(items))
    h_content += 'extern %s;\n'%(decl)
    c_content += '%s = {\n  %s\n};\n\n'%(decl,',\n  '.join(items))
    
option = options.get('data')
if None != option :
    size,varname = option
    ds = Data_Source(size)
    items = ds.get_items()
    decl = '%s %s[%d]'%(ds.get_type(),varname,len(items))
    h_content += 'extern %s;\n'%(decl)
    c_content += '%s = {\n  %s\n};\n\n'%(decl,',\n  '.join(items))

define = basename.upper()+'_H'
fh = open(basename+'.h','w')
fh.write('#ifndef %s\n#define %s\n\n#include <stdint.h>\n\n%s\n#endif\n'%(define,define,h_content))
fh.close()

fh = open(basename+'.c','w')
fh.write('#include "%s.h"\n\n%s'%(basename,c_content))
fh.close()
