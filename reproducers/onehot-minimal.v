// Independent reduction of the CoherenceManager mismatch; no PDK required.
module onehot_minimal(input select, output mismatch);
  wire [1:0] value = select ? 2'b01 : 2'b10;
  assign mismatch = (value == 2'b11);
endmodule
