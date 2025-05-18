# Magic Testbench Strings (`::TAG::`) for VHDL Simulation

These standardized `report` strings are designed to be:

- Easily greppable in logs and test output
- Machine-parseable with or without regex
- Unambiguous and consistent across testbenches

## ✅ Format Convention

Each string follows the format:

```
::CATEGORY::DETAILS
```

## 📘 Standard Tags

| String                          | Purpose                                      |
|---------------------------------|----------------------------------------------|
| `::TESTCASE::name`              | Start of a named test case                   |
| `::CHECKPOINT::label`           | Marks a milestone or phase in simulation     |
| `::PASS::ALL_TESTS`             | Indicates all checks passed successfully     |
| `::FAIL::ASSERTION`             | Assertion failure triggered                  |
| `::FAIL::UNEXPECTED_BEHAVIOR`   | Manual failure report (e.g., unexpected value)|
| `::DONE::SIMULATION_DONE`       | End of simulation marker                     |

## 🧪 Example Usage in VHDL

```vhdl
report "::TESTCASE::basic_trigger_delay";

assert trig_out = '1'
  report "::FAIL::ASSERTION: trig_out not high after delay" severity error;

report "::PASS::ALL_TESTS";
report "::DONE::SIMULATION_DONE";
```

## 🧰 Grep-Friendly Examples

```sh
grep '^::' simulation.log            # Show all machine-readable markers
grep '::FAIL::' simulation.log       # Show only failure points
grep '::PASS::ALL_TESTS' simulation.log && echo OK
```

## 🧼 Notes

- Use `::DONE::SIMULATION_DONE` at the very end of each testbench.
- Use `::PASS::ALL_TESTS` only if all checks passed.
- Keep everything case-sensitive and colon-delimited.
