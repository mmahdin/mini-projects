module arithmetic_unit_tb;

reg [1:0] a_tb, b_tb;
reg enable_tb;
reg [1:0] s_tb;
wire [1:0] result_tb;

arithmetic_unit dut (
    .a(a_tb),
    .b(b_tb),
    .enable(enable_tb),
    .s(s_tb),
    .result(result_tb)
);

initial begin
    $monitor("Time=%0t: a=%b, b=%b, enable=%b, s=%b, result=%b", $time, a_tb, b_tb, enable_tb, s_tb, result_tb);

    // Test 1: addition (s=00)
    a_tb = 2'b10; b_tb = 2'b01; enable_tb = 1'b1; s_tb = 2'b00;
    #10;

    // Test 2: subtraction (s=01)
    a_tb = 2'b10; b_tb = 2'b01; enable_tb = 1'b1; s_tb = 2'b01;
    #10;

    // Test 3: multiplication (s=10)
    a_tb = 2'b10; b_tb = 2'b01; enable_tb = 1'b1; s_tb = 2'b10;
    #10;

    // Test 4: bitwise AND (s=11)
    a_tb = 2'b10; b_tb = 2'b01; enable_tb = 1'b1; s_tb = 2'b11;
    #10;

    // Test 5: disable operation
    enable_tb = 1'b0;
    #10;

    $finish;
end

endmodule
