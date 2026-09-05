v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_ihp_capless} -550 -200 0 0 0.4 0.4 {}
C {devices/vsource.sym} -510 345 0 0 {name=VREF value="dc \{vref_val\}"}
C {devices/vsource.sym} -510 605 0 0 {name=VLP value="dc 0"}
C {sg13g2_pr/rhigh.sym} 435 435 0 0 {name=R1 model=rhigh spiceprefix=X body=vss w=r_w l=r_fb_l}
C {sg13g2_pr/cap_cmim.sym} 755 260 1 0 {name=CFF model=cap_cmim spiceprefix=X w=c_ff_w l=c_ff_w}
C {sg13g2_pr/rhigh.sym} 435 605 0 0 {name=R2 model=rhigh spiceprefix=X body=vss w=r_w l=r_fb_l}
C {sg13g2_pr/rhigh.sym} 850 435 0 0 {name=RB model=rhigh spiceprefix=X body=vss w=r_w l=r_bias_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 850 520 0 1 {name=MB0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 1190 260 0 0 {name=MB1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb1_w l=x_dut_xmb0_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 1190 0 0 0 {name=MBP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmbp_w l=x_dut_xmbp_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 0 0 0 1 {name=MT model=sg13_lv_pmos spiceprefix=X w=x_dut_xmt_w l=x_dut_xmbp_l}
C {sg13g2_pr/sg13_lv_pmos.sym} -170 260 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 170 260 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {sg13g2_pr/sg13_lv_nmos.sym} -170 520 0 1 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 170 520 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 510 260 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 510 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xmbp_l}
C {sg13g2_pr/cap_cmim.sym} 510 390 0 0 {name=CC model=cap_cmim spiceprefix=X w=c_comp_w l=c_comp_w}
C {sg13g2_pr/sg13_lv_pmos.sym} 2210 260 0 0 {name=MC model=sg13_lv_pmos spiceprefix=X w=x_dut_xmc_w l=x_dut_xmc_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 2210 520 0 0 {name=MA model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 1870 260 0 0 {name=MB model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 1870 0 0 0 {name=MCP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcp_w l=x_dut_xmcp_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 1530 0 0 0 {name=MD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcp_w l=x_dut_xmcp_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 1530 260 0 0 {name=MS model=sg13_lv_nmos spiceprefix=X w=x_dut_xms_w l=x_dut_xms_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 2210 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
C {sg13g2_pr/cap_cmim.sym} 2390 520 0 0 {name=COUT model=cap_cmim spiceprefix=X w=c_out_w l=c_out_w m=c_out_m}
N -510 255 -510 315 {}
N -510 375 -510 435 {}
N -510 515 -510 575 {}
N -510 635 -510 695 {}
N -250 260 -250 354 {}
N -250 520 -250 614 {}
N -190 200 -190 230 {}
N -190 290 -190 490 {}
N -190 550 -190 745 {}
N -150 450 -150 520 {}
N -80 0 -80 94 {}
N -20 -140 -20 -30 {}
N -20 30 -20 200 {}
N 120 460 120 520 {}
N 190 200 190 230 {}
N 190 290 190 490 {}
N 190 550 190 745 {}
N 250 260 250 354 {}
N 250 520 250 614 {}
N 430 0 430 94 {}
N 435 260 435 405 {}
N 435 465 435 495 {}
N 435 515 435 575 {}
N 435 635 435 695 {}
N 490 -140 490 -30 {}
N 490 30 490 230 {}
N 490 290 490 745 {}
N 510 200 510 360 {}
N 510 420 510 460 {}
N 560 260 560 450 {}
N 770 520 770 614 {}
N 785 260 785 320 {}
N 815 260 815 495 {}
N 830 450 830 490 {}
N 830 550 830 745 {}
N 850 375 850 460 {}
N 870 450 870 520 {}
N 1140 260 1140 375 {}
N 1170 0 1170 70 {}
N 1210 -140 1210 -30 {}
N 1210 30 1210 230 {}
N 1210 290 1210 745 {}
N 1270 0 1270 94 {}
N 1270 260 1270 354 {}
N 1550 -140 1550 -30 {}
N 1550 30 1550 230 {}
N 1550 290 1550 745 {}
N 1610 0 1610 94 {}
N 1610 260 1610 354 {}
N 1850 0 1850 70 {}
N 1890 -140 1890 -30 {}
N 1890 30 1890 70 {}
N 1890 170 1890 230 {}
N 1890 290 1890 745 {}
N 1950 0 1950 94 {}
N 1950 260 1950 354 {}
N 2160 0 2160 60 {}
N 2160 260 2160 330 {}
N 2190 450 2190 520 {}
N 2230 -140 2230 -30 {}
N 2230 30 2230 230 {}
N 2230 290 2230 490 {}
N 2230 550 2230 745 {}
N 2290 0 2290 94 {}
N 2290 260 2290 354 {}
N 2290 520 2290 614 {}
N 2390 200 2390 490 {}
N 2390 550 2390 745 {}
N -570 -140 2560 -140 {}
N -80 0 -20 0 {}
N 20 0 80 0 {}
N 430 0 490 0 {}
N 530 0 590 0 {}
N 1110 0 1170 0 {}
N 1210 0 1270 0 {}
N 1450 0 1510 0 {}
N 1550 0 1610 0 {}
N 1790 0 1850 0 {}
N 1890 0 1950 0 {}
N 2130 0 2190 0 {}
N 2230 0 2290 0 {}
N 1170 70 1210 70 {}
N 1850 70 1890 70 {}
N -190 200 190 200 {}
N 490 200 510 200 {}
N 2230 200 2390 200 {}
N -250 260 -190 260 {}
N -150 260 -90 260 {}
N 90 260 150 260 {}
N 190 260 250 260 {}
N 530 260 590 260 {}
N 665 260 725 260 {}
N 785 260 815 260 {}
N 1110 260 1170 260 {}
N 1210 260 1270 260 {}
N 1450 260 1510 260 {}
N 1550 260 1610 260 {}
N 1790 260 1850 260 {}
N 1890 260 1950 260 {}
N 2160 260 2190 260 {}
N 2230 260 2290 260 {}
N 510 330 2160 330 {}
N 850 375 1140 375 {}
N 375 405 435 405 {}
N -190 450 -150 450 {}
N 510 450 560 450 {}
N 830 450 870 450 {}
N 2190 450 2230 450 {}
N -190 460 120 460 {}
N 190 460 510 460 {}
N 830 460 850 460 {}
N 790 465 850 465 {}
N 435 495 815 495 {}
N -250 520 -190 520 {}
N 120 520 150 520 {}
N 190 520 250 520 {}
N 770 520 830 520 {}
N 2230 520 2290 520 {}
N -570 745 2560 745 {}
C {devices/lab_wire.sym} -570 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -570 745 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -190 350 2 0 {name=l2 lab=ea_n}
C {devices/lab_wire.sym} 590 260 0 1 {name=l3 lab=ea_o1}
C {devices/lab_wire.sym} 490 90 2 0 {name=l4 lab=ea_out}
C {devices/lab_wire.sym} -20 90 2 0 {name=l5 lab=ea_tail}
C {devices/lab_wire.sym} -90 260 0 1 {name=l6 lab=fb}
C {devices/lab_wire.sym} 375 405 0 0 {name=l7 lab=fb}
C {devices/lab_wire.sym} 435 695 2 0 {name=l8 lab=fb}
C {devices/lab_wire.sym} 665 260 0 0 {name=l9 lab=fb}
C {devices/lab_wire.sym} 1550 90 2 0 {name=l10 lab=gate}
C {devices/lab_wire.sym} 2130 0 0 0 {name=l11 lab=gate}
C {devices/lab_wire.sym} 785 320 2 0 {name=l12 lab=lp_brk}
C {devices/lab_wire.sym} 1110 260 0 0 {name=l13 lab=nbias}
C {devices/lab_wire.sym} 1450 260 0 0 {name=l14 lab=nbias}
C {devices/lab_wire.sym} 80 0 0 1 {name=l15 lab=pbias}
C {devices/lab_wire.sym} 590 0 0 1 {name=l16 lab=pbias}
C {devices/lab_wire.sym} 1110 0 0 0 {name=l17 lab=pbias}
C {devices/lab_wire.sym} 2230 90 2 0 {name=l18 lab=vout}
C {devices/lab_wire.sym} 90 260 0 0 {name=l19 lab=vref}
C {devices/lab_wire.sym} 1790 260 0 0 {name=l20 lab=x1}
C {devices/lab_wire.sym} 2230 350 2 0 {name=l21 lab=x1}
C {devices/lab_wire.sym} 1450 0 0 0 {name=l22 lab=y}
C {devices/lab_wire.sym} 1790 0 0 0 {name=l23 lab=y}
C {devices/lab_wire.sym} 1890 170 0 1 {name=l24 lab=y}
C {devices/lab_wire.sym} 1270 94 2 0 {name=l25 lab=vdd}
C {devices/lab_wire.sym} -80 94 2 0 {name=l26 lab=vdd}
C {devices/lab_wire.sym} -250 354 2 0 {name=l27 lab=vdd}
C {devices/lab_wire.sym} 250 354 2 0 {name=l28 lab=vdd}
C {devices/lab_wire.sym} 430 94 2 0 {name=l29 lab=vdd}
C {devices/lab_wire.sym} 2290 354 2 0 {name=l30 lab=vdd}
C {devices/lab_wire.sym} 1950 94 2 0 {name=l31 lab=vdd}
C {devices/lab_wire.sym} 1610 94 2 0 {name=l32 lab=vdd}
C {devices/lab_wire.sym} 2290 94 2 0 {name=l33 lab=vdd}
C {devices/lab_wire.sym} 770 614 2 0 {name=l34 lab=vss}
C {devices/lab_wire.sym} 1270 354 2 0 {name=l35 lab=vss}
C {devices/lab_wire.sym} -250 614 2 0 {name=l36 lab=vss}
C {devices/lab_wire.sym} 250 614 2 0 {name=l37 lab=vss}
C {devices/lab_wire.sym} 490 260 0 0 {name=l38 lab=vss}
C {devices/lab_wire.sym} 2290 614 2 0 {name=l39 lab=vss}
C {devices/lab_wire.sym} 1950 354 2 0 {name=l40 lab=vss}
C {devices/lab_wire.sym} 1610 354 2 0 {name=l41 lab=vss}
C {devices/lab_wire.sym} -510 255 0 1 {name=l42 lab=vref}
C {devices/lab_wire.sym} -510 435 2 0 {name=l43 lab=vss}
C {devices/lab_wire.sym} -510 515 0 1 {name=l44 lab=lp_brk}
C {devices/lab_wire.sym} -510 695 2 0 {name=l45 lab=vout}
C {devices/lab_wire.sym} 790 465 0 0 {name=l46 lab=vdd}
C {devices/lab_wire.sym} 435 515 0 1 {name=l47 lab=vss}
C {devices/opin.sym} 2700 30 0 0 {name=p0 lab=vout}
