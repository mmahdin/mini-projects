module SimpleALU (
    input [1:0] x,        // 2-bit input x (was 'a')
    input [1:0] y,        // 2-bit input y (was 'b')
    input en,             // enable signal (was 'enable')
    input [1:0] sel,      // 2-bit select signal (was 's')
    output reg [3:0] out  // 4-bit output (was 'result')
);

always @(*) begin
    if (en) begin
        case (sel)
            2'b00: out = x + y;                      // sel=00: x + y
            2'b01: out = x - y;                      // sel=01: x - y
            2'b10: out = x * y;                      // sel=10: x * y
            2'b11: out = (x[0] * y[0]) + (x[1] * y[1]); // sel=11: x0*y0 + x1*y1
            default: out = 4'b0000;                  // default case
        endcase
    end else begin
        out = 4'b0000;  // output zero when enable is low
    end
end

endmodule