v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ea_stage1} -210 -200 0 0 0.4 0.4 {}
C {sg13g2_pr/sg13_lv_pmos.sym} 0 0 0 0 {name=MT model=sg13_lv_pmos spiceprefix=X w=x_dut_xmt_w l=x_dut_xmbp_l}
C {sg13g2_pr/sg13_lv_pmos.sym} -170 260 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 170 260 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {sg13g2_pr/sg13_lv_nmos.sym} -170 520 0 1 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 170 520 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
N -250 260 -250 354 {}
N -250 520 -250 614 {}
N -190 200 -190 230 {}
N -190 290 -190 490 {}
N -190 550 -190 660 {}
N -150 450 -150 520 {}
N 20 -140 20 -30 {}
N 20 30 20 200 {}
N 80 0 80 94 {}
N 120 460 120 520 {}
N 190 200 190 230 {}
N 190 290 190 490 {}
N 190 550 190 660 {}
N 250 260 250 354 {}
N 250 520 250 614 {}
N -380 -140 380 -140 {}
N -80 0 -20 0 {}
N 20 0 80 0 {}
N -190 200 190 200 {}
N -250 260 -190 260 {}
N -150 260 -90 260 {}
N 90 260 150 260 {}
N 190 260 250 260 {}
N -190 450 -150 450 {}
N -190 460 120 460 {}
N -250 520 -190 520 {}
N 120 520 150 520 {}
N 190 520 250 520 {}
N -380 660 380 660 {}
C {devices/lab_wire.sym} -380 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -380 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -190 350 2 0 {name=l2 lab=ea_n}
C {devices/lab_wire.sym} 190 350 2 0 {name=l3 lab=ea_o1}
C {devices/lab_wire.sym} 20 90 2 0 {name=l4 lab=ea_tail}
C {devices/lab_wire.sym} -90 260 0 1 {name=l5 lab=fb}
C {devices/lab_wire.sym} -80 0 0 0 {name=l6 lab=pbias}
C {devices/lab_wire.sym} 90 260 0 0 {name=l7 lab=vref}
C {devices/lab_wire.sym} 80 94 2 0 {name=l8 lab=vdd}
C {devices/lab_wire.sym} -250 354 2 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} 250 354 2 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} -250 614 2 0 {name=l11 lab=vss}
C {devices/lab_wire.sym} 250 614 2 0 {name=l12 lab=vss}
C {devices/ipin.sym} -520 0 0 0 {name=p0 lab=pbias}
C {devices/ipin.sym} -520 260 0 0 {name=p1 lab=fb}
C {devices/ipin.sym} -520 380 0 0 {name=p2 lab=vref}
C {devices/iopin.sym} -190 800 0 0 {name=p3 lab=vdd}
C {devices/iopin.sym} 20 800 0 0 {name=p4 lab=vss}
C {devices/opin.sym} 520 290 0 0 {name=p5 lab=ea_o1}
