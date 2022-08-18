# this class can be only imported
import mimetypes
from os.path import exists
import pathlib
from contextlib import redirect_stdout

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QMimeDatabase
from PyQt5.QtWidgets import QMessageBox

from mymodules import GDBModule as gdb

HEADER_SEARCH_RESULTS_TABLE = ['Directory', 'Filename', 'Size', 'Extension', 'Drive']
HEADER_DRIVES_TABLE = {"serial": "Serial Number", "name": "Drive Name", "label": "Own Label", "size": "Size (GB)",
                       "active": "Active", 'partitions': "Partitions"}

icons_map = {'ez': 'application-andrew-inset', 'anx': 'application-annodex', 'atom': 'application-atom+xml',
             'atomcat': 'application-atomcat+xml', 'atomsrv': 'application-atomserv+xml', 'lin': 'application-bbolin',
             'cu': 'application-cu-seeme', 'davmount': 'application-davmount+xml', 'dcm': 'application-dicom',
             'tsp': 'application-dsptype', 'es': 'application-ecmascript', 'epub': 'application-epub+zip',
             'otf': 'application-x-font-otf', 'ttf': 'application-x-font-ttf', 'pfr': 'application-font-tdpfr', 'woff': 'font-woff',
             'spl': 'application-x-futuresplash', 'gz': 'application-gzip', 'hta': 'application-hta',
             'jar': 'application-java-archive', 'ser': 'application-java-serialized-object',
             'class': 'application-java-vm', 'js': 'application-javascript', 'mjs': 'application-javascript',
             'json': 'application-json', 'jsonld': 'application-ld+json', 'm3g': 'application-m3g',
             'hqx': 'application-mac-binhex40', 'cpt': 'image-x-corelphotopaint', 'nb': 'application-mathematica',
             'nbp': 'application-mathematica', 'mbox': 'application-mbox', 'mdb': 'application-msaccess',
             'doc': 'application-msword', 'dot': 'application-msword', 'mxf': 'application-mxf',
             'bin': 'application-octet-stream', 'deploy': 'application-octet-stream', 'msu': 'application-octet-stream',
             'msp': 'application-octet-stream', 'oda': 'application-oda', 'opf': 'application-oebps-package+xml',
             'ogx': 'application-ogg', 'one': 'application-onenote', 'onetoc2': 'application-onenote',
             'onetmp': 'application-onenote', 'onepkg': 'application-onenote', 'pdf': 'application-pdf',
             'pgp': 'application-pgp-encrypted', 'key': 'application-pgp-keys', 'sig': 'application-pgp-signature',
             'prf': 'application-pics-rules', 'ps': 'application-postscript', 'ai': 'application-postscript',
             'eps': 'application-postscript', 'epsi': 'application-postscript', 'epsf': 'application-postscript',
             'eps2': 'application-postscript', 'eps3': 'application-postscript', 'rar': 'application-rar',
             'rdf': 'application-rdf+xml', 'rtf': 'application-rtf', 'stl': 'application-vnd.ms-pki.stl',
             'smi': 'chemical-x-daylight-smiles', 'smil': 'application-smil+xml', 'wasm': 'application-wasm',
             'xhtml': 'application-xhtml+xml', 'xht': 'application-xhtml+xml', 'xml': 'application-xml',
             'xsd': 'application-xml', 'xsl': 'application-xslt+xml', 'xslt': 'application-xslt+xml',
             'xspf': 'application-xspf+xml', 'zip': 'application-zip', 'apk': 'application-vnd.android.package-archive',
             'cdy': 'application-vnd.cinderella', 'deb': 'application-x-debian-package',
             'ddeb': 'application-vnd.debian.binary-package', 'udeb': 'application-x-debian-package',
             'sfd': 'application-vnd.font-fontforge-sfd', 'kml': 'application-vnd.google-earth.kml+xml',
             'kmz': 'application-vnd.google-earth.kmz', 'xul': 'application-vnd.mozilla.xul+xml',
             'xls': 'application-vnd.ms-excel', 'xlb': 'application-vnd.ms-excel', 'xlt': 'application-vnd.ms-excel',
             'xlam': 'application-vnd.ms-excel.addin.macroEnabled.12',
             'xlsb': 'application-vnd.ms-excel.sheet.binary.macroEnabled.12',
             'xlsm': 'application-vnd.ms-excel.sheet.macroEnabled.12',
             'xltm': 'application-vnd.ms-excel.template.macroEnabled.12', 'eot': 'application-vnd.ms-fontobject',
             'thmx': 'application-vnd.ms-officetheme', 'cat': 'application-vnd.ms-pki.seccat',
             'ppt': 'application-vnd.ms-powerpoint', 'pps': 'application-vnd.ms-powerpoint',
             'ppam': 'application-vnd.ms-powerpoint.addin.macroEnabled.12',
             'pptm': 'application-vnd.ms-powerpoint.presentation.macroEnabled.12',
             'sldm': 'application-vnd.ms-powerpoint.slide.macroEnabled.12',
             'ppsm': 'application-vnd.ms-powerpoint.slideshow.macroEnabled.12',
             'potm': 'application-vnd.ms-powerpoint.template.macroEnabled.12',
             'docm': 'application-vnd.ms-word.document.macroEnabled.12',
             'dotm': 'application-vnd.ms-word.template.macroEnabled.12',
             'odc': 'application-vnd.oasis.opendocument.chart', 'odb': 'application-vnd.oasis.opendocument.database',
             'odf': 'application-vnd.oasis.opendocument.formula', 'odg': 'application-vnd.oasis.opendocument.graphics',
             'otg': 'application-vnd.oasis.opendocument.graphics-template',
             'odi': 'application-vnd.oasis.opendocument.image',
             'odp': 'application-vnd.oasis.opendocument.presentation',
             'otp': 'application-vnd.oasis.opendocument.presentation-template',
             'ods': 'application-vnd.oasis.opendocument.spreadsheet',
             'ots': 'application-vnd.oasis.opendocument.spreadsheet-template',
             'odt': 'application-vnd.oasis.opendocument.text', 'odm': 'application-vnd.oasis.opendocument.text-master',
             'ott': 'application-vnd.oasis.opendocument.text-template',
             'oth': 'application-vnd.oasis.opendocument.text-web',
             'sldx': 'application-vnd.openxmlformats-officedocument.presentationml.slide',
             'ppsx': 'application-vnd.openxmlformats-officedocument.presentationml.slideshow',
             'potx': 'application-vnd.openxmlformats-officedocument.presentationml.template',
             'xlsx': 'application-vnd.openxmlformats-officedocument.spreadsheetml.sheet',
             'xltx': 'application-vnd.openxmlformats-officedocument.spreadsheetml.template',
             'docx': 'application-vnd.openxmlformats-officedocument.wordprocessingml.document',
             'dotx': 'application-vnd.openxmlformats-officedocument.wordprocessingml.template',
             'cod': 'application-vnd.rim.cod', 'mmf': 'application-vnd.smaf',
             'sdc': 'application-vnd.stardivision.calc', 'sds': 'application-vnd.stardivision.chart',
             'sda': 'application-vnd.stardivision.draw', 'sdd': 'application-vnd.stardivision.impress',
             'sdf': 'chemical-x-mdl-sdfile', 'sdw': 'application-vnd.stardivision.writer',
             'sgl': 'application-vnd.stardivision.writer-global', 'sxc': 'application-vnd.sun.xml.calc',
             'stc': 'application-vnd.sun.xml.calc.template', 'sxd': 'application-vnd.sun.xml.draw',
             'std': 'application-vnd.sun.xml.draw.template', 'sxi': 'application-vnd.sun.xml.impress',
             'sti': 'application-vnd.sun.xml.impress.template', 'sxm': 'application-vnd.sun.xml.math',
             'sxw': 'application-vnd.sun.xml.writer', 'sxg': 'application-vnd.sun.xml.writer.global',
             'stw': 'application-vnd.sun.xml.writer.template', 'sis': 'application-vnd.symbian.install',
             'cap': 'application-vnd.tcpdump.pcap', 'pcap': 'application-vnd.tcpdump.pcap',
             'vsd': 'application-vnd.visio', 'vst': 'application-vnd.visio', 'vsw': 'application-vnd.visio',
             'vss': 'application-vnd.visio', 'wbxml': 'application-vnd.wap.wbxml', 'wmlc': 'application-vnd.wap.wmlc',
             'wmlsc': 'application-vnd.wap.wmlscriptc', 'wpd': 'application-vnd.wordperfect',
             'wp5': 'application-vnd.wordperfect5.1', 'wk': 'application-x-123', '7z': 'application-x-7z-compressed',
             'abw': 'application-x-abiword', 'dmg': 'application-x-apple-diskimage', 'bcpio': 'application-x-bcpio',
             'torrent': 'application-x-bittorrent', 'cab': 'application-x-cab', 'cbr': 'application-x-cbr',
             'cbz': 'application-x-cbz', 'cdf': 'application-x-cdf', 'cda': 'application-x-cdf',
             'vcd': 'application-x-cdlink', 'pgn': 'application-x-chess-pgn', 'mph': 'application-x-comsol',
             'cpio': 'application-x-cpio', 'csh': 'text-x-csh', 'dcr': 'application-x-director',
             'dir': 'application-x-director', 'dxr': 'application-x-director', 'dms': 'application-x-dms',
             'wad': 'application-x-doom', 'dvi': 'application-x-dvi', 'pfa': 'application-x-font',
             'pfb': 'application-x-font', 'gsf': 'application-x-font', 'pcf': 'application-x-font-pcf',
             'pcf.Z': 'application-x-font-pcf', 'mm': 'application-x-freemind', 'gan': 'application-x-ganttproject',
             'gnumeric': 'application-x-gnumeric', 'sgf': 'application-x-go-sgf',
             'gcf': 'application-x-graphing-calculator', 'gtar': 'application-x-gtar',
             'tgz': 'application-x-gtar-compressed', 'taz': 'application-x-gtar-compressed', 'hdf': 'application-x-hdf',
             'rhtml': 'application-x-httpd-eruby', 'phtml': 'application-x-php',
             'pht': 'application-x-php', 'php': 'application-x-php',
             'phps': 'application-x-php-source', 'php3': 'application-x-php3',
             'php3p': 'application-x-php3-preprocessed', 'php4': 'application-x-php4',
             'php5': 'application-x-php5', 'hwp': 'application-x-hwp', 'ica': 'application-x-ica',
             'info': 'application-x-info', 'ins': 'application-x-internet-signup',
             'isp': 'application-x-internet-signup', 'iii': 'application-x-iphone',
             'iso': 'application-x-iso9660-image', 'jam': 'application-x-jam', 'jnlp': 'application-x-java-jnlp-file',
             'jmz': 'application-x-jmol', 'chrt': 'application-x-kchart', 'kil': 'application-x-killustrator',
             'skp': 'application-x-koan', 'skd': 'application-x-koan', 'skt': 'application-x-koan',
             'skm': 'application-x-koan', 'kpr': 'application-x-kpresenter', 'kpt': 'application-x-kpresenter',
             'ksp': 'application-x-kspread', 'kwd': 'application-x-kword', 'kwt': 'application-x-kword',
             'latex': 'application-x-latex', 'lha': 'application-x-lha', 'lyx': 'application-x-lyx',
             'lzh': 'application-x-lzh', 'lzx': 'application-x-lzx', 'frm': 'application-x-maker',
             'maker': 'application-x-maker', 'frame': 'application-x-maker', 'fm': 'application-x-maker',
             'fb': 'application-x-maker', 'book': 'application-x-maker', 'fbdoc': 'application-x-maker',
             'mif': 'chemical-x-mif', 'm3u8': 'application-x-mpegURL', 'application': 'application-x-ms-application',
             'manifest': 'application-x-ms-manifest', 'wmd': 'application-x-ms-wmd', 'wmz': 'application-x-ms-wmz',
             'com': 'application-x-msdos-program', 'exe': 'application-x-msdos-program',
             'bat': 'application-x-msdos-program', 'dll': 'application-x-msdos-program', 'msi': 'application-x-msi',
             'nc': 'application-x-netcdf', 'pac': 'application-x-ns-proxy-autoconfig', 'nwc': 'application-x-nwc',
             'o': 'application-x-object', 'oza': 'application-x-oz-application',
             'p7r': 'application-x-pkcs7-certreqresp', 'crl': 'application-x-pkcs7-crl',
             'pyc': 'application-x-python-code', 'pyo': 'application-x-python-code', 'qgs': 'application-x-qgis',
             'shp': 'application-x-qgis', 'shx': 'application-x-qgis', 'qtl': 'application-x-quicktimeplayer',
             'rdp': 'application-x-rdp', 'rpm': 'application-x-redhat-package-manager', 'rss': 'application-x-rss+xml',
             'rb': 'application-x-ruby', 'sci': 'application-x-scilab', 'sce': 'application-x-scilab',
             'xcos': 'application-x-scilab-xcos', 'sh': 'text-x-sh', 'shar': 'application-x-shar',
             'swf': 'application-x-shockwave-flash', 'swfl': 'application-x-shockwave-flash',
             'scr': 'application-x-silverlight', 'sql': 'application-x-sql', 'sit': 'application-x-stuffit',
             'sitx': 'application-x-stuffit', 'sv4cpio': 'application-x-sv4cpio', 'sv4crc': 'application-x-sv4crc',
             'tar': 'application-x-tar', 'tcl': 'text-x-tcl', 'gf': 'application-x-tex-gf',
             'pk': 'application-x-tex-pk', 'texinfo': 'application-x-texinfo', 'texi': 'application-x-texinfo',
             '~': 'application-x-trash', '%': 'application-x-trash', 'bak': 'application-x-trash',
             'old': 'application-x-trash', 'sik': 'application-x-trash', 't': 'application-x-troff',
             'tr': 'application-x-troff', 'roff': 'application-x-troff', 'man': 'application-x-troff-man',
             'me': 'application-x-troff-me', 'ms': 'application-x-troff-ms', 'ustar': 'application-x-ustar',
             'src': 'application-x-wais-source', 'wz': 'application-x-wingz', 'crt': 'application-x-x509-ca-cert',
             'xcf': 'application-x-xcf', 'fig': 'application-x-xfig', 'xpi': 'application-x-xpinstall',
             'xz': 'application-x-xz', 'amr': 'audio-amr', 'awb': 'audio-amr-wb', 'axa': 'audio-annodex',
             'au': 'audio-basic', 'snd': 'audio-basic', 'csd': 'audio-csound', 'orc': 'audio-csound',
             'sco': 'audio-csound', 'flac': 'audio-x-flac+ogg', 'mid': 'audio-midi', 'midi': 'audio-midi',
             'kar': 'audio-midi', 'mpga': 'audio-mpeg', 'mpega': 'audio-mpeg', 'mp2': 'audio-mpeg', 'mp3': 'audio-mpeg',
             'm4a': 'audio-mpeg', 'm3u': 'audio-x-mpegurl', 'oga': 'audio-ogg', 'ogg': 'audio-ogg', 'opus': 'audio-ogg',
             'spx': 'audio-ogg', 'sid': 'audio-prs.sid', 'aif': 'audio-x-aiff', 'aiff': 'audio-x-aiff',
             'aifc': 'audio-x-aiff', 'gsm': 'audio-x-gsm', 'wma': 'audio-x-ms-wma', 'wax': 'audio-x-ms-wax',
             'ra': 'audio-x-realaudio', 'rm': 'audio-x-pn-realaudio', 'ram': 'audio-x-pn-realaudio',
             'pls': 'audio-x-scpls', 'sd2': 'audio-x-sd2', 'wav': 'audio-x-wav', 'alc': 'chemical-x-alchemy',
             'cac': 'chemical-x-cache', 'cache': 'chemical-x-cache', 'csf': 'chemical-x-cache-csf',
             'cbin': 'chemical-x-cactvs-binary', 'cascii': 'chemical-x-cactvs-binary',
             'ctab': 'chemical-x-cactvs-binary', 'cdx': 'chemical-x-cdx', 'cer': 'chemical-x-cerius',
             'c3d': 'chemical-x-chem3d', 'chm': 'chemical-x-chemdraw', 'cif': 'chemical-x-cif',
             'cmdf': 'chemical-x-cmdf', 'cml': 'chemical-x-cml', 'cpa': 'chemical-x-compass',
             'bsd': 'chemical-x-crossfire', 'csml': 'chemical-x-csml', 'csm': 'chemical-x-csml',
             'ctx': 'chemical-x-ctx', 'cxf': 'chemical-x-cxf', 'cef': 'chemical-x-cxf',
             'emb': 'chemical-x-embl-dl-nucleotide', 'embl': 'chemical-x-embl-dl-nucleotide',
             'spc': 'chemical-x-galactic-spc', 'inp': 'chemical-x-gamess-input', 'gam': 'chemical-x-gamess-input',
             'gamin': 'chemical-x-gamess-input', 'fch': 'chemical-x-gaussian-checkpoint',
             'fchk': 'chemical-x-gaussian-checkpoint', 'cub': 'chemical-x-gaussian-cube',
             'gau': 'chemical-x-gaussian-input', 'gjc': 'chemical-x-gaussian-input', 'gjf': 'chemical-x-gaussian-input',
             'gal': 'chemical-x-gaussian-log', 'gcg': 'chemical-x-gcg8-sequence', 'gen': 'chemical-x-genbank',
             'hin': 'chemical-x-hin', 'istr': 'chemical-x-isostar', 'ist': 'chemical-x-isostar',
             'jdx': 'chemical-x-jcamp-dx', 'dx': 'chemical-x-jcamp-dx', 'kin': 'chemical-x-kinemage',
             'mcm': 'chemical-x-macmolecule', 'mmd': 'chemical-x-macromodel-input',
             'mmod': 'chemical-x-macromodel-input', 'mol': 'chemical-x-mdl-molfile', 'rd': 'chemical-x-mdl-rdfile',
             'rxn': 'chemical-x-mdl-rxnfile', 'sd': 'chemical-x-mdl-sdfile', 'tgf': 'chemical-x-mdl-tgf',
             'mcif': 'chemical-x-mmcif', 'mol2': 'chemical-x-mol2', 'b': 'chemical-x-molconn-Z',
             'gpt': 'chemical-x-mopac-graph', 'mop': 'chemical-x-mopac-input', 'mopcrt': 'chemical-x-mopac-input',
             'mpc': 'chemical-x-mopac-input', 'zmt': 'chemical-x-mopac-input', 'moo': 'chemical-x-mopac-out',
             'mvb': 'chemical-x-mopac-vib', 'asn': 'chemical-x-ncbi-asn1-spec', 'prt': 'chemical-x-ncbi-asn1-ascii',
             'ent': 'chemical-x-pdb', 'val': 'chemical-x-ncbi-asn1-binary', 'aso': 'chemical-x-ncbi-asn1-binary',
             'pdb': 'chemical-x-pdb', 'ros': 'chemical-x-rosdal', 'sw': 'chemical-x-swissprot',
             'vms': 'chemical-x-vamas-iso14976', 'vmd': 'chemical-x-vmd', 'xtel': 'chemical-x-xtel',
             'xyz': 'chemical-x-xyz', 'ttc': 'font-collection', 'woff2': 'font-woff2', 'gif': 'image-gif',
             'ief': 'image-ief', 'jp2': 'image-jp2', 'jpg2': 'image-jp2', 'jpeg': 'image-jpeg', 'jpg': 'image-jpeg',
             'jpe': 'image-jpeg', 'jpm': 'image-jpm', 'jpx': 'image-jpx', 'jpf': 'image-jpx', 'pcx': 'image-pcx',
             'png': 'image-png', 'svg': 'image-svg+xml', 'svgz': 'image-svg+xml', 'tiff': 'image-tiff',
             'tif': 'image-tiff', 'djvu': 'image-vnd.djvu', 'djv': 'image-vnd.djvu', 'ico': 'image-vnd.microsoft.icon',
             'wbmp': 'image-vnd.wap.wbmp', 'cr2': 'image-x-canon-cr2', 'crw': 'image-x-canon-crw',
             'ras': 'image-x-cmu-raster', 'cdr': 'image-x-coreldraw', 'pat': 'image-x-coreldrawpattern',
             'cdt': 'image-x-coreldrawtemplate', 'erf': 'image-x-epson-erf', 'art': 'image-x-jg', 'jng': 'image-x-jng',
             'bmp': 'image-x-ms-bmp', 'nef': 'image-x-nikon-nef', 'orf': 'image-x-olympus-orf',
             'psd': 'image-x-photoshop', 'pnm': 'image-x-portable-anymap', 'pbm': 'image-x-portable-bitmap',
             'pgm': 'image-x-portable-graymap', 'ppm': 'image-x-portable-pixmap', 'rgb': 'image-x-rgb',
             'xbm': 'image-x-xbitmap', 'xpm': 'image-x-xpixmap', 'xwd': 'image-x-xwindowdump', 'eml': 'message-rfc822',
             'igs': 'model-iges', 'iges': 'model-iges', 'msh': 'model-mesh', 'mesh': 'model-mesh', 'silo': 'model-mesh',
             'wrl': 'x-world-x-vrml', 'vrml': 'x-world-x-vrml', 'x3dv': 'model-x3d+vrml', 'x3d': 'model-x3d+xml',
             'x3db': 'model-x3d+binary', 'appcache': 'text-cache-manifest', 'ics': 'text-calendar',
             'icz': 'text-calendar', 'css': 'text-css', 'csv': 'text-csv', '323': 'text-h323', 'html': 'text-html',
             'htm': 'text-html', 'shtml': 'text-html', 'uls': 'text-iuls', 'mml': 'text-mathml', 'md': 'text-markdown',
             'markdown': 'text-markdown', 'asc': 'text-plain', 'txt': 'text-plain', 'text': 'text-plain',
             'pot': 'text-plain', 'brf': 'text-plain', 'srt': 'text-plain', 'rtx': 'text-richtext',
             'sct': 'text-scriptlet', 'wsc': 'text-scriptlet', 'tm': 'text-texmacs', 'tsv': 'text-tab-separated-values',
             'ttl': 'text-turtle', 'vcf': 'text-vcard', 'vcard': 'text-vcard',
             'jad': 'text-vnd.sun.j2me.app-descriptor', 'wml': 'text-vnd.wap.wml', 'wmls': 'text-vnd.wap.wmlscript',
             'bib': 'text-x-bibtex', 'boo': 'text-x-boo', 'h++': 'text-x-c++hdr', 'hpp': 'text-x-c++hdr',
             'hxx': 'text-x-c++hdr', 'hh': 'text-x-c++hdr', 'c++': 'text-x-c++src', 'cpp': 'text-x-c++src',
             'cxx': 'text-x-c++src', 'cc': 'text-x-c++src', 'h': 'text-x-chdr', 'htc': 'text-x-component',
             'c': 'text-x-csrc', 'd': 'text-x-dsrc', 'diff': 'text-x-diff', 'patch': 'text-x-diff',
             'hs': 'text-x-haskell', 'java': 'text-x-java', 'ly': 'text-x-lilypond', 'lhs': 'text-x-literate-haskell',
             'moc': 'text-x-moc', 'p': 'text-x-pascal', 'pas': 'text-x-pascal', 'gcd': 'text-x-pcs-gcd',
             'pl': 'text-x-perl', 'pm': 'text-x-perl', 'py': 'text-x-python', 'scala': 'text-x-scala',
             'etx': 'text-x-setext', 'sfv': 'text-x-sfv', 'tk': 'text-x-tcl', 'tex': 'text-x-tex', 'ltx': 'text-x-tex',
             'sty': 'text-x-tex', 'cls': 'text-x-tex', 'vcs': 'text-x-vcalendar', '3gp': 'video-3gpp',
             'axv': 'video-annodex', 'dl': 'video-dl', 'dif': 'video-dv', 'dv': 'video-dv', 'fli': 'video-fli',
             'gl': 'video-gl', 'mpeg': 'video-mpeg', 'mpg': 'video-mpeg', 'mpe': 'video-mpeg', 'ts': 'video-MP2T',
             'mp4': 'video-mp4', 'qt': 'video-quicktime', 'mov': 'video-quicktime', 'ogv': 'video-ogg',
             'webm': 'video-webm', 'mxu': 'video-vnd.mpegurl', 'flv': 'video-x-flv', 'lsf': 'video-x-la-asf',
             'lsx': 'video-x-la-asf', 'mng': 'video-x-mng', 'asf': 'video-x-ms-asf', 'asx': 'video-x-ms-asf',
             'wm': 'video-x-ms-wm', 'wmv': 'video-x-ms-wmv', 'wmx': 'video-x-ms-wmx', 'wvx': 'video-x-ms-wvx',
             'avi': 'video-x-msvideo', 'movie': 'video-x-sgi-movie', 'mpv': 'video-x-matroska',
             'mkv': 'video-x-matroska', 'ice': 'x-conference-x-cooltalk', 'sisx': 'x-epoc-x-sisx-app',
             'vrm': 'x-world-x-vrml'}

icons_with_image_map = {'otf': 'font-ttf', 'ttf': 'font-ttf', 'jar': 'application-java-archive', 'class': 'application-java-vm',
             'mdb': 'application-msaccess', 'rar': 'application-rar', 'apk': 'application-vnd.android.package-archive',
             'deb': 'application-x-debian-package', 'xlsm': 'application-vnd.ms-excel.sheet.macroEnabled.12',
             'dmg': 'application-x-apple-diskimage', 'cab': 'application-x-cab', 'cda': 'application-x-cdf',
             'vcd': 'application-x-cdlink', 'iso': 'application-x-iso9660-image', 'com': 'application-x-msdos-program',
             'exe': 'application-x-msdos-program', 'bat': 'application-x-msdos-program',
             'dll': 'application-x-msdos-program', 'msi': 'application-x-msi',
             'rpm': 'application-x-redhat-package-manager', 'rss': 'application-x-rss+xml', 'sh': 'text-x-sh',
             'sql': 'application-x-sql', 'ogg': 'audio-ogg', 'wma': 'audio-x-ms-wma', 'rm': 'audio-x-pn-realaudio',
             'cer': 'chemical-x-cerius', 'ico': 'image-vnd.microsoft.icon', 'bmp': 'image-x-ms-bmp',
             'psd': 'image-x-photoshop', 'vcf': 'text-vcard', 'pl': 'text-x-perl', '3gp': 'video-3gpp',
             'mpeg': 'video-mpeg', 'mpg': 'video-mpeg', 'mov': 'video-quicktime'}


default_extensions = [['aif', 1, 0], ['cda', 1, 0], ['mid', 1, 0], ['midi', 1, 0], ['mp3', 1, 1],
                      ['mpa', 1, 0], ['ogg', 1, 1], ['wav', 1, 0], ['wma', 1, 0], ['wpl', 1, 0],
                      ['7z', 2, 0], ['arj', 2, 0], ['deb', 2, 0], ['pkg', 2, 0], ['rar', 2, 1],
                      ['rpm', 2, 0], ['tar.gz', 2, 0], ['z', 2, 0], ['zip', 2, 1], ['dmg', 3, 0],
                      ['iso', 3, 0], ['toast', 3, 0], ['vcd', 3, 0], ['csv', 4, 1], ['dat', 4, 0],
                      ['db', 4, 1], ['dbf', 4, 0], ['log', 4, 0], ['mdb', 4, 0], ['sav', 4, 0],
                      ['sql', 4, 1], ['tar', 4, 0], ['xml', 4, 1], ['email', 5, 0], ['eml', 5, 0],
                      ['emlx', 5, 0], ['msg', 5, 0], ['oft', 5, 0], ['ost', 5, 0], ['pst', 5, 0],
                      ['vcf', 5, 0], ['apk', 6, 0], ['bat', 6, 0], ['bin', 6, 0], ['cgi', 6, 0],
                      ['com', 6, 0], ['exe', 6, 1], ['gadget', 6, 0], ['jar', 6, 0], ['msi', 6, 1],
                      ['wsf', 6, 0], ['fnt', 7, 0], ['fon', 7, 0], ['otf', 7, 1], ['ttf', 7, 1],
                      ['ai', 8, 1], ['bmp', 8, 0], ['gif', 8, 0], ['ico', 8, 0], ['jpeg', 8, 1],
                      ['jpg', 8, 1], ['png', 8, 1], ['ps', 8, 0], ['psd', 8, 0], ['svg', 8, 0],
                      ['tif', 8, 0], ['tiff', 8, 0], ['asp', 9, 1], ['aspx', 9, 1], ['cer', 9, 0],
                      ['cfm', 9, 0], ['css', 9, 1], ['htm', 9, 0], ['html', 9, 1], ['js', 9, 1],
                      ['jsp', 9, 0], ['part', 9, 0], ['rss', 9, 0], ['xhtml', 9, 0], ['key', 10, 0],
                      ['odp', 10, 0], ['pps', 10, 0], ['ppt', 10, 1], ['pptx', 10, 1], ['c', 11, 0],
                      ['pl', 11, 0], ['class', 11, 0], ['cpp', 11, 0], ['cs', 11, 0], ['h', 11, 1],
                      ['java', 11, 1], ['php', 11, 1], ['py', 11, 1], ['sh', 11, 1], ['swift', 11, 0],
                      ['vb', 11, 0], ['json', 11, 0], ['ods', 12, 1], ['xls', 12, 1], ['xlsm', 12, 1],
                      ['xlsx', 12, 1], ['bak', 13, 0], ['cab', 13, 0], ['cfg', 13, 0], ['cpl', 13, 0],
                      ['cur', 13, 0], ['dll', 13, 0], ['dmp', 13, 0], ['drv', 13, 0], ['icns', 13, 0],
                      ['ini', 13, 0], ['lnk', 13, 0], ['sys', 13, 0], ['tmp', 13, 0], ['3g2', 14, 0],
                      ['3gp', 14, 0], ['avi', 14, 1], ['flv', 14, 0], ['h264', 14, 0], ['m4v', 14, 1],
                      ['mkv', 14, 1], ['mov', 14, 0], ['mp4', 14, 1], ['mpg', 14, 1], ['mpeg', 14, 1],
                      ['rm', 14, 0], ['swf', 14, 0], ['vob', 14, 0], ['wmv', 14, 1], ['srt', 14, 1],
                      ['sub', 14, 1], ['doc', 15, 1], ['docx', 15, 1], ['odt', 15, 1], ['pdf', 15, 1],
                      ['rtf', 15, 0], ['tex', 15, 0], ['txt', 15, 0], ['wpd', 15, 0]]


def getIcon(item, size=24):
    current_directory = str(pathlib.Path(__file__).parent.absolute())
    if item in icons_map.keys():
        name = icons_map[item]
        path = current_directory + '/../images/icons/' + name + '.png'
        print(item, path, exists(path))
        icon = QtGui.QIcon(path)
        return icon.pixmap(size)
        # else:
        #     mime = mimetypes.types_map
        #     ext = '.'+item
        #     if ext in mime.keys():
        #         name = mime[ext].replace('/', '-')
        #         icon = QtGui.QIcon.fromTheme(name)
        #         if not icon.isNull():
        #             return icon.pixmap(size)
        #         else:
        #             a = QMimeDatabase().allMimeTypes()
        #             for mime in a:
        #                 if mime.name() == 'text/' + item or mime.name() == 'application/x-' + item:
        #                     name = mime.name().replace('/', '-')
        #                     icon = QtGui.QIcon.fromTheme(name)
        #                     if not icon.isNull():
        #                         return icon.pixmap(size)


def file_exists(path_of_file):
    return exists(path_of_file)

def formatDictToHuman(d):
    lista = []
    for k, v in d.items():
        item = k + ' : ' + v
        lista.append(item)
    human_list = "\n".join(lista)
    return human_list


def putInFile(data, filename='out.txt'):
    with open(filename, 'w') as f:
        with redirect_stdout(f):
            print(data)


def iconForButton(name):
    return QtWidgets.QApplication.style().standardIcon(getattr(QtWidgets.QStyle, name))


def confirmationDialog(title, message):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText(message)
    msg_box.setWindowTitle(title)
    msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    return msg_box.exec() == QMessageBox.Ok


def tabIndexByName(tab_widget, tab_name):
    for index in range(tab_widget.count()):
        if tab_name == tab_widget.tabText(index):
            return index


def categoriesCombo():
    categories = gdb.getAll('categories')
    combo = QtWidgets.QComboBox()
    categories_name = []
    for item in categories:
        categories_name.append(item['category'])
    categories_name.insert(0, '--Categories--')
    combo.addItems(categories_name)
    return combo


class Global():
    pass
