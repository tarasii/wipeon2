UPBAR$ = "220000000000"
EGG$ = "C2"
EGGC$ = "W"
LNUM$ = "01"
ENT$ = "AA"
ID$ = "000015"
SIZE 60 mm, 60 mm
CLS
BARCODE 90, 50, "EAN13", 80,  0, 90, 6, 0, UPBAR$
BARCODE 630, 650, "128", 120,  1, 270, 4, 3, ""+ENT$+LNUM$+ID$
TEXT 120, 50, "2", 270, 1, 1, ""+EGG$+" "+EGGC$
PRINT 1
EOP
