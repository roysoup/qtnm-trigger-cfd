// Copyright 1986-2016 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2016.3 (win64) Build 1682563 Mon Oct 10 19:07:27 MDT 2016
// Date        : Wed Aug 09 14:27:31 2023
// Host        : XPS-13-9310 running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode funcsim
//               C:/Users/roysi/Files/URSS/Verilog/Practice/Practice.srcs/sources_1/bd/design_1/ip/design_1_zero_detector_0_0/design_1_zero_detector_0_0_sim_netlist.v
// Design      : design_1_zero_detector_0_0
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7z010clg400-1
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "design_1_zero_detector_0_0,zero_detector,{}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) (* X_CORE_INFO = "zero_detector,Vivado 2016.3" *) 
(* NotValidForBitStream *)
module design_1_zero_detector_0_0
   (clk,
    x,
    y,
    sign,
    last_sign);
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 clk CLK" *) input clk;
  input [7:0]x;
  output [0:0]y;
  output [0:0]sign;
  output [0:0]last_sign;

  wire clk;
  wire [0:0]last_sign;
  wire [0:0]sign;
  wire [7:0]x;
  wire [0:0]y;

  design_1_zero_detector_0_0_zero_detector inst
       (.clk(clk),
        .last_sign(last_sign),
        .sign(sign),
        .x(x[7]),
        .y(y));
endmodule

(* ORIG_REF_NAME = "zero_detector" *) 
module design_1_zero_detector_0_0_zero_detector
   (sign,
    last_sign,
    y,
    x,
    clk);
  output [0:0]sign;
  output [0:0]last_sign;
  output [0:0]y;
  input [0:0]x;
  input clk;

  wire clk;
  wire [0:0]last_sign;
  wire [0:0]sign;
  wire [0:0]x;
  wire [0:0]y;

  FDRE #(
    .INIT(1'b0)) 
    \last_sign_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .D(sign),
        .Q(last_sign),
        .R(1'b0));
  FDRE \sign_reg[0] 
       (.C(clk),
        .CE(1'b1),
        .D(x),
        .Q(sign),
        .R(1'b0));
  LUT2 #(
    .INIT(4'h6)) 
    \y[0]_INST_0 
       (.I0(sign),
        .I1(last_sign),
        .O(y));
endmodule
`ifndef GLBL
`define GLBL
`timescale  1 ps / 1 ps

module glbl ();

    parameter ROC_WIDTH = 100000;
    parameter TOC_WIDTH = 0;

//--------   STARTUP Globals --------------
    wire GSR;
    wire GTS;
    wire GWE;
    wire PRLD;
    tri1 p_up_tmp;
    tri (weak1, strong0) PLL_LOCKG = p_up_tmp;

    wire PROGB_GLBL;
    wire CCLKO_GLBL;
    wire FCSBO_GLBL;
    wire [3:0] DO_GLBL;
    wire [3:0] DI_GLBL;
   
    reg GSR_int;
    reg GTS_int;
    reg PRLD_int;

//--------   JTAG Globals --------------
    wire JTAG_TDO_GLBL;
    wire JTAG_TCK_GLBL;
    wire JTAG_TDI_GLBL;
    wire JTAG_TMS_GLBL;
    wire JTAG_TRST_GLBL;

    reg JTAG_CAPTURE_GLBL;
    reg JTAG_RESET_GLBL;
    reg JTAG_SHIFT_GLBL;
    reg JTAG_UPDATE_GLBL;
    reg JTAG_RUNTEST_GLBL;

    reg JTAG_SEL1_GLBL = 0;
    reg JTAG_SEL2_GLBL = 0 ;
    reg JTAG_SEL3_GLBL = 0;
    reg JTAG_SEL4_GLBL = 0;

    reg JTAG_USER_TDO1_GLBL = 1'bz;
    reg JTAG_USER_TDO2_GLBL = 1'bz;
    reg JTAG_USER_TDO3_GLBL = 1'bz;
    reg JTAG_USER_TDO4_GLBL = 1'bz;

    assign (weak1, weak0) GSR = GSR_int;
    assign (weak1, weak0) GTS = GTS_int;
    assign (weak1, weak0) PRLD = PRLD_int;

    initial begin
	GSR_int = 1'b1;
	PRLD_int = 1'b1;
	#(ROC_WIDTH)
	GSR_int = 1'b0;
	PRLD_int = 1'b0;
    end

    initial begin
	GTS_int = 1'b1;
	#(TOC_WIDTH)
	GTS_int = 1'b0;
    end

endmodule
`endif
