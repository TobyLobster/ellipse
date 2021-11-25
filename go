set -e

mkdir -p build/disk

# Assemble menu code
cd asm
../Tools/acme -o ../build/disk/ELLIPSE -r ../build/ellipse.txt --vicelabels ../build/ellipse.tmp ellipse.a
cd ..

# Sort symbols
sort <build/ellipse.tmp | uniq >build/ellipse.sym
rm build/ellipse.tmp

# Create !BOOT file
printf "*BASIC\rPAGE=&1900\r*FX21\rCLOSE#0:*RUN ELLIPSE\r" >build/disk/\!BOOT

# Create INF file for !BOOT
myfilesize=$(stat -f %z "build/disk/!BOOT")
myfilesizehex=$(printf '%x\n' $myfilesize)
echo "$.!BOOT     FFFF1900 FFFF1900 $myfilesizehex" >build/disk/\!BOOT.INF

# Create INF file for ELLIPSE
myfilesize=$(stat -f %z "build/disk/ELLIPSE")
myfilesizehex=$(printf '%x\n' $myfilesize)
echo "$.ELLIPSE   FFFF1900 FFFF1900 $myfilesizehex" >build/disk/ELLIPSE.INF

# Create new SSD file with the appropriate files
cp templates/EMPTY.SSD ELLIPSE.SSD
cd build/disk
python3 ../../tools/image.py -d ../../ELLIPSE.SSD -i !BOOT -i ELLIPSE
cd ../..

if [ $USER == "tobynelson" ];
then
    # Open SSD in b2
    osascript -e 'quit app "b2 Debug"'
    sleep 1
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
    open -a 'b2 Debug' --args -0 "$DIR/ELLIPSE.ssd" -b
else
    # Open SSD in BeebEm
    open ELLIPSE.ssd
fi
