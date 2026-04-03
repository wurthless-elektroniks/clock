import sys 
from deflate import gzippit

def _load_or_die(path) -> str:
    with open(path, "r") as f:
        return f.readlines()

def main():
    htm = _load_or_die("www/index.html")
    js  = _load_or_die("www/cfg.js")
    css = _load_or_die("www/cfg.css")
    lines_out = []
    for line in htm:
        if "cfg.css" in line:
            lines_out.append("<style>")
            lines_out += css
            lines_out.append("</style>")
        elif "cfg.js" in line:
            lines_out.append("<script type=\"text/javascript\">")
            lines_out += js
            lines_out.append("</script>")
        else:
            lines_out.append(line) 

    with open(sys.argv[1], "w", encoding='utf8') as f:
        f.write("\n".join(lines_out))
    gzippit(sys.argv[1], f"{sys.argv[1]}.gz")

if __name__ == '__main__':
    main()
