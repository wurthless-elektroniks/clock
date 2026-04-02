import sys
import gzip

def main():

    out = None
    with open(sys.argv[1],"rb") as f:
        out = gzip.compress(f.read())
    
    with open(sys.argv[2],"wb") as f:
        f.write(out)

if __name__ == '__main__':
    main()
