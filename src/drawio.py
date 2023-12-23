import re
import xmltodict
from urllib.parse import unquote

def get_mxfile_from_png(fpath):
    """Given a path to a *.drawio.png file, extracts the MxFile XML and returns 
    the XML content as a string."""
    if not fpath.endswith('.drawio.png'):
        print('File is not a Draw.io PNG')
        return None
    pngbytes = open(fpath, mode='rb').read()
    png = pngbytes.decode('utf-8', errors='ignore')
    decoded = unquote(png, encoding='utf-8')
    match = re.search('<mxfile>.*</mxfile>', decoded)
    mxfile = match.group(0)
    return mxfile


def mxfile_to_json(fpath):
    """Given a path to a drawio file, parses the XML and returns the content as
    a dict using xmltodict.parse()."""
    if fpath.endswith('.drawio.png'):
        xml = get_mxfile_from_png(fpath)
    elif fpath.endswith('.drawio'):
        xml = open(fpath, mode='r').read()
    else:
        print('Error: File is not a Draw.io PNG (*.drawio.png) or XML (*.drawio)')
        exit(-1)
    d = xmltodict.parse(xml)
    mxgraph = d['mxfile']['diagram']['mxGraphModel']
    return mxgraph


if __name__ == '__main__':
    # Sanity check
    x = mxfile_to_json('examples/simple.drawio.png')
    n_root_objects = len(list(x.get('root', {}).values()))
    assert n_root_objects == 2