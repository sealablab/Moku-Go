---
aliases:
  - EM-FI Transient Probe
tags:
  - RISCURE
  - PROBE
  - EM
  - FI
---

# Riscure [DS1120A (EM FI Trans Probe)](https://www.keysight.com/us/en/product/DS1120A/unidirectional-fault-injection-probe.html)
The original Riscure chipshouter.
[[imgs/Riscure-DS1120A EM FI Transient probe.png]]


The DS1120A (EM Fi Trans Probe) is designed to fire when its digital_glitch input rises above 2.4v. The **intensity** of the output is a __linear function__ of the (poorly named) `pulse amplitude` input. (More on these below)
## dig_glitch (trig_in)
the **dig_glitch** (aka `trig_in`) port is a **50-ohm** __SMB__ connector.
The EM FI Trans probe has a **threshold** of `2.4v

## ~~pulse amplitude~~ (intensity)

the **pulse_amplitude** (aka `intensity`) port is a **50-ohm** __SMB__ connector. This analog input controls the **intensity** of the output at the probe tip. 

> [!NOTE] The **EM FI Trans Probe** has a **MAXIMUM** input rating of 3v3 

## coil current (monitor)

The DS1120a (EM FI Transient probe) has an __optional__ output for monitoring its performance. It is **highly reccomended** to monitor this to verify the probe is in fact, firing.

``` vhdl
entity DS1120A
(
	in: trig_in  -- STATIC: 2v5 threshold
	in: intensity_in -- from 0 - 3v3
	out: curr_mon -- (from ??? - ???)
)
```

![[Riscure-DS1120A EM FI Probe Sketch]]


# Probe tips
The DS1120 is designed to function with the following different tips.
* [[Tips/Riscure EM FI Classic Probe tips|Riscure EM FI Classic Probe tips]]
* [[Tips/Riscure EM FI Crescent Probe tips|Riscure EM FI Crescent Probe tips]]
* [[Tips/Riscure-DS1320A Body Bias Injection Probe Needles|Riscure-DS1320A Body Bias Injection Probe Needles]]

## Moku Fi-Py support
You can find a simple VHDL driver for this probe at [Here]()
#JCRET2HERE 2025-05-18

# See Also
## [[Riscure-DS1121A Bi-Directional EM FI Probe]]
 
