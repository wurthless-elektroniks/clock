import sys
import gzip

def gzippit(input, output):
    out = None
    with open(input,"rb") as f:
        out = gzip.compress(f.read())
    
    with open(output,"wb") as f:
        f.write(out)

def main():
    gzippit(sys.argv[1],sys.argv[2])

if __name__ == '__main__':
    main()
