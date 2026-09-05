v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {fb_divider} -40 -200 0 0 0.4 0.4 {}
C {sg13g2_pr/rhigh.sym} 240 0 0 0 {name=R1 model=rhigh spiceprefix=X body=vss w=r_w l=r_fb_l}
C {sg13g2_pr/rhigh.sym} 0 240 0 0 {name=R2 model=rhigh spiceprefix=X body=vss w=r_w l=r_fb_l}
C {sg13g2_pr/cap_cmim.sym} 0 0 0 0 {name=CFF model=cap_cmim spiceprefix=X w=c_ff_w l=c_ff_w}
N 0 -90 0 -30 {}
N 0 30 0 90 {}
N 0 150 0 210 {}
N 0 270 0 330 {}
N 240 -90 240 -30 {}
N 240 30 240 90 {}
N -60 380 410 380 {}
C {devices/lab_wire.sym} -60 380 0 0 {name=l0 lab=vss}
C {devices/lab_wire.sym} 0 90 2 0 {name=l1 lab=fb}
C {devices/lab_wire.sym} 0 330 2 0 {name=l2 lab=fb}
C {devices/lab_wire.sym} 240 -90 0 1 {name=l3 lab=fb}
C {devices/lab_wire.sym} 0 -90 0 1 {name=l4 lab=lp_brk}
C {devices/lab_wire.sym} 240 90 2 0 {name=l5 lab=lp_brk}
C {devices/lab_wire.sym} 0 150 0 1 {name=l6 lab=vss}
C {devices/iopin.sym} 0 520 0 0 {name=p0 lab=lp_brk}
C {devices/iopin.sym} 120 520 0 0 {name=p1 lab=fb}
C {devices/iopin.sym} 240 520 0 0 {name=p2 lab=vss}
