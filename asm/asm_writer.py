bytesWrittenOnLine = 0

def start():
    global bytesWrittenOnLine

    bytesWrittenOnLine = 0

def writeByte(byte, f):
    global bytesWrittenOnLine

    if bytesWrittenOnLine == 16:
        f.write('\n')
        bytesWrittenOnLine = 0
    if bytesWrittenOnLine == 0:
        f.write('    !byte ')
    elif bytesWrittenOnLine != 0:
        f.write(",")
    f.write(str(byte))
    bytesWrittenOnLine += 1

def end(f):
    f.write('\n')

def writeBit(array, f):
    index = 0
    a = 0
    start()
    for x in array:
        if x:
            a += 1
        if index == 7:
            writeByte(a, f)
            index = 0
            a = 0
        else:
            index += 1
            a *= 2

    # flush remaining bits
    if index != 0:
        writeByte(a,f)
    end(f)
