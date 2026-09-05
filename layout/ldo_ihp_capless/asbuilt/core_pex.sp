*********************************************************
*** NGSPICE file created by KLayout-PEX 0.3.12
*** -----------------------------------------------------
***     Extraction Engine: KPEX/2.5D
***     Technology: ihp_sg13g2
***     Date: 2026-09-04 23:15:58
*********************************************************

.subckt ldo_ihp_capless vdd vout vss
VREF vref vss dc {vref_val}
* kpex hangs every extracted ground capacitance on a substrate node VSUBS that is NOT in the
* subckt pin list; the p-substrate is at vss through the layout's own ptap ring, so tie it (a 0 V
* source rather than a rename, so the substrate branch stays visible to a reviewer). Without this
* the operating point is singular at `xdut.vsubs`.
VSUBSTIE VSUBS vss dc 0
VLP lp_brk vout dc 0
XCFF lp_brk fb cap_cmim w=c_ff_w l=c_ff_w
XCC ea_out ea_o1 cap_cmim w=c_comp_w l=c_comp_w
XCOUT vout vss cap_cmim w=c_out_w l=c_out_w m=c_out_m
XMn_1 y x1 vss vss sg13_lv_nmos L=0.5U W=5.79U AS=1.9686P AD=1.9686P PS=12.26U
+ PD=12.26U rfmode=0
XMn_2 x1 x1 vss vss sg13_lv_nmos L=0.5U W=5.79U AS=1.9686P AD=1.9686P PS=12.26U
+ PD=12.26U rfmode=0
XMn_3 ea_out ea_o1 vss vss sg13_lv_nmos L=0.5U W=2.42U AS=0.8228P AD=0.8228P
+ PS=5.52U PD=5.52U rfmode=0
XMn_4 gate nbias vss vss sg13_lv_nmos L=0.95U W=1.1U AS=0.374P AD=0.374P PS=2.88U
+ PD=2.88U rfmode=0
XMn_5 nbias nbias vss vss sg13_lv_nmos L=1U W=0.5U AS=0.17P AD=0.17P PS=1.68U
+ PD=1.68U rfmode=0
XMn_6 ea_o1 ea_n vss vss sg13_lv_nmos L=1U W=1.475U AS=0.5015P AD=0.5015P
+ PS=3.63U PD=3.63U rfmode=0
XMn_7 ea_n ea_n vss vss sg13_lv_nmos L=1U W=1.475U AS=0.5015P AD=0.5015P PS=3.63U
+ PD=3.63U rfmode=0
XMn_8 pbias nbias vss vss sg13_lv_nmos L=1U W=0.695U AS=0.2363P AD=0.2363P
+ PS=2.07U PD=2.07U rfmode=0
XMn_9 ea_n ea_n vss vss sg13_lv_nmos L=1U W=1.475U AS=0.5015P AD=0.5015P PS=3.63U
+ PD=3.63U rfmode=0
XMn_10 pbias nbias vss vss sg13_lv_nmos L=1U W=0.695U AS=0.2363P AD=0.2363P
+ PS=2.07U PD=2.07U rfmode=0
XMn_11 nbias nbias vss vss sg13_lv_nmos L=1U W=0.5U AS=0.17P AD=0.17P PS=1.68U
+ PD=1.68U rfmode=0
XMn_12 gate nbias vss vss sg13_lv_nmos L=0.95U W=1.1U AS=0.374P AD=0.374P
+ PS=2.88U PD=2.88U rfmode=0
XMn_13 ea_o1 ea_n vss vss sg13_lv_nmos L=1U W=1.475U AS=0.5015P AD=0.5015P
+ PS=3.63U PD=3.63U rfmode=0
XMn_14 pbias pbias vdd vdd sg13_lv_pmos L=1U W=10U AS=3.4P AD=3.4P PS=20.68U
+ PD=20.68U rfmode=0
XMn_15 ea_tail pbias vdd vdd sg13_lv_pmos L=1U W=10U AS=3.4P AD=3.4P PS=20.68U
+ PD=20.68U rfmode=0
XMn_16 ea_out pbias vdd vdd sg13_lv_pmos L=1U W=5.53U AS=1.8802P AD=1.8802P
+ PS=11.74U PD=11.74U rfmode=0
XMn_17 ea_n fb ea_tail vdd sg13_lv_pmos L=0.5U W=4.765U AS=1.6201P AD=1.6201P
+ PS=10.21U PD=10.21U rfmode=0
XMn_18 ea_o1 vref ea_tail vdd sg13_lv_pmos L=0.5U W=4.765U AS=1.6201P AD=1.6201P
+ PS=10.21U PD=10.21U rfmode=0
XMn_19 ea_o1 vref ea_tail vdd sg13_lv_pmos L=0.5U W=4.765U AS=1.6201P AD=1.6201P
+ PS=10.21U PD=10.21U rfmode=0
XMn_20 ea_n fb ea_tail vdd sg13_lv_pmos L=0.5U W=4.765U AS=1.6201P AD=1.6201P
+ PS=10.21U PD=10.21U rfmode=0
XMn_21 x1 ea_out vout vdd sg13_lv_pmos L=0.36U W=15.76U AS=5.3584P AD=5.3584P
+ PS=32.2U PD=32.2U rfmode=0
XMn_22 y y vdd vdd sg13_lv_pmos L=0.5U W=9.02U AS=3.0668P AD=3.0668P PS=18.72U
+ PD=18.72U rfmode=0
XMn_23 gate y vdd vdd sg13_lv_pmos L=0.5U W=9.02U AS=3.0668P AD=3.0668P PS=18.72U
+ PD=18.72U rfmode=0
XMn_24 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.85P AD=0.475P PS=5.68U
+ PD=2.88U rfmode=0
XMn_25 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_26 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_27 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_28 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_29 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_30 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_31 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_32 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_33 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_34 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_35 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_36 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_37 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_38 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_39 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_40 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_41 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_42 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_43 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_44 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_45 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_46 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_47 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_48 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_49 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_50 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_51 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_52 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_53 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_54 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_55 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_56 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_57 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_58 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_59 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_60 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_61 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_62 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_63 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_64 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_65 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_66 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_67 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_68 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_69 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_70 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_71 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_72 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_73 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_74 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_75 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_76 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_77 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_78 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_79 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_80 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_81 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_82 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_83 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_84 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_85 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_86 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_87 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_88 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_89 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_90 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_91 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_92 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_93 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_94 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_95 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_96 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_97 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_98 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_99 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.85P PS=2.88U
+ PD=5.68U rfmode=0
XRn_100 n_25 lp_brk vss rhigh w=0.5u l=42.5u m=1
XRn_101 n_26 fb vss rhigh w=0.5u l=42.5u m=1
XRn_102 n_26 n_39 vss rhigh w=0.5u l=42.5u m=1
XRn_103 n_25 n_40 vss rhigh w=0.5u l=42.5u m=1
XRn_104 n_27 n_40 vss rhigh w=0.5u l=42.5u m=1
XRn_105 n_28 n_39 vss rhigh w=0.5u l=42.5u m=1
XRn_106 n_28 n_41 vss rhigh w=0.5u l=42.5u m=1
XRn_107 n_27 n_42 vss rhigh w=0.5u l=42.5u m=1
XRn_108 n_29 n_42 vss rhigh w=0.5u l=42.5u m=1
XRn_109 n_30 n_41 vss rhigh w=0.5u l=42.5u m=1
XRn_110 n_30 n_43 vss rhigh w=0.5u l=42.5u m=1
XRn_111 n_29 n_44 vss rhigh w=0.5u l=42.5u m=1
XRn_112 n_31 n_44 vss rhigh w=0.5u l=42.5u m=1
XRn_113 n_32 n_43 vss rhigh w=0.5u l=42.5u m=1
XRn_114 n_32 vss vss rhigh w=0.5u l=42.5u m=1
XRn_115 n_31 fb vss rhigh w=0.5u l=42.5u m=1
XRn_116 vdd n_45 vss rhigh w=0.5u l=27.7u m=1
XRn_117 n_33 n_45 vss rhigh w=0.5u l=27.7u m=1
XRn_118 n_33 n_46 vss rhigh w=0.5u l=27.7u m=1
XRn_119 n_34 n_46 vss rhigh w=0.5u l=27.7u m=1
XRn_120 n_34 nbias vss rhigh w=0.5u l=27.7u m=1
Cext_1 n_25 n_26 84.7091a
Cext_2 n_25 n_27 29.1208a
Cext_3 n_25 n_28 0.382346a
Cext_4 n_25 ea_o1 46.5979a
Cext_5 n_25 fb 50.6922a
Cext_6 n_25 lp_brk 3.71789a
Cext_7 n_25 vss 17.2477a
Cext_8 n_25 VSUBS 894.53a
Cext_9 n_26 n_27 0.580868a
Cext_10 n_26 n_28 3.1728a
Cext_11 n_26 ea_o1 11.3256a
Cext_12 n_26 fb 24.5464a
Cext_13 n_26 lp_brk 3.78971a
Cext_14 n_26 vss 0.769542a
Cext_15 n_26 VSUBS 508.818a
Cext_16 n_27 n_28 84.7091a
Cext_17 n_27 n_29 29.1208a
Cext_18 n_27 n_30 0.580868a
Cext_19 n_27 ea_o1 29.4074a
Cext_20 n_27 fb 0.10108a
Cext_21 n_27 lp_brk 54.5808a
Cext_22 n_27 VSUBS 884.846a
Cext_23 n_28 n_29 0.580868a
Cext_24 n_28 n_30 5.96012a
Cext_25 n_28 ea_o1 11.1554a
Cext_26 n_28 lp_brk 15.728a
Cext_27 n_28 VSUBS 511.398a
Cext_28 n_29 n_30 85.6526a
Cext_29 n_29 n_31 29.1208a
Cext_30 n_29 n_32 0.580868a
Cext_31 n_29 ea_o1 30.2717a
Cext_32 n_29 lp_brk 0.103114a
Cext_33 n_29 VSUBS 884.846a
Cext_34 n_30 n_31 0.580868a
Cext_35 n_30 n_32 5.96012a
Cext_36 n_30 ea_o1 11.1554a
Cext_37 n_30 VSUBS 517.566a
Cext_38 n_31 n_32 85.6526a
Cext_39 n_31 ea_o1 30.2717a
Cext_40 n_31 vss 11.5305a
Cext_41 n_31 VSUBS 899.063a
Cext_42 n_32 ea_o1 11.1554a
Cext_43 n_32 vss 4.95894a
Cext_44 n_32 VSUBS 517.65a
Cext_45 n_33 n_34 12.5033a
Cext_46 n_33 ea_o1 7.54868a
Cext_47 n_33 vdd 16.8396a
Cext_48 n_33 VSUBS 365.519a
Cext_49 n_34 ea_o1 7.54868a
Cext_50 n_34 vdd 0.463827a
Cext_51 n_34 VSUBS 376.903a
Cext_52 n_39 n_40 63.2751a
Cext_53 n_39 n_41 29.9581a
Cext_54 n_39 fb 21.6148a
Cext_55 n_39 lp_brk 60.7243a
Cext_56 n_39 vss 13.4273a
Cext_57 n_39 VSUBS 766.334a
Cext_58 n_40 n_42 7.36983a
Cext_59 n_40 fb 1.50969a
Cext_60 n_40 lp_brk 28.7125a
Cext_61 n_40 vss 15.9257a
Cext_62 n_40 VSUBS 552.606a
Cext_63 n_41 n_42 65.0349a
Cext_64 n_41 n_43 29.9581a
Cext_65 n_41 lp_brk 0.165868a
Cext_66 n_41 vss 13.7644a
Cext_67 n_41 VSUBS 781.407a
Cext_68 n_42 n_44 7.36983a
Cext_69 n_42 lp_brk 0.603941a
Cext_70 n_42 vss 15.9257a
Cext_71 n_42 VSUBS 550.728a
Cext_72 n_43 n_44 65.0349a
Cext_73 n_43 fb 0.163803a
Cext_74 n_43 vss 35.0313a
Cext_75 n_43 VSUBS 787.047a
Cext_76 n_44 vss 17.3131a
Cext_77 n_44 VSUBS 552.606a
Cext_78 n_45 n_46 12.5033a
Cext_79 n_45 nbias 0.410221a
Cext_80 n_45 vdd 37.2442a
Cext_81 n_45 vss 3.77709a
Cext_82 n_45 VSUBS 374.17a
Cext_83 n_46 nbias 16.2438a
Cext_84 n_46 vdd 1.09071a
Cext_85 n_46 VSUBS 365.519a
Cext_86 ea_n ea_o1 2.69333f
Cext_87 ea_n ea_out 167.878a
Cext_88 ea_n ea_tail 2.71864f
Cext_89 ea_n fb 1.31734f
Cext_90 ea_n gate 24.4523a
Cext_91 ea_n nbias 40.1784a
Cext_92 ea_n pbias 46.3167a
Cext_93 ea_n vdd 192.516a
Cext_94 ea_n vref 409.055a
Cext_95 ea_n vss 1.00191f
Cext_96 ea_n x1 19.782a
Cext_97 ea_o1 ea_out 4.5887f
Cext_98 ea_o1 ea_tail 2.78437f
Cext_99 ea_o1 fb 4.66657f
Cext_100 ea_o1 gate 1.55696a
Cext_101 ea_o1 lp_brk 3.6131f
Cext_102 ea_o1 nbias 277.638a
Cext_103 ea_o1 pbias 45.7312a
Cext_104 ea_o1 vdd 163.843a
Cext_105 ea_o1 vref 835.631a
Cext_106 ea_o1 vss 3.3918f
Cext_107 ea_out ea_tail 2.3638f
Cext_108 ea_out fb 116.829a
Cext_109 ea_out gate 29.0137a
Cext_110 ea_out nbias 1.00289f
Cext_111 ea_out pbias 379.783a
Cext_112 ea_out vdd 479.553a
Cext_113 ea_out vout 383.084a
Cext_114 ea_out vref 47.0256a
Cext_115 ea_out vss 466.812a
Cext_116 ea_out x1 576.273a
Cext_117 ea_out y 90.7062a
Cext_118 ea_tail fb 671.681a
Cext_119 ea_tail gate 143.036a
Cext_120 ea_tail nbias 2.39629f
Cext_121 ea_tail pbias 755.553a
Cext_122 ea_tail vdd 724.222a
Cext_123 ea_tail vref 980.752a
Cext_124 ea_tail vss 0.893003a
Cext_125 ea_tail x1 27.1822a
Cext_126 fb gate 23.7407a
Cext_127 fb lp_brk 2.4941f
Cext_128 fb nbias 83.2052a
Cext_129 fb pbias 55.8325a
Cext_130 fb vdd 373.125a
Cext_131 fb vref 372.768a
Cext_132 fb vss 1.95363f
Cext_133 fb x1 12.9794a
Cext_134 gate nbias 931.357a
Cext_135 gate pbias 99.2403a
Cext_136 gate vdd 6.01239f
Cext_137 gate vout 10.9336f
Cext_138 gate vref 5.21313a
Cext_139 gate vss 341.92a
Cext_140 gate x1 128.56a
Cext_141 gate y 666.539a
Cext_142 lp_brk vss 179.073a
Cext_143 nbias pbias 7.13912f
Cext_144 nbias vdd 313.138a
Cext_145 nbias vout 26.0896a
Cext_146 nbias vref 45.0607a
Cext_147 nbias vss 1.37656f
Cext_148 nbias x1 80.6036a
Cext_149 nbias y 30.1141a
Cext_150 pbias vdd 2.01631f
Cext_151 pbias vout 177.124a
Cext_152 pbias vref 51.663a
Cext_153 pbias vss 231.932a
Cext_154 pbias x1 1.03929f
Cext_155 pbias y 463.191a
Cext_156 vdd vout 24.1852f
Cext_157 vdd vref 181.211a
Cext_158 vdd vss 3.89043f
Cext_159 vdd x1 209.882a
Cext_160 vdd y 1.2728f
Cext_161 vout vss 5.98506f
Cext_162 vout x1 1.61853f
Cext_163 vout y 1.21217f
Cext_164 vref vss 2.32628a
Cext_165 vss x1 951.231a
Cext_166 vss y 396.103a
Cext_167 VSUBS ea_n 9.08773f
Cext_168 VSUBS ea_o1 41.6541f
Cext_169 VSUBS ea_out 15.7489f
Cext_170 VSUBS ea_tail 5.86756f
Cext_171 VSUBS fb 21.7316f
Cext_172 VSUBS gate 28.1542f
Cext_173 VSUBS lp_brk 11.7268f
Cext_174 VSUBS nbias 17.6896f
Cext_175 VSUBS pbias 13.3328f
Cext_176 VSUBS vdd 119.091f
Cext_177 VSUBS vout 38.1453f
Cext_178 VSUBS vref 2.99077f
Cext_179 VSUBS vss 255.771f
Cext_180 VSUBS x1 5.64915f
Cext_181 VSUBS y 6.39702f
Cext_182 x1 y 967.658a
.ENDS ldo_ihp_capless
