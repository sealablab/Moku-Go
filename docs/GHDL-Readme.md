# Simulating `delay_b.vhd` with GHDL

This guide walks through compiling, elaborating, and running a simulation of the `delay_b` delay-box module using [GHDL](https://ghdl.github.io/ghdl/).

## 📁 File Structure

```
Delays/
├── delay_b.vhd         # Your DUT (Device Under Test)
└── tb_delay_b.vhd      # A testbench that drives `clk`, `reset`, `controlX`, and `trig_in`
```

## 🧰 Prerequisites

Make sure `ghdl` is installed. If not:

```bash
sudo apt install ghdl               # Debian/Ubuntu
brew install ghdl                  # macOS
```

## 🚦 Step-by-Step Simulation

### 1. Analyze the source files

```bash
ghdl -a delay_b.vhd tb_delay_b.vhd
```

### 2. Elaborate the testbench

```bash
ghdl -e tb_delay_b
```

### 3. Run the simulation

```bash
ghdl -r tb_delay_b --vcd=wave.vcd
```

This will output a `wave.vcd` file that you can inspect using GTKWave:

```bash
gtkwave wave.vcd
```

## 🧪 Example Testbench Behavior

Your testbench should:
- Apply a `reset` pulse at the start.
- Set `control0` to enable the delay box (bit 31 = `0`).
- Set `control1` to a known delay value (e.g. 10 clock cycles).
- Pulse `trig_in` to start the countdown.
- Check that `fired` and `trig_out` respond correctly after N cycles.

## ✅ Tips

- Use short delays (5–20 cycles) for easier simulation.
- Use `report` statements in the testbench for GHDL terminal output.
- Remember: `fired` stays high until reset, `trig_out` is one-cycle pulse.

---

Happy simulating! 🚀