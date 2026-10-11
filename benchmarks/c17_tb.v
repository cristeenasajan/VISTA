`timescale 1ns/1ps

module c17_tb;

    reg N1;
    reg N2;
    reg N3;
    reg N6;
    reg N7;

    wire N22;
    wire N23;

    c17 dut (
        .N1(N1),
        .N2(N2),
        .N3(N3),
        .N6(N6),
        .N7(N7),
        .N22(N22),
        .N23(N23)
    );

    integer i;

    initial begin

        for (i = 0; i < 32; i = i + 1) begin

            {N1, N2, N3, N6, N7} = i;

            #10;

            $display(
                "INPUT=%05b OUTPUT=%02b",
                {N1, N2, N3, N6, N7},
                {N22, N23}
            );

        end

        $finish;

    end

endmodule