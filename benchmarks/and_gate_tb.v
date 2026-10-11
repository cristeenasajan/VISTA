`timescale 1ns/1ps

module and_gate_tb;

    reg A;
    reg B;
    wire Y;

    and_gate dut (
        .A(A),
        .B(B),
        .Y(Y)
    );

    initial begin

        A = 0; B = 0;
        #10;
        $display("A=%b B=%b Y=%b", A, B, Y);

        A = 0; B = 1;
        #10;
        $display("A=%b B=%b Y=%b", A, B, Y);

        A = 1; B = 0;
        #10;
        $display("A=%b B=%b Y=%b", A, B, Y);

        A = 1; B = 1;
        #10;
        $display("A=%b B=%b Y=%b", A, B, Y);

        $finish;

    end

endmodule