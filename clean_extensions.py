uniq_extension = ['aif', 'cda', 'mid', 'midi', 'mp3', 'mpa', 'ogg', 'wav', 'wma', 'wpl', '7z', 'arj', 'deb', 'pkg', 'rar', 'rpm', 'targz', 'z', 'zip', 'bin', 'dmg', 'iso', 'toast', 'vcd', 'csv', 'dat', 'db', 'dbf', 'log', 'mdb', 'sav', 'sql', 'tar', 'xml', 'email', 'eml', 'emlx', 'msg', 'oft', 'ost', 'pst', 'vcf', 'apk', 'bat', 'cgi', 'pl', 'com', 'exe', 'gadget', 'jar', 'msi', 'py', 'wsf', 'fnt', 'fon', 'otf', 'ttf', 'ai', 'bmp', 'gif', 'ico', 'jpeg', 'jpg', 'png', 'ps', 'psd', 'svg', 'tif', 'tiff', 'asp', 'aspx', 'cer', 'cfm', 'css', 'htm', 'html', 'js', 'jsp', 'part', 'php', 'rss', 'xhtml', 'key', 'odp', 'pps', 'ppt', 'pptx', 'c', 'class', 'cpp', 'cs', 'h', 'java', 'sh', 'swift', 'vb', 'ods', 'xls', 'xlsm', 'xlsx', 'bak', 'cab', 'cfg', 'cpl', 'cur', 'dll', 'dmp', 'drv', 'icns', 'ini', 'lnk', 'sys', 'tmp', '3g2', '3gp', 'avi', 'flv', 'h264', 'm4v', 'mkv', 'mov', 'mp4', 'mpg', 'mpeg', 'rm', 'swf', 'vob', 'wmv', 'doc', 'docx', 'odt', 'pdf', 'rtf', 'tex', 'txt', 'wpd', 'srt', 'sub']
clean_categories = ['Audio', 'Compressed', 'Disc and media', 'Data and database', 'E-mail', 'Executable', 'Font', 'Image', 'Internet', 'Presentation', 'Programming', 'Spreadsheet', 'System', 'Video', 'Word']
extension_category_id = [['aif', 1], ['cda', 1], ['mid', 1], ['midi', 1], ['mp3', 1], ['mpa', 1], ['ogg', 1], ['wav', 1], ['wma', 1], ['wpl', 1], ['7z', 2], ['arj', 2], ['deb', 2], ['pkg', 2], ['rar', 2], ['rpm', 2], ['tar.gz', 2], ['z', 2], ['zip', 2], ['dmg', 3], ['iso', 3], ['toast', 3], ['vcd', 3], ['csv', 4], ['dat', 4], ['db', 4], ['dbf', 4], ['log', 4], ['mdb', 4], ['sav', 4], ['sql', 4], ['tar', 4], ['xml', 4], ['email', 5], ['eml', 5], ['emlx', 5], ['msg', 5], ['oft', 5], ['ost', 5], ['pst', 5], ['vcf', 5], ['apk', 6], ['bat', 6], ['bin', 6], ['cgi', 6], ['com', 6], ['exe', 6], ['gadget', 6], ['jar', 6], ['msi', 6], ['wsf', 6], ['fnt', 7], ['fon', 7], ['otf', 7], ['ttf', 7], ['ai', 8], ['bmp', 8], ['gif', 8], ['ico', 8], ['jpeg', 8], ['jpg', 8], ['png', 8], ['ps', 8], ['psd', 8], ['svg', 8], ['tif', 8], ['tiff', 8], ['asp', 9], ['aspx', 9], ['cer', 9], ['cfm', 9], ['css', 9], ['htm', 9], ['html', 9], ['js', 9], ['jsp', 9], ['part', 9], ['rss', 9], ['xhtml', 9], ['key', 10], ['odp', 10], ['pps', 10], ['ppt', 10], ['pptx', 10], ['c', 11], ['pl', 11], ['class', 11], ['cpp', 11], ['cs', 11], ['h', 11], ['java', 11], ['php', 11], ['py', 11], ['sh', 11], ['swift', 11], ['vb', 11], ['json', 11], ['ods', 12], ['xls', 12], ['xlsm', 12], ['xlsx', 12], ['bak', 13], ['cab', 13], ['cfg', 13], ['cpl', 13], ['cur', 13], ['dll', 13], ['dmp', 13], ['drv', 13], ['icns', 13], ['ini', 13], ['lnk', 13], ['sys', 13], ['tmp', 13], ['3g2', 14], ['3gp', 14], ['avi', 14], ['flv', 14], ['h264', 14], ['m4v', 14], ['mkv', 14], ['mov', 14], ['mp4', 14], ['mpg', 14], ['mpeg', 14], ['rm', 14], ['swf', 14], ['vob', 14], ['wmv', 14], ['srt', 14], ['sub', 14], ['doc', 15], ['docx', 15], ['odt', 15], ['pdf', 15], ['rtf', 15], ['tex', 15], ['txt', 15], ['wpd', 15]]
extension_category_id_preselected = [['aif', 1, 0], ['cda', 1, 0], ['mid', 1, 0], ['midi', 1, 0], ['mp3', 1, 1], ['mpa', 1, 0], ['ogg', 1, 1], ['wav', 1, 0], ['wma', 1, 0], ['wpl', 1, 0], ['7z', 2, 0], ['arj', 2, 0], ['deb', 2, 0], ['pkg', 2, 0], ['rar', 2, 1], ['rpm', 2, 0], ['tar.gz', 2, 0], ['z', 2, 0], ['zip', 2, 1], ['dmg', 3, 0], ['iso', 3, 0], ['toast', 3, 0], ['vcd', 3, 0], ['csv', 4, 1], ['dat', 4, 0], ['db', 4, 1], ['dbf', 4, 0], ['log', 4, 0], ['mdb', 4, 0], ['sav', 4, 0], ['sql', 4, 1], ['tar', 4, 0], ['xml', 4, 1], ['email', 5, 0], ['eml', 5, 0], ['emlx', 5, 0], ['msg', 5, 0], ['oft', 5, 0], ['ost', 5, 0], ['pst', 5, 0], ['vcf', 5, 0], ['apk', 6, 0], ['bat', 6, 0], ['bin', 6, 0], ['cgi', 6, 0], ['com', 6, 0], ['exe', 6, 1], ['gadget', 6, 0], ['jar', 6, 0], ['msi', 6, 1], ['wsf', 6, 0], ['fnt', 7, 0], ['fon', 7, 0], ['otf', 7, 1], ['ttf', 7, 1], ['ai', 8, 1], ['bmp', 8, 0], ['gif', 8, 0], ['ico', 8, 0], ['jpeg', 8, 1], ['jpg', 8, 1], ['png', 8, 1], ['ps', 8, 0], ['psd', 8, 0], ['svg', 8, 0], ['tif', 8, 0], ['tiff', 8, 0], ['asp', 9, 1], ['aspx', 9, 1], ['cer', 9, 0], ['cfm', 9, 0], ['css', 9, 1], ['htm', 9, 0], ['html', 9, 1], ['js', 9, 1], ['jsp', 9, 0], ['part', 9, 0], ['rss', 9, 0], ['xhtml', 9, 0], ['key', 10, 0], ['odp', 10, 0], ['pps', 10, 0], ['ppt', 10, 1], ['pptx', 10, 1], ['c', 11, 0], ['pl', 11, 0], ['class', 11, 0], ['cpp', 11, 0], ['cs', 11, 0], ['h', 11, 1], ['java', 11, 1], ['php', 11, 1], ['py', 11, 1], ['sh', 11, 1], ['swift', 11, 0], ['vb', 11, 0], ['json', 11, 0], ['ods', 12, 1], ['xls', 12, 1], ['xlsm', 12, 1], ['xlsx', 12, 1], ['bak', 13, 0], ['cab', 13, 0], ['cfg', 13, 0], ['cpl', 13, 0], ['cur', 13, 0], ['dll', 13, 0], ['dmp', 13, 0], ['drv', 13, 0], ['icns', 13, 0], ['ini', 13, 0], ['lnk', 13, 0], ['sys', 13, 0], ['tmp', 13, 0], ['3g2', 14, 0], ['3gp', 14, 0], ['avi', 14, 1], ['flv', 14, 0], ['h264', 14, 0], ['m4v', 14, 1], ['mkv', 14, 1], ['mov', 14, 0], ['mp4', 14, 1], ['mpg', 14, 1], ['mpeg', 14, 1], ['rm', 14, 0], ['swf', 14, 0], ['vob', 14, 0], ['wmv', 14, 1], ['srt', 14, 1], ['sub', 14, 1], ['doc', 15, 1], ['docx', 15, 1], ['odt', 15, 1], ['pdf', 15, 1], ['rtf', 15, 0], ['tex', 15, 0], ['txt', 15, 0], ['wpd', 15, 0]]




categories = {
        "Audio": ["aif", "cda", "mid", "midi", "mp3", "mpa", "ogg", "wav", "wma", "wpl"],
        "Compressed": ["7z", "arj", "deb", "pkg", "rar", "rpm", "tar.gz", "z", "zip"],
        "Disc and media": ["dmg", "iso", "toast", "vcd"],
        "Data and database": ["csv", "dat", "db", "dbf", "log", "mdb", "sav", "sql", "tar", "xml"],
        "E-mail": ["email", "eml", "emlx", "msg", "oft", "ost", "pst", "vcf"],
        "Executable": ["apk", "bat", "bin", "cgi", "com", "exe", "gadget", "jar", "msi", "wsf"],
        "Font": ["fnt", "fon", "otf", "ttf"],
        "Image": ["ai", "bmp", "gif", "ico", "jpeg", "jpg", "png", "ps", "psd", "svg", "tif", "tiff"],
        "Internet": ["asp", "aspx", "cer", "cfm", "css", "htm", "html", "js", "jsp", "part", "rss", "xhtml"],
        "Presentation": ["key", "odp", "pps", "ppt", "pptx"],
        "Programming": ["c", "pl", "class", "cpp", "cs", "h", "java", "php", "py", "sh", "swift", "vb", "json"],
        "Spreadsheet": ["ods", "xls", "xlsm", "xlsx"],
        "System": ["bak", "cab", "cfg", "cpl", "cur", "dll", "dmp", "drv", "icns", "ini", "lnk", "sys", "tmp"],
        "Video": ["3g2", "3gp", "avi", "flv", "h264", "m4v", "mkv", "mov", "mp4", "mpg", "mpeg", "rm", "swf", "vob", "wmv", "srt", "sub"],
        "Word": ["doc", "docx", "odt", "pdf", "rtf", "tex", "txt", "wpd"]
    }

preselected_extension = ['mp3', 'ogg', 'rar', 'zip', 'csv', 'db', 'sql', 'xml', 'exe',
                         'msi', 'py', 'otf', 'ttf', 'ai', 'jpeg', 'jpg', 'png', 'asp', 'aspx', 'css',
                         'html', 'js', 'php', 'ppt', 'pptx', 'h', 'java', 'sh', 'ods', 'xls', 'xlsm',
                         'xlsx', 'avi', 'm4v', 'mkv', 'mp4', 'mpg', 'mpeg', 'wmv', 'doc', 'docx', 'odt',
                         'pdf', 'srt', 'sub']


exts = []
singular = []
duplicates = []

idx = 1
for category, extensions in categories.items():
    for extension in extensions:
        if extension in preselected_extension:
            preselect = 1
        else:
            preselect = 0
        if extension not in exts:
            exts.append(extension)
            singular.append([extension, idx, preselect])
        else:
            duplicates.append([extension, category, idx])
    idx = idx + 1

print(singular)
print(duplicates)

