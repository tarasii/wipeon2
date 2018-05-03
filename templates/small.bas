UPBAR$ = "{barcodeEAN}"
EGG$ = "{category}"
EGGC$ = "{color}"
LNUM$ = "{line}"
ENT$ = "{enterprise}"
ID$ = "{id}"
SIZE 60 mm, 60 mm
CLS
BARCODE 50, 20, "EAN13", 150,  0, 0, 4, 0, UPBAR$
BARCODE 80, 260, "128", 170,  1, 0, 3, 3, ""+ENT$+LNUM$+ID$
TEXT 100, 180, "2", 0, 5, 4, ""+EGG$+" "+EGGC$
PRINT 1
EOP
