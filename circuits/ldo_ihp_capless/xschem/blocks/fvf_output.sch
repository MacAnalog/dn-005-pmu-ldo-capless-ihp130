v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {fvf_output} -380 -200 0 0 0.4 0.4 {}
C {sg13g2_pr/sg13_lv_pmos.sym} 0 260 0 0 {name=MC model=sg13_lv_pmos spiceprefix=X w=x_dut_xmc_w l=x_dut_xmc_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 0 520 0 0 {name=MA model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
C {sg13g2_pr/sg13_lv_nmos.sym} -340 260 0 1 {name=MB model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
C {sg13g2_pr/sg13_lv_pmos.sym} -340 0 0 1 {name=MCP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcp_w l=x_dut_xmcp_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 340 0 0 0 {name=MD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcp_w l=x_dut_xmcp_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 340 260 0 0 {name=MS model=sg13_lv_nmos spiceprefix=X w=x_dut_xms_w l=x_dut_xms_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 0 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 660 {}
N -320 0 -320 70 {}
N -20 450 -20 520 {}
N 20 -140 20 -30 {}
N 20 30 20 90 {}
N 20 170 20 230 {}
N 20 290 20 490 {}
N 20 550 20 660 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 80 520 80 614 {}
N 290 0 290 60 {}
N 360 -140 360 -30 {}
N 360 30 360 230 {}
N 360 290 360 660 {}
N 420 0 420 94 {}
N 420 260 420 354 {}
N -555 -140 555 -140 {}
N -420 0 -360 0 {}
N -320 0 -260 0 {}
N -80 0 -20 0 {}
N 20 0 80 0 {}
N 260 0 320 0 {}
N 360 0 420 0 {}
N -360 70 -320 70 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N -80 260 -20 260 {}
N 20 260 80 260 {}
N 260 260 320 260 {}
N 360 260 420 260 {}
N -20 450 20 450 {}
N 20 520 80 520 {}
N -555 660 555 660 {}
C {devices/lab_wire.sym} -555 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -555 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -80 260 0 0 {name=l2 lab=ea_out}
C {devices/lab_wire.sym} -80 0 0 0 {name=l3 lab=gate}
C {devices/lab_wire.sym} 360 90 2 0 {name=l4 lab=gate}
C {devices/lab_wire.sym} 260 260 0 0 {name=l5 lab=nbias}
C {devices/lab_wire.sym} 20 90 2 0 {name=l6 lab=vout}
C {devices/lab_wire.sym} 20 170 0 1 {name=l7 lab=vout}
C {devices/lab_wire.sym} -260 260 0 1 {name=l8 lab=x1}
C {devices/lab_wire.sym} 20 350 2 0 {name=l9 lab=x1}
C {devices/lab_wire.sym} -260 0 0 1 {name=l10 lab=y}
C {devices/lab_wire.sym} 260 0 0 0 {name=l11 lab=y}
C {devices/lab_wire.sym} 80 354 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 80 614 2 0 {name=l16 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l17 lab=vss}
C {devices/lab_wire.sym} 420 354 2 0 {name=l18 lab=vss}
C {devices/ipin.sym} -695 260 0 0 {name=p0 lab=ea_out}
C {devices/ipin.sym} -695 380 0 0 {name=p1 lab=nbias}
C {devices/iopin.sym} -360 800 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -240 800 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 695 30 0 0 {name=p4 lab=vout}
