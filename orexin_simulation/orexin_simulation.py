import moose
import rdesigneur as rd
import numpy as np
import matplotlib.pyplot as plt

def run_simulation(freq, gbar):

    rdes = rd.rdesigneur(

        cellProto=[['somaProto', 'soma', 20e-6, 200e-6]],

        chanProto=[
            ['make_HH_Na()', 'Na'],
            ['make_HH_K()', 'K'],
            ['make_glu()', 'glu']
        ],

        chanDistrib=[
            ['Na', 'soma', 'Gbar', '1200'],
            ['K', 'soma', 'Gbar', '360'],
            ['glu', 'soma', 'Gbar', str(gbar)]
        ],

        stimList=[
            ['soma', '0.5', 'glu', 'periodicsyn', str(freq)]
        ],

        plotList=[
            ['soma', '1', '.', 'Vm', 'Soma membrane potential']
        ]
    )

    rdes.buildModel()
    moose.reinit()
    moose.start(0.3)

    vm = moose.wildcardFind('/##[TYPE=Table]')[0].vector.copy()

    if moose.exists('/model'):
        moose.delete('/model')

    return vm

conditions = {
    "Control":      {"freq": 50, "gbar": 1.0},
    "Apigenin":     {"freq": 35, "gbar": 0.9},
    "Hesperidin":   {"freq": 20, "gbar": 0.7},
    "Lemborexant":  {"freq": 5, "gbar": 0.4}
}

plt.figure(figsize=(10,5))

for label, params in conditions.items():
    vm = run_simulation(params["freq"], params["gbar"])

    # Spike count (threshold = 0 mV)
    spikes = np.sum((vm[:-1] < 0) & (vm[1:] >= 0))

    print(f"{label}")
    print(f"Frequency: {params['freq']} Hz")
    print(f"Spike count: {spikes}")
    print(f"Peak Vm: {np.max(vm):.4f} V")
    print(f"Mean Vm: {np.mean(vm):.4f} V")
    print()

    time = np.linspace(0, 0.3, len(vm))

    plt.plot(time, vm, label=label)

plt.xlabel("Time (s)")
plt.ylabel("Membrane Potential (V)")
plt.title("Effect of Qualitative OX2R Modulation on Neuronal Activity")
plt.legend()
plt.grid(True)
plt.show()