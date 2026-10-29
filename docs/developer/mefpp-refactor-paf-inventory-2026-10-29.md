# PAF template key-family inventory — 29 October 2026

Baseline: 22a32d39463a73ab32d2ba9d811f949198852902.

OCAM: 591 MEF/PHASE3 entries / 591 unique keys; WFI: 257 entries / 255 unique keys. CHIP-number families are collapsed; all template keys remain represented.

WFI repeats MEF.MASTER.BIAS.KEY (lines 235/244) and MEF.MASTER.BIAS.COMMENT (236/245) with identical values. Preserve and report these source occurrences; a migration tool must distinguish identical repetitions from conflicts. This observation does not establish a runtime processing error.

This is a lexical inventory, not a PAF parser, runtime-use proof or final TOML schema. PAF envelope fields are excluded. Native hits identify matching literal key text in mefp_lib.c, including possible comments; dynamic or indirect consumption needs review. Instrument CFG, project CFG, CLI overrides and live partition-local PAFs remain separate inputs. Domain labels are preliminary; .KEY/.COMMENT metadata can describe parameters in another domain.

| Key family | OCAM entries / first line | WFI entries / first line | Native textual line hits | Proposed domain |
|---|---|---|---|---|
| MEF.BIAS.FRAME.I.COMMENT | 1 / 570 | 1 / 234 | 554 | product/header mapping |
| MEF.BIAS.FRAME.I.KEY | 1 / 569 | 1 / 233 | 547 | product/header mapping |
| MEF.BIAS.FRAMENUM.MIN | 1 / 575 | 1 / 241 | 798 | processing/recipe review |
| MEF.BIAS.FRAMETHR.HI | 1 / 573 | 1 / 239 | not found | processing/recipe review |
| MEF.BIAS.FRAMETHR.LO | 1 / 572 | 1 / 238 | not found | processing/recipe review |
| MEF.BIAS.KAPPA1 | 1 / 574 | 1 / 240 | 792 | processing/recipe review |
| MEF.BIAS.NAME.O | 1 / 571 | 1 / 237 | 576 | product/header mapping |
| MEF.BINX.KEY | 1 / 79 | 1 / 79 | 774 | product/header mapping |
| MEF.BINY.KEY | 1 / 80 | 1 / 80 | 783 | product/header mapping |
| MEF.BPM.FRAME.I.COMMENT | 1 / 585 | 1 / 251 | 621 | product/header mapping |
| MEF.BPM.FRAME.I.KEY | 1 / 584 | 1 / 250 | 614 | product/header mapping |
| MEF.BPM.HGAINTHR | 1 / 594 | 1 / 260 | 816 | processing/recipe review |
| MEF.BPM.HGAINTHR.COMMENT | 1 / 593 | 1 / 259 | 663 | product/header mapping |
| MEF.BPM.HGAINTHR.KEY | 1 / 592 | 1 / 258 | 656 | product/header mapping |
| MEF.BPM.LGAINTHR | 1 / 591 | 1 / 257 | 810 | processing/recipe review |
| MEF.BPM.LGAINTHR.COMMENT | 1 / 590 | 1 / 256 | 649 | product/header mapping |
| MEF.BPM.LGAINTHR.KEY | 1 / 589 | 1 / 255 | 642 | product/header mapping |
| MEF.BPM.NAME | 1 / 582 | 1 / 248 | 607 | processing/recipe review |
| MEF.BPM.NAME.O | 1 / 583 | 1 / 249 | 583 | product/header mapping |
| MEF.BPM.PROPFLAG | 1 / 588 | 1 / 254 | 804 | processing/recipe review |
| MEF.BPM.PROPFLAG.COMMENT | 1 / 587 | 1 / 253 | 635 | product/header mapping |
| MEF.BPM.PROPFLAG.KEY | 1 / 586 | 1 / 252 | 628 | product/header mapping |
| MEF.CCD.GAIN.CHIP{n} | 32 / 535 | 8 / 223 | 199 | instrument/detector |
| MEF.CCD.GAIN.COMMENT | 1 / 534 | 1 / 222 | 1074 | product/header mapping |
| MEF.CCD.GAIN.I.KEY | 1 / 533 | 1 / 221 | 1067 | product/header mapping |
| MEF.CCD.GAIN.KEY | 1 / 532 | 1 / 220 | 1060 | product/header mapping |
| MEF.CCD.RON.CHIP{n} | 32 / 499 | 8 / 211 | 193 | instrument/detector |
| MEF.CCD.RON.COMMENT | 1 / 498 | 1 / 210 | 1053 | product/header mapping |
| MEF.CCD.RON.I.KEY | 1 / 497 | 1 / 209 | 1046 | product/header mapping |
| MEF.CCD.RON.KEY | 1 / 496 | 1 / 208 | 1039 | product/header mapping |
| MEF.CORRECT.REFPIXELS | 1 / 222 | 1 / 126 | 254 | processing/recipe review |
| MEF.CROP.X.MAX.CHIP{n} | 32 / 367 | 8 / 175 | 175 | instrument/detector |
| MEF.CROP.X.MIN.CHIP{n} | 32 / 366 | 8 / 174 | 169 | instrument/detector |
| MEF.CROP.Y.MAX.CHIP{n} | 32 / 369 | 8 / 177 | 187 | instrument/detector |
| MEF.CROP.Y.MIN.CHIP{n} | 32 / 368 | 8 / 176 | 181 | instrument/detector |
| MEF.CRPIX1.CHIP{n} | 32 / 228 | 8 / 132 | 217 | instrument/detector |
| MEF.CRPIX2.CHIP{n} | 32 / 229 | 8 / 133 | 223 | instrument/detector |
| MEF.CRVAL1.CHIP{n} | 32 / 226 | 8 / 130 | 205 | instrument/detector |
| MEF.CRVAL2.CHIP{n} | 32 / 227 | 8 / 131 | 211 | instrument/detector |
| MEF.DOMEFF.FRAME.I.COMMENT | 1 / 602 | 1 / 268 | 829 | product/header mapping |
| MEF.DOMEFF.FRAME.I.KEY | 1 / 601 | 1 / 267 | 822 | product/header mapping |
| MEF.DOMEFF.FRAMENUM.MIN | 1 / 612 | 1 / 278 | 891 | processing/recipe review |
| MEF.DOMEFF.FRAMENUM.MIN.COMMENT | 1 / 611 | 1 / 277 | 884 | product/header mapping |
| MEF.DOMEFF.FRAMENUM.MIN.KEY | 1 / 610 | 1 / 276 | 877 | product/header mapping |
| MEF.DOMEFF.FRAMETHR.HI | 1 / 609 | 1 / 275 | 871 | processing/recipe review |
| MEF.DOMEFF.FRAMETHR.HI.COMMENT | 1 / 608 | 1 / 274 | 864 | product/header mapping |
| MEF.DOMEFF.FRAMETHR.HI.KEY | 1 / 607 | 1 / 273 | 857 | product/header mapping |
| MEF.DOMEFF.FRAMETHR.LO | 1 / 606 | 1 / 272 | 850 | processing/recipe review |
| MEF.DOMEFF.FRAMETHR.LO.COMMENT | 1 / 605 | 1 / 271 | 843 | product/header mapping |
| MEF.DOMEFF.FRAMETHR.LO.KEY | 1 / 604 | 1 / 270 | 836 | product/header mapping |
| MEF.DOMEFF.NAME.O | 1 / 603 | 1 / 269 | 700 | product/header mapping |
| MEF.DPR.CATG.COMMENT | 1 / 19 | 1 / 19 | 274 | product/header mapping |
| MEF.DPR.CATG.KEY | 1 / 18 | 1 / 18 | 267 | product/header mapping |
| MEF.DPR.TYPE.COMMENT | 1 / 21 | 1 / 21 | 288 | product/header mapping |
| MEF.DPR.TYPE.KEY | 1 / 20 | 1 / 20 | 281 | product/header mapping |
| MEF.FILTER.KEY | 1 / 78 | 1 / 78 | 765 | product/header mapping |
| MEF.INSTRUMENT | 1 / 15 | 1 / 15 | 247 | instrument/mapping |
| MEF.KERN.HSIZE | 1 / 655 | 1 / 321 | 1177 | processing/recipe review |
| MEF.KERN.HSIZE.COMMENT | 1 / 654 | 1 / 320 | 1170 | product/header mapping |
| MEF.KERN.HSIZE.KEY | 1 / 653 | 1 / 319 | 1163 | product/header mapping |
| MEF.MASTER.BIAS.COMMENT | 1 / 579 | 2 / 236 | 569 | product/header mapping |
| MEF.MASTER.BIAS.KEY | 1 / 578 | 2 / 235 | 562 | product/header mapping |
| MEF.MASTER.BPM.COMMENT | 1 / 598 | 1 / 264 | 677 | product/header mapping |
| MEF.MASTER.BPM.KEY | 1 / 597 | 1 / 263 | 670 | product/header mapping |
| MEF.MASTER.DOME.COMMENT | 1 / 616 | 1 / 282 | 693 | product/header mapping |
| MEF.MASTER.DOME.KEY | 1 / 615 | 1 / 281 | 686 | product/header mapping |
| MEF.MASTER.FLAT.COMMENT | 1 / 658 | 1 / 324 | 745 | product/header mapping |
| MEF.MASTER.FLAT.KEY | 1 / 657 | 1 / 323 | 738 | product/header mapping |
| MEF.MASTER.SKY.COMMENT | 1 / 634 | 1 / 300 | 715 | product/header mapping |
| MEF.MASTER.SKY.KEY | 1 / 633 | 1 / 299 | 708 | product/header mapping |
| MEF.MEDIAN.REG.COMMENT | 1 / 645 | 1 / 311 | 1128 | product/header mapping |
| MEF.MEDIAN.REG.KEY | 1 / 644 | 1 / 310 | 1121 | product/header mapping |
| MEF.MEDIAN.REG.X1 | 1 / 646 | 1 / 312 | 1135 | processing/recipe review |
| MEF.MEDIAN.REG.X2 | 1 / 647 | 1 / 313 | 1141 | processing/recipe review |
| MEF.MEDIAN.REG.Y1 | 1 / 648 | 1 / 314 | 1147 | processing/recipe review |
| MEF.MEDIAN.REG.Y2 | 1 / 649 | 1 / 315 | 1153 | processing/recipe review |
| MEF.MFF.NAME.O | 1 / 652 | 1 / 318 | 729 | product/header mapping |
| MEF.NCHIPS | 1 / 74 | 1 / 74 | 111 | instrument/mapping |
| MEF.ORIGIN | 1 / 13 | 1 / 13 | 233 | instrument/mapping |
| MEF.OVERSCAN.X.COMMENT | 1 / 153 | 1 / 106 | 992 | product/header mapping |
| MEF.OVERSCAN.X.KEY | 1 / 152 | 1 / 105 | 985 | product/header mapping |
| MEF.OVERSCAN.X.MAX.CHIP{n} | 32 / 155 | 8 / 108 | 163 | instrument/detector |
| MEF.OVERSCAN.X.MIN.CHIP{n} | 32 / 154 | 8 / 107 | 157 | instrument/detector |
| MEF.PIXREJ.SIGMA.HI | 1 / 642 | 1 / 308 | 1115 | processing/recipe review |
| MEF.PIXREJ.SIGMA.HI.COMMENT | 1 / 641 | 1 / 307 | 1108 | product/header mapping |
| MEF.PIXREJ.SIGMA.HI.KEY | 1 / 640 | 1 / 306 | 1101 | product/header mapping |
| MEF.PIXREJ.SIGMA.LO | 1 / 639 | 1 / 305 | 1095 | processing/recipe review |
| MEF.PIXREJ.SIGMA.LO.COMMENT | 1 / 638 | 1 / 304 | 1088 | product/header mapping |
| MEF.PIXREJ.SIGMA.LO.KEY | 1 / 637 | 1 / 303 | 1081 | product/header mapping |
| MEF.PRESCAN.X.COMMENT | 1 / 85 | 1 / 85 | 978 | product/header mapping |
| MEF.PRESCAN.X.KEY | 1 / 84 | 1 / 84 | 971 | product/header mapping |
| MEF.PRESCAN.X.MAX.CHIP{n} | 32 / 87 | 8 / 87 | 151 | instrument/detector |
| MEF.PRESCAN.X.MIN.CHIP{n} | 32 / 86 | 8 / 86 | 145 | instrument/detector |
| MEF.RECIPE.KEY | 1 / 16 | 1 / 16 | 260 | product/header mapping |
| MEF.REFPIX.X | 1 / 223 | 1 / 127 | 753 | instrument/detector |
| MEF.REFPIX.Y | 1 / 224 | 1 / 128 | 759 | instrument/detector |
| MEF.SATLEVEL | 1 / 75 | 1 / 75 | 1186 | processing/recipe review |
| MEF.SATMAX | 1 / 76 | 1 / 76 | 1192 | processing/recipe review |
| MEF.SCANREJ.COMMENT | 1 / 358 | 1 / 165 | 1006 | product/header mapping |
| MEF.SCANREJ.KEY | 1 / 357 | 1 / 164 | 999 | product/header mapping |
| MEF.SCANREJ.MAX | 1 / 360 | 1 / 167 | 1019 | processing/recipe review |
| MEF.SCANREJ.MIN | 1 / 359 | 1 / 166 | 1013 | processing/recipe review |
| MEF.SKYFF.FRAME.I.COMMENT | 1 / 620 | 1 / 286 | 904 | product/header mapping |
| MEF.SKYFF.FRAME.I.KEY | 1 / 619 | 1 / 285 | 897 | product/header mapping |
| MEF.SKYFF.FRAMENUM.MIN | 1 / 630 | 1 / 296 | 965 | processing/recipe review |
| MEF.SKYFF.FRAMENUM.MIN.COMMENT | 1 / 629 | 1 / 295 | 958 | product/header mapping |
| MEF.SKYFF.FRAMENUM.MIN.KEY | 1 / 628 | 1 / 294 | 951 | product/header mapping |
| MEF.SKYFF.FRAMETHR.HI | 1 / 627 | 1 / 293 | 945 | processing/recipe review |
| MEF.SKYFF.FRAMETHR.HI.COMMENT | 1 / 626 | 1 / 292 | 938 | product/header mapping |
| MEF.SKYFF.FRAMETHR.HI.KEY | 1 / 625 | 1 / 291 | 931 | product/header mapping |
| MEF.SKYFF.FRAMETHR.LO | 1 / 624 | 1 / 290 | 925 | processing/recipe review |
| MEF.SKYFF.FRAMETHR.LO.COMMENT | 1 / 623 | 1 / 289 | 918 | product/header mapping |
| MEF.SKYFF.FRAMETHR.LO.KEY | 1 / 622 | 1 / 288 | 911 | product/header mapping |
| MEF.SKYFF.NAME.O | 1 / 621 | 1 / 287 | 722 | product/header mapping |
| MEF.TELESCOPE | 1 / 14 | 1 / 14 | 240 | instrument/mapping |
| MEF.TRIMREG.COMMENT | 1 / 364 | 1 / 172 | 1032 | product/header mapping |
| MEF.TRIMREG.KEY | 1 / 363 | 1 / 171 | 1025 | product/header mapping |
| MEF.USE.OVERSCAN | 1 / 151 | 1 / 104 | 541 | processing/recipe review |
| MEF.USE.PRESCAN | 1 / 83 | 1 / 83 | 535 | processing/recipe review |
| PHASE3.FILTER.COMMENT | 1 / 62 | 1 / 62 | 486 | product/header mapping |
| PHASE3.FILTER.KEY.NAME | 1 / 61 | 1 / 61 | 479 | product/header mapping |
| PHASE3.FLUXCAL.COMMENT | 1 / 67 | 1 / 67 | 507 | product/header mapping |
| PHASE3.FLUXCAL.HDRKEY | 1 / 65 | 1 / 65 | not found | product/header mapping |
| PHASE3.FLUXCAL.KEY.NAME | 1 / 64 | 1 / 64 | 493 | product/header mapping |
| PHASE3.FLUXCAL.VAL | 1 / 66 | 1 / 66 | 500 | product/header mapping |
| PHASE3.MJDEND.COMMENT | 1 / 50 | 1 / 50 | 437 | product/header mapping |
| PHASE3.MJDEND.HDRKEY | 1 / 49 | 1 / 49 | not found | product/header mapping |
| PHASE3.MJDEND.KEY.NAME | 1 / 48 | 1 / 48 | 430 | product/header mapping |
| PHASE3.NCOMBINE.COMMENT | 1 / 42 | 1 / 42 | 402 | product/header mapping |
| PHASE3.NCOMBINE.KEY.NAME | 1 / 41 | 1 / 41 | 395 | product/header mapping |
| PHASE3.OBID.COMMENT | 1 / 39 | 1 / 39 | 388 | product/header mapping |
| PHASE3.OBID.HDRKEY | 1 / 38 | 1 / 38 | 381 | product/header mapping |
| PHASE3.OBID.KEY.NAME | 1 / 37 | 1 / 37 | 374 | product/header mapping |
| PHASE3.OBSTECH.COMMENT | 1 / 46 | 1 / 46 | 423 | product/header mapping |
| PHASE3.OBSTECH.HDRKEY | 1 / 45 | 1 / 45 | 416 | product/header mapping |
| PHASE3.OBSTECH.KEY.NAME | 1 / 44 | 1 / 44 | 409 | product/header mapping |
| PHASE3.PROCSOFT.COMMENT | 1 / 54 | 1 / 54 | 451 | product/header mapping |
| PHASE3.PROCSOFT.HDRKEY | 1 / 53 | 1 / 53 | not found | product/header mapping |
| PHASE3.PROCSOFT.KEY.NAME | 1 / 52 | 1 / 52 | 444 | product/header mapping |
| PHASE3.PRODCATG.COMMENT | 1 / 31 | 1 / 31 | 346 | product/header mapping |
| PHASE3.PRODCATG.KEY.NAME | 1 / 24 | 1 / 24 | 297 | product/header mapping |
| PHASE3.PRODCATG.VAL.BIAS | 1 / 27 | 1 / 26 | 304 | product/header mapping |
| PHASE3.PRODCATG.VAL.BPM | 1 / 26 | 1 / 27 | 311 | product/header mapping |
| PHASE3.PRODCATG.VAL.DOMEFF | 1 / 28 | 1 / 28 | 318 | product/header mapping |
| PHASE3.PRODCATG.VAL.MFF | 1 / 30 | 1 / 30 | 332 | product/header mapping |
| PHASE3.PRODCATG.VAL.SCIENCE | 1 / 25 | 1 / 25 | 339 | product/header mapping |
| PHASE3.PRODCATG.VAL.SKYFF | 1 / 29 | 1 / 29 | 325 | product/header mapping |
| PHASE3.PROGID.COMMENT | 1 / 35 | 1 / 35 | 367 | product/header mapping |
| PHASE3.PROGID.HDRKEY | 1 / 34 | 1 / 34 | 360 | product/header mapping |
| PHASE3.PROGID.KEY.NAME | 1 / 33 | 1 / 33 | 353 | product/header mapping |
| PHASE3.RADESYS.COMMENT | 1 / 71 | 1 / 71 | 528 | product/header mapping |
| PHASE3.RADESYS.HDRKEY | 1 / 70 | 1 / 70 | 521 | product/header mapping |
| PHASE3.RADESYS.KEY.NAME | 1 / 69 | 1 / 69 | 514 | product/header mapping |
| PHASE3.TIMESYS.COMMENT | 1 / 59 | 1 / 59 | 472 | product/header mapping |
| PHASE3.TIMESYS.HDRKEY | 1 / 57 | 1 / 57 | not found | product/header mapping |
| PHASE3.TIMESYS.KEY.NAME | 1 / 56 | 1 / 56 | 458 | product/header mapping |
| PHASE3.TIMESYS.VAL | 1 / 58 | 1 / 58 | 465 | product/header mapping |
