v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {bias_ref} -210 -200 0 0 0.4 0.4 {}
C {sg13g2_pr/rhigh.sym} -10 260 0 0 {name=RB model=rhigh spiceprefix=X body=vss w=r_w l=r_bias_l}
C {sg13g2_pr/sg13_lv_nmos.sym} -170 260 0 1 {name=MB0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 170 260 0 0 {name=MB1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb1_w l=x_dut_xmb0_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 170 0 0 0 {name=MBP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmbp_w l=x_dut_xmbp_l}
N -250 260 -250 354 {}
N -190 170 -190 230 {}
N -190 290 -190 400 {}
N -150 190 -150 260 {}
N -10 200 -10 230 {}
N -10 290 -10 350 {}
N 120 200 120 260 {}
N 150 0 150 70 {}
N 190 -140 190 -30 {}
N 190 30 190 230 {}
N 190 290 190 400 {}
N 250 0 250 94 {}
N 250 260 250 354 {}
N -385 -140 385 -140 {}
N 90 0 150 0 {}
N 190 0 250 0 {}
N 150 70 190 70 {}
N -190 190 -150 190 {}
N -190 200 120 200 {}
N -250 260 -190 260 {}
N 120 260 150 260 {}
N 190 260 250 260 {}
N -385 400 385 400 {}
C {devices/lab_wire.sym} -385 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -385 400 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -190 170 0 1 {name=l2 lab=nbias}
C {devices/lab_wire.sym} 90 0 0 0 {name=l3 lab=pbias}
C {devices/lab_wire.sym} 250 94 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} -250 354 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} 250 354 2 0 {name=l6 lab=vss}
C {devices/lab_wire.sym} -10 350 2 0 {name=l7 lab=vdd}
C {devices/iopin.sym} -190 540 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} 190 540 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 525 0 0 0 {name=p2 lab=pbias}
C {devices/opin.sym} 525 230 0 0 {name=p3 lab=nbias}
