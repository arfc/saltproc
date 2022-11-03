NUM_REGEX = '-?[0-9]+(\.[0-9]+)?'
COMMENT_IGNORE_BEG_REGEX = '^\s*[^%]*\s*'
COMMENT_IGNORE_END_REGEX = '\s*[^%]*'
BC_REGEX_CORE = 'set\s+bc(\s+([1-3]|black|reflective|periodic)){1,3}'
SURF_REGEX_CORE = 'surf\s+[a-zA-Z0-9]+\s+[a-z]{2,}(\s+' + \
    NUM_REGEX + '\s*)*'
CELL_REGEX1_CORE = 'cell(\s+[a-zA-Z0-9]+){3}'
CELL_REGEX2_CORE = 'cell(\s+[a-zA-Z0-9]+){2}\s+fill\s+[a-zA-Z0-9]+'
CELL_REGEX3_CORE = 'cell(\s+[a-zA-Z0-9]+){2}\s+outside'
CELL_SURFACE_REGEX = '(\s+\-?\:?\#?[a-zA-Z0-9]+)+'
ROOT_REGEX_CORE = 'set\s+root\s+[a-zA-Z0-9]+'
USYM_REGEX_CORE = 'set\s+usym\s+[a-zA-Z0-9]+\s+(1|2|3)\s+(\s+' + \
    NUM_REGEX + ')'
TRANS_REGEX_CORE = 'trans\s+[A-Z]{1}\s+[a-zA-Z0-9]+(\s+' + NUM_REGEX + ')+'
CARD_IGNORE_REGEX = '^\s*(?!.*%)(?!.*lat)(?!.*cell)(?!.*set)(?!.*surf)' + \
    '(?!.*dtrans)(?!.*ftrans)(?!.*ltrans)(?!.*pin)(?!.*solid)(?!.*strans)' + \
    '(?!.*trans)'
LAT_REGEX_CORE = 'lat\s+[a-zA-Z0-9]+\s+[0-9]{1,2}(\s+' + NUM_REGEX + \
    '){2,4}(\s+[0-9]+){0,3}((\s+' + NUM_REGEX + '){0,2}\s+[a-zA-Z0-9]+)+'
# right now this is limiting universe names to 3 chars until I can come up
# witha more robust regex
LAT_MULTILINE_REGEX_CORE = '\s*((' + NUM_REGEX + '\s+){0,2}[a-zA-Z0-9]{1,3}\s+)+'
BC_REGEX = COMMENT_IGNORE_BEG_REGEX + \
    BC_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX
SURF_REGEX = COMMENT_IGNORE_BEG_REGEX + \
    SURF_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX
CELL_REGEX1 = COMMENT_IGNORE_BEG_REGEX + \
    CELL_REGEX1_CORE + \
    CELL_SURFACE_REGEX + \
    COMMENT_IGNORE_END_REGEX
CELL_REGEX2 = COMMENT_IGNORE_BEG_REGEX + \
    CELL_REGEX2_CORE + \
    CELL_SURFACE_REGEX + \
    COMMENT_IGNORE_END_REGEX
CELL_REGEX3 = COMMENT_IGNORE_BEG_REGEX + \
    CELL_REGEX3_CORE + \
    CELL_SURFACE_REGEX + \
    COMMENT_IGNORE_END_REGEX
CELL_REGEX_ALL = COMMENT_IGNORE_BEG_REGEX + \
    f'({CELL_REGEX2_CORE}|{CELL_REGEX3_CORE}|{CELL_REGEX1_CORE})' + \
    CELL_SURFACE_REGEX + \
    COMMENT_IGNORE_END_REGEX
ROOT_REGEX = COMMENT_IGNORE_BEG_REGEX + \
    ROOT_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX
USYM_REGEX = COMMENT_IGNORE_BEG_REGEX + \
    USYM_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX

TRANS_REGEX = COMMENT_IGNORE_BEG_REGEX + \
    TRANS_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX
LAT_REGEX = COMMENT_IGNORE_BEG_REGEX + \
    LAT_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX
LAT_MULTILINE_REGEX = CARD_IGNORE_REGEX + \
    LAT_MULTILINE_REGEX_CORE + \
    COMMENT_IGNORE_END_REGEX


